import configparser
from kraken.kraken import KrakenExchange


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_kraken_object(config_file='private.cfg'):
    config = load_config(config_file)
    api_key = config.get('KrakenAPI', 'API_KEY')
    api_secret = config.get('KrakenAPI', 'API_SECRET')

    kraken = KrakenExchange(api_key, api_secret)
    return kraken


if __name__ == "__main__":
    kraken_conn = create_kraken_object()
    kraken_conn.setup_midprice_feed("BTC/USD")
    print("Connected to Kraken WebSocket feed for BTC/USD.")
    print(f"Balances: {kraken_conn.fetch_balances()}")
    print(f"OHLC data for BTC/USD: {kraken_conn.fetch_ohlcv('XBTUSD')}")
