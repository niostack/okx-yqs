import ccxt
import websocket
import json
import threading
from config import API_KEY, SECRET_KEY, PASSPHRASE, SYMBOL, TEST


class OkxAPI:
    def __init__(self):
        self.exchange = ccxt.okx(
            {
                "apiKey": API_KEY,
                "secret": SECRET_KEY,
                "password": PASSPHRASE,
                "enableRateLimit": True,
                "options": {"defaultType": "future"},
                "test": TEST,
            }
        )
        self.ws = None
        self.latest_price = None

    def get_ticker(self):
        return self.exchange.fetch_ticker(SYMBOL)

    def create_market_buy_order(self, amount):
        return self.exchange.create_market_buy_order(SYMBOL, amount)

    def create_market_sell_order(self, amount):
        return self.exchange.create_market_sell_order(SYMBOL, amount)

    def start_websocket(self):
        def on_message(ws, message):
            data = json.loads(message)
            if "data" in data:
                self.latest_price = float(data["data"][0]["last"])

        def on_error(ws, error):
            print(f"WebSocket错误: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket连接关闭: {close_status_code} - {close_msg}")

        def on_open(ws):
            print("WebSocket连接打开")
            subscribe_message = {
                "op": "subscribe",
                "args": [{"channel": "tickers", "instId": SYMBOL.replace("/", "-")}],
            }
            ws.send(json.dumps(subscribe_message))

        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://ws.okx.com:8443/ws/v5/public",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def stop_websocket(self):
        if self.ws:
            self.ws.close()

    def get_latest_price(self):
        return self.latest_price
