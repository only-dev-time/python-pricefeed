# Steem Witness Price Feed Publishing Tool

![image](https://user-images.githubusercontent.com/1764434/173547905-6366f5eb-22dc-4327-bbda-6a4cc4cd3b96.png)

This is a python version of the price feed publishing tool from [rexthetech's](https://github.com/rexthetech/pricefeed) respectively [justyy's](https://github.com/DoctorLai/pricefeed) javascript version.

This version is especially intended for witnesses who already use steem-python and do not want to enter their private key in config.json. With the wallet tool [steempy](https://steem.readthedocs.io/en/latest/cli.html) the keys can be used in such a way that they do not have to be stored locally in plain text. For configuration of steempy look at this [tutorial](https://steemit.com/utopian-io/@steempytutorials/part-1-how-to-configure-the-steempy-cli-wallet-and-upvote-an-article-with-steem-python).

This version uses my updated Python library [steempy](https://github.com/only-dev-time/steempy).

## Run with Docker

I suggest runnig the pricefeed in a docker container.
Docker Compose keeps the witness account and other non-secret runtime settings in `config.json`. The private active key and optional API keys belong in `.env`; `.env` is ignored by Git and excluded from the image build context.

Clone the project repo into the "pricefeed" directory and set permissions to run the script for all users:

```bash
git clone https://github.com/only-dev-time/python-pricefeed pricefeed
cd pricefeed
```

Copy the example environment file and set your private active key:

```bash
cp .env.example .env
```

Set `feed_steem_account` in `config.json`, then build and start the service:

```bash
docker compose up -d --build
```

View the feed process logs with `docker compose logs -f`. Stop it with `docker compose down`. Changes to `config.json` or `.env` require recreating the container with `docker compose up -d`.

## Local Installation

### Setup & Installation

Python and the Python library for Steem [steempy](https://github.com/only-dev-time/steempy) must be installed on the system.

Clone the project repo into the "pricefeed" directory and set permissions to run the script for all users:

```bash
git clone https://github.com/only-dev-time/python-pricefeed pricefeed
cd pricefeed
chmod a+x feed.py pricefeed_start.sh
```

Set your witness account name in `config.json`. Provide the private active key through an environment variable or use [steempy](https://github.com/only-dev-time/steempy/blob/master/docs/cli.rst).
*Note:* `steempy` currently doesn't support storing the keys for `cli` in a container.

### Run in background as cron job

 using then crontab to manage and run your python pricefeed in the background. Use the following command to install the cron job for running the pricefeed program:

```bash
crontab -e
```

Add the following line to the end of existing entries:

```bash
46 3,15 * * * ~/pricefeed/pricefeed_start.sh &
```

Maybe you have to change the path. Save the file with `Ctrl+X` (if you use the nano editor). Now the script will start at 3:46 am/pm every day. In that case, the script should be configured that the internal loop only runs once. For this, set the field `interval: 0` in `config.json` (see below).

### Run in background by starting manually

You can also start the program once and then let the internal loop run continuously. For this, set `interval` in `config.json` with the delay time in minutes (see below).
Start the program with following bash command:

```bash
sh pricefeed_start.sh
```

If everything worked you should not see any errors in the logs and a price feed transaction should have been published to your account.

## Configuration

### `config.json`

List of STEEM RPC nodes to use and other settings:

```json
{
  "rpc_nodes": [
    "https://api.moecki.online",
    "https://api.steem.fans",
    "https://steemd.steemworld.org",
    "https://api.steememory.com",
    "https://api.justyy.com",
    "https://api2.justyy.com",
    "https://api.pennsif.net",
    "https://api.steemit.com"
  ],
  "feed_steem_account": "",                     // Name of your Steem witness account
  "exchanges": ["cloudflare", "coingecko", "coinmarketcap"],  // List of exchanges to use. Will publish an average of all exchanges in the list.
  "interval": 60,                               // Number of minutes between feed publishes
  "feed_publish_interval": 30,                  // Feed published after 30 seconds of price feed - not necessary in python
  "feed_publish_fail_retry": 5,                 // RPC node fail over to next after 5 retries - not necessary in python
  "price_feed_max_retry": 5,                    // Max retry for Price Feed API
  "retry_interval": 10,                         // Retry interval 10 seconds
  "peg_multi": 1                                // Feed bias setting, quote will be set to 1 / peg_multi
}
```

### `.env`

```bash
FEED_STEEM_ACTIVE_KEY=          # add your private active key for the feed_publish operation
COINMARKETCAP_API_KEY=          # add your api key if you want to use CoinMarketCap
```
