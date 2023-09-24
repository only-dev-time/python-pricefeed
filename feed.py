#!/usr/bin/env python3
import datetime
import json
import logging
import os
import sys
import time

import requests
from steem import Steem

# -------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------
CONFIG_FILE = "./config.json"
LOG_FILE = "./pricefeed.log"


# -------------------------------------------------------------------
# Blockchain Functions
# -------------------------------------------------------------------
def publish_feed(steem_client: Steem, account: str, max_retry: int, retry_interval: int, price: float, peg_multi):
    retries = 0
    while retries < max_retry:
        try:
            exchange_rate = {"base": round(price, 3), "quote": round(1 / peg_multi, 3)}

            log_info(f"Broadcasting feed_publish transaction: {exchange_rate}")

            steem_client.witness_feed_publish(exchange_rate["base"], exchange_rate["quote"], account)

            log_info("Broadcast successful!")
            break

        except Exception as err:
            err_msg = err.args[0] if len(err.args) else err.__class__.__name__
            log_error("Error broadcasting feed_publish transaction: " + err_msg)
            retries += 1
            time.sleep(retry_interval)


# -------------------------------------------------------------------
# Read Config Functions
# -------------------------------------------------------------------
def load_config():
    with open(CONFIG_FILE, encoding="UTF-8") as fp:
        logging.debug("config loaded")
        return json.load(fp)


def get_rpc_node(config: dict):
    rpc_nodes = config.get("rpc_nodes", [])
    return rpc_nodes if rpc_nodes else ["https://api.steemit.com"]


# if feed_steem_active_key is not set in config.json
# then look for it in environment variables
def get_active_key(config: dict):
    key = config.get("feed_steem_active_key", "")
    if key:
        return key
    return os.environ.get("FEED_STEEM_ACTIVE_KEY", "")


# if feed_steem_account is not set in config.json
# then look for it in environment variables
def get_account_name(config: dict):
    name = config.get("feed_steem_account", "")
    if name:
        return name
    return os.environ.get("FEED_STEEM_ACCOUNT", "")


# if coinmarketcap_api_key is not set in config.json
# then look for it in environment variables
def get_coinmarketcap_api_key(config: dict):
    key = config.get("coinmarketcap_api_key", "")
    if key:
        return key
    return os.environ.get("COINMARKETCAP_API_KEY", "")


def get_exchanges(config: dict):
    return config.get("exchanges", [])


def get_retry_interval(config: dict):
    return config.get("retry_interval", 10)


def get_max_retry(config: dict):
    return config.get("price_feed_max_retry", 5)


# fee_publish_interval is not necessary in python,
# because the process is waiting for response
def get_publish_interval(config: dict):
    return config.get("feed_publish_interval", 30)


def get_interval(config: dict):
    return config.get("interval", 120)


def get_peg_multi(config: dict):
    peg = config.get("peg_multi", 1)
    return peg if peg else 1


# -------------------------------------------------------------------
# Log Functions
# -------------------------------------------------------------------
def log_info(msg):
    logging.info(str(datetime.datetime.now()) + " - " + str(msg))


def log_error(msg):
    logging.error(str(datetime.datetime.now()) + " - " + str(msg))


# -------------------------------------------------------------------
# Load Functions
# -------------------------------------------------------------------
def load_price_cloudflare(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # load STEEM price
            response = requests.get("https://price.justyy.workers.dev/query/?s=STEEM+USDT")
            json_data = response.json()
            arr = json_data["result"][0].split(" ")
            steem_price = float(arr[3])
            log_info(f"Loaded STEEM Price from Cloudflare: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from Cloudflare: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_coingecko(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price in USD directly from CoinGecko
            response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=steem&vs_currencies=usd")
            json_data = response.json()
            steem_price = float(json_data["steem"]["usd"])
            log_info(f"Loaded STEEM Price from Coingecko: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from Coingecko: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_cryptocompare(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price in USD directly from CoinGecko
            response = requests.get("https://min-api.cryptocompare.com/data/price?fsym=STEEM&tsyms=USDT")
            json_data = response.json()
            steem_price = float(json_data["USDT"])
            log_info(f"Loaded STEEM Price from Cryptocompare: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from Cryptocompare: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_coinmarketcap(max_retry: int, retry_interval: int, api_key: str):
    if not api_key:
        log_error("coinmarketcap_api_key not set in config.json or environment")
        sys.exit(1)

    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price in USD directly from CoinGecko
            response = requests.get(
                "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest?symbol=STEEM&CMC_PRO_API_KEY="
                + api_key
            )
            json_data = response.json()
            steem_price = float(json_data["data"]["STEEM"][0]["quote"]["USD"]["price"])
            log_info(f"Loaded STEEM Price from CoinMarketCap: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from CoinMarketCap: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_binance(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price in USDT directly from Binance
            response = requests.get("https://api.binance.com/api/v3/avgPrice?symbol=STEEMUSDT")
            json_data = response.json()
            steem_price = float(json_data["price"])
            log_info(f"Loaded STEEM Price from Binance: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from Binance: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_poloniex(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price from Poloniex
            response = requests.get("https://api.poloniex.com/markets/price")
            # j_data = response.json()
            json_data = {x["symbol"]: x for x in response.json()}
            steem_price = -1.0
            if json_data["STEEM_BTC"] and json_data["BTC_USDT"]:
                # log_info("STEEM_BTC and BTC_USDT")
                steem_price = float(json_data["STEEM_BTC"]["price"]) * float(json_data["BTC_USDT"]["price"])
            if json_data["STEEM_TRX"] and json_data["TRX_USDT"]:
                # log_info("STEEM_TRX and TRX_USDT")
                steem_price = float(json_data["STEEM_TRX"]["price"]) * float(json_data["TRX_USDT"]["price"])
            if json_data["STEEM_USDT"]:
                # log_info("STEEM_USDT")
                steem_price = float(json_data["STEEM_USDT"]["price"])
            if steem_price > 0:
                log_info(f"Loaded STEEM Price from Binance: {steem_price}")
                return steem_price
            else:
                raise ValueError("Poloniex API Error!")
        except Exception as err:
            log_error(f"Error loading STEEM price from Poloniex: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


def load_price_bittrex(max_retry: int, retry_interval: int):
    retries = 0
    while retries < max_retry:
        try:
            # Load STEEM price in USDT directly from Bittrex
            response = requests.get("https://api.bittrex.com/v3/markets/STEEM-USDT/ticker")
            json_data = response.json()
            steem_price = float(json_data["lastTradeRate"])
            log_info(f"Loaded STEEM Price from Bittrex: {steem_price}")
            return steem_price
        except Exception as err:
            log_error(f"Error loading STEEM price from Bittrex: {err.args[0]}")
            retries += 1
            time.sleep(retry_interval)
    return None


# -------------------------------------------------------------------
# Main Functions
# -------------------------------------------------------------------
def run_pricefeed():
    config = load_config()
    rpc_nodes = get_rpc_node(config)

    account = get_account_name(config)
    if not account:
        log_error("feed_steem_account not set in config.json or environment")
        sys.exit(1)

    exchanges = get_exchanges(config)
    if not exchanges:
        log_error("no exchanges are specified.")
        sys.exit(1)

    coinmarketcap_api_key = get_coinmarketcap_api_key(config)

    # with steempy empty key possible
    active_key = get_active_key(config)
    st = Steem(nodes=rpc_nodes, keys=[active_key]) if active_key else Steem(nodes=rpc_nodes)

    # load prices
    retry_interval = get_retry_interval(config)
    max_retry = get_max_retry(config)

    while True:
        prices = []

        if "cloudflare" in exchanges:
            prices.append(load_price_cloudflare(max_retry, retry_interval))

        if "coingecko" in exchanges:
            prices.append(load_price_coingecko(max_retry, retry_interval))

        if "cryptocompare" in exchanges:
            prices.append(load_price_cryptocompare(max_retry, retry_interval))

        if "coinmarketcap" in exchanges:
            prices.append(load_price_coinmarketcap(max_retry, retry_interval, coinmarketcap_api_key))

        if "binance" in exchanges:
            prices.append(load_price_binance(max_retry, retry_interval))

        if "poloniex" in exchanges:
            prices.append(load_price_poloniex(max_retry, retry_interval))

        if "bittrex" in exchanges:
            prices.append(load_price_bittrex(max_retry, retry_interval))

        prices = list(filter(None, prices))
        if len(prices):
            price = sum(prices) / len(prices)
            log_info(prices)
            log_info(f"Price = {price}")

            publish_feed(st, account, max_retry, retry_interval, price, get_peg_multi(config))
        else:
            log_info("no prices found.")

        # interval=0 means no loop
        interval = get_interval(config)
        if interval:
            time.sleep(interval * 60)
        else:
            break


if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_FILE, filemode="a", format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
    )
    run_pricefeed()
