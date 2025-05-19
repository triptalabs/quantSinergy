# services/binance_client.py

import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()  # carga variables de .env
_api_key = os.getenv("BINANCE_API_KEY")
_api_secret = os.getenv("BINANCE_API_SECRET")

# Cliente global
client = Client(_api_key, _api_secret)

def get_balances():
    """Devuelve la lista de balances no cero."""
    account = client.get_account()
    return [b for b in account["balances"] if float(b["free"]) + float(b["locked"]) > 0]

def get_price(symbol: str):
    """Precio de mercado actual de un par (ej. 'BTCUSDT')."""
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])
