import base64
from enum import Enum
import hashlib
import hmac
import json
import time
import threading
import urllib.parse
import requests
import websocket

from kraken.error_handler import KrakenErrorHandler


class Interval(Enum):
    ONE_MINUTE = 1
    FIVE_MINUTES = 5
    FIFTEEN_MINUTES = 15
    THIRTY_MINUTES = 30
    ONE_HOUR = 60
    FOUR_HOURS = 240
    ONE_DAY = 1440
    ONE_WEEK = 10080
    FIFTEEN_DAYS = 21600


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop-loss"
    TAKE_PROFIT = "take-profit"
    STOP_LOSS_LIMIT = "stop-loss-limit"
    TAKE_PROFIT_LIMIT = "take-profit-limit"
    SETTLE_POSITION = "settle-position"


class Type(Enum):
    BUY = "buy"
    SELL = "sell"


class AddOrder:

    def __init__(
        self,
        pair,
        order_type: Type,
        ordertype: OrderType,
        volume,
        price=None,
        leverage=None,
    ):
        self.pair = pair
        self.order_type = order_type
        self.ordertype = ordertype
        self.volume = volume
        self.price = price
        self.leverage = leverage

    def to_dict(self):
        return {
            "pair": self.pair,
            "type": self.order_type.value,
            "ordertype": self.ordertype,
            "volume": self.volume,
            "price": self.price,
            "leverage": self.leverage,
        }


class KrakenExchange:
    HTTPS_API_URL = "https://api.kraken.com"
    WSS_PUBLIC_API_URL = "wss://ws.kraken.com/v2"
    WSS_PRIVATE_API_URL = "wss://ws-auth.kraken.com/v2"

    def __init__(self, api_key: str, api_secret: str):
        """
        Initializes the KrakenExchange with necessary API credentials.

        Parameters:
            api_key (str): API key for accessing Kraken's private API endpoints.
            api_secret (str): API secret used to sign requests securely.

        Attributes:
            HTTPS_API_URL (str): Base URL for HTTPS API requests.
            WSS_PUBLIC_API_URL (str): Base URL for public WebSocket feeds.
            WSS_PRIVATE_API_URL (str): Base URL for private WebSocket feeds.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = None
        self.err_handler = KrakenErrorHandler()

    def _get_websocket_token(self):
        url = f"{self.HTTPS_API_URL}/0/private/GetWebSocketsToken"
        data = {"nonce": self._generate_nonce()}
        headers = {
            "API-Key": self.api_key,
            "API-Sign": self._generate_signature("/0/private/GetWebSocketsToken", data),
        }
        response = requests.post(url, headers=headers, data=data, timeout=10).json()
        self.err_handler.check_for_error(response)
        self.token = response["result"]["token"]

    def _generate_signature(self, urlpath: str, data: dict):
        """
        Generates a signature for API requests.

        Parameters:
            urlpath (str): API endpoint path that needs to be signed.
            data (dict): Data payload for the request which includes the nonce.

        Returns:
            str: The generated signature.
        Note: Implementation is taken from the official kraken REST API documentation.
        """

        postdata = urllib.parse.urlencode(data)
        encoded = (str(data["nonce"]) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _generate_nonce(self):
        """
        Generates a nonce. Nonce is a number that is only used once to prevent replay attacks.

        Returns:
            int: Returns the current time in milliseconds.
        """
        return int(time.time() * 1000)

    def _api_request(self, method: str, endpoint: str, data: dict | None = None):
        url = f"{self.HTTPS_API_URL}{endpoint}"
        headers = {}

        # Initialize data if None for payload manipulation
        if data is None:
            data = {}

        data["nonce"] = self._generate_nonce()
        # Adding nonce for every private request
        if "/private/" in endpoint:
            # Signature needs to be generated after adding nonce and possibly otp
            headers["API-Key"] = self.api_key
            headers["API-Sign"] = self._generate_signature(endpoint, data)

        # Adjust how data is sent based on the method; GET typically does not have a body
        if method.upper() in ["GET", "DELETE"]:
            response = requests.request(
                method, url, headers=headers, params=data, timeout=10
            )
        else:
            response = requests.request(
                method, url, headers=headers, data=data, timeout=10
            )

        return self.err_handler.check_for_error(response.json())

    def setup_midprice_feed(self, pair):
        """
        Sets up a WebSocket connection to receive real-time mid-price updates for a specified trading pair.

        Parameters:
            pair (str): The trading pair to monitor.
        Note:
            This function uses a separate thread to handle the WebSocket connection.
        """

        def on_message(ws, message):  # pylint: disable=unused-argument
            data = json.loads(message)
            if "result" in data and "as" in data["result"] and "bs" in data["result"]:
                best_ask = float(data["result"]["as"][0][0])
                best_bid = float(data["result"]["bs"][0][0])
                mid_price = (best_ask + best_bid) / 2
                print(f"Mid-price update for {pair}: {mid_price}")

        def on_error(ws, error):  # pylint: disable=unused-argument
            print("Error:", error)

        def on_close(ws):  # pylint: disable=unused-argument
            print("### WebSocket closed ###")

        def on_open(ws):
            self._get_websocket_token()  # Ensure token is refreshed
            subscribe_message = {
                "method": "subscribe",
                "params": {"channel": "book", "snapshot": False, "symbol": [pair]},
                "req_id": self._generate_nonce(),
            }
            ws.send(json.dumps(subscribe_message))

        # Choose the correct URL based on whether it's private or public data access
        ws_url = self.WSS_PRIVATE_API_URL if self.token else self.WSS_PUBLIC_API_URL
        ws = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        threading.Thread(target=ws.run_forever).start()

    def fetch_balances(self):
        """
        Fetches the account balances from Kraken's private API.

        Returns:
            dict: A dictionary containing balance information or an error message.
            Example result: {
            "error": [ ],
            "result": {
                "ZUSD": "171288.6158",
                "ZEUR": "504861.8946",
                "XXBT": "1011.1908877900",
                "XETH": "818.5500000000"
            }
        }
        """
        endpoint = "/0/private/Balance"
        response = self._api_request("POST", endpoint)
        return response

    def fetch_ohlcv(
        self, pair: str, interval: Interval = Interval.ONE_MINUTE, since: int = None
    ):
        """
        Fetches OHLCV data for a specified trading pair, inteval, and optional since timestamp.

        Parameters:
            pair (str): Trading pair to fetch data for, e.g., 'XBTUSD'.
            interval (Interval): Time frame interval from the Interval Enum.
            since (int, optional): Timestamp in seconds since when to fetch historical data.

        Returns:
            dict: A dictionary containing OHLCV data or an error message.
        """

        endpoint = "/0/public/OHLC"
        data = {
            "pair": pair,
            "interval": interval.value,
        }
        if since:
            data["since"] = since
        response = self._api_request("GET", endpoint, data)
        return response

    def place_order(self, order: AddOrder):
        """
        Places an order on the Kraken exchange.

        Parameters:
            order (AddOrder): An object containing order details.

        Returns:
            tuple: A tuple containing the transaction ID of the placed order or an error message.
        """

        endpoint = "/0/private/AddOrder"
        order_dict = order.to_dict()

        response = self._api_request("POST", endpoint, order_dict)
        # Extract and return order ID
        txid = response.get("result", {}).get("txid", [])
        return txid[0]
