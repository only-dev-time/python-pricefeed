# Steem Witness Price Feed Publishing Tool

![image](https://user-images.githubusercontent.com/1764434/173547905-6366f5eb-22dc-4327-bbda-6a4cc4cd3b96.png)

## Install nodejs & npm (TODO: CHECK)
If you already have nodejs & npm installed you can skip this section, but I wanted to include it here for thoroughness. Run the following commands to install nodejs and npm in order to run the pricefeed software:

```bash
$ sudo apt-get update
$ curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -
$ sudo apt-get install -y nodejs
```

## Setup & Installation
Clone the project repo into the "pricefeed" directory and set permissions to run the script for all users:

```bash
$ git clone https://github.com/only-dev-time/python-pricefeed pricefeed
$ cd pricefeed
$ chmod a+x feed.py
$ chmod a+x pricefeed_start.sh
```

Update the config.json file with your witness account name and private active key as described in the Configuration section below. Alternative, you can set account and private key in environment variables or you can use [steempy](https://steem.readthedocs.io/en/latest/cli.html)

### Run in background as cron job
I suggest using the using of crontab to manage and run your python pricefeed in the background. Use the following commands to install the cron job and run the pricefeed program:

```bash
$ crontab -e
```

Add following line to the end of existing entries:

```bash
46 3,15 * * * ~/pricefeed/pricefeed_start.sh &
```

Save the file with <code>Ctrl+X</code>. Now the script will start at 3:46 am/pm every day.
In that case, the script should be configured so that the internal loop only runs once. For this, set <code>"interval": 0</code> in config.json (see below).

### Run in background by starting manually
You can also start the programme once and then let the internal loop run continuously. For this, set <code>"interval"</code> in config.json with the delay time in minutes (see below).
Start the program with following bash-command:

```bash
$ sh pricefeed_start.sh
```

If everything worked you should not see any errors in the logs and a price feed transaction should have been published to your account.

## Configuration
List of STEEM RPC nodes to use and other settings:

```json
{
  "rpc_nodes": [
    "https://api.steemit.com",
    "https://steemapi.boylikegirl.club",
    "https://api.steemzzang.com",
    "https://steem.ecosynthesizer.com",
    "https://api.wherein.io",
    "https://api.dlike.io",
    "https://api.steem-fanbase.com",
    "https://api.steemitdev.com",
    "https://api.justyy.com"
  ],
  "feed_steem_account": "",                     // Name of your Steem witness account - if left empty, then should be set in env.
  "feed_steem_active_key": "",                  // Private active key of your Steem witness account - if left empty, then should be set in env or in steempy
  "coinmarketcap_api_key": "",                  // API key for CoinMarketCap; required if using "coinmarketcap" in exchange list below. Set in env if empty.
  "exchanges": ["cloudflare", "coingecko", "cryptocompare", "coinmarketcap"],  // List of exchanges to use. Will publish an average of all exchanges in the list.
  "interval": 60,                               // Number of minutes between feed publishes
  "feed_publish_interval": 30,                  // Feed published after 30 seconds of price feed - not necessary in python
  "feed_publish_fail_retry": 5,                 // RPC node fail over to next after 5 retries - not necessary in python
  "price_feed_max_retry": 5,                    // Max retry for Price Feed API
  "retry_interval": 10,                         // Retry interval 10 seconds
  "peg_multi": 1                                // Feed bias setting, quote will be set to 1 / peg_multi
}
```
