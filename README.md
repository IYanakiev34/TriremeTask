# KrakenExchange API Client

The `KrakenExchange` API client is a Python library for interacting with the Kraken cryptocurrency exchange. It supports various operations such as fetching account balances, retrieving OHLCV (Open, High, Low, Close, Volume) data, placing different types of trading orders, and real-time price monitoring through WebSockets.

## Requirements

1. Retrive OHLCV data without libraries like cctx
2. Interact both with PUBLIC and PRIVATE https endpoints
3. Fetch Account Balances
4. Fetch OHLCV data
5. Place market order
    - Allow user to specify: trading pair, amounts, leverage, price, side, etc
    - Return Order ID
6. Setup live mid-price feed using websockets
    - Midprice = (best_bid + best_ask) / 2
    - Allow user to specify: pair
    - Log each new price

## Prerequisites

- Python 3.6 or higher
- `requests` library
- `websocket-client` library

## Installation

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/KrakenExchange.git
    cd KrakenExchange
    ```

2. **Install Dependencies**
    ```bash
    python setup.py install
    ```

## Configuration
Place your api key and secret in the `kraken.cfg` file.

## Usage
Import and use the KrakenExchange I will outline some common use cases:

### Initializing API Client
```python
from kraken import KrakenExchange
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
kraken = create_kraken_object()
```

### Fetching Account Balances

```python
from kraken_exchange import Interval

# Fetch OHLCV data for Bitcoin against USD
ohlcv = kraken.fetch_ohlcv('XBTUSD', Interval.ONE_HOUR)
print(ohlcv)
```

### Place Limit Order
```python
from kraken_exchange import AddOrder, Type, OrderType

# Create an order
order = AddOrder(pair='XBTUSD', type=Type.BUY, ordertype=OrderType.LIMIT, volume='0.5', price='30000')

# Place the order
order_id, error = kraken.place_order(order)
if error:
    print("Error:", error)
else:
    print("Order ID:", order_id)
```

### Setting Up Real-Time Mid-Price Feed
```python
# Monitor mid-price for Ethereum against USD
kraken.setup_midprice_feed('ETHUSD')
```

## License
This project is licensed under: `LGPLv3`


