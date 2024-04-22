# API KEY: yFq37dWrUYZF1XO3ezPHf1OO4jTHUr/bwAcqXpTtzMwEZc4Eaa1WMFUJ
# Private Key: 2qIKpzptr0c4FesQdZe5heryunCsrZh0456sm/3KaobLaqq/DqRua4mrpmTAiESywHJHodQCUkvUeJgN296h6Q==

from kraken import KrakenExchange, Interval
import configparser

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_kraken_object(config_file='kraken.cfg'):
    config = load_config(config_file)
    api_key = config.get('KrakenAPI', 'API_KEY')
    api_secret = config.get('KrakenAPI', 'API_SECRET')

    kraken = KrakenExchange(api_key, api_secret)
    return kraken


if __name__ == "__main__":
    kraken_conn = create_kraken_object()
    kraken_conn.setup_midprice_feed("BTC/USD")
    print(f"Connected to Kraken WebSocket feed for BTC/USD.")
    print(f"OHLC data for BTC/USD: {kraken_conn.fetch_ohlcv('BTC/USD', Interval.ONE_MINUTE)}")


