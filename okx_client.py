import os, base64, hmac, hashlib, time, requests, json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OKX_API_KEY")
SECRET_KEY = os.getenv("OKX_SECRET_KEY")
PASSPHRASE = os.getenv("OKX_PASSPHRASE")
BASE_URL = os.getenv("OKX_BASE_URL", "https://www.okx.com")
SIMULATED = os.getenv("OKX_SIMULATED", "0") == "1"

def _timestamp():
    return time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())


def _sign(timestamp, method, path, body=""):
    message = f"{timestamp}{method.upper()}{path}{body}"
    mac = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode()


def _headers(method, path, body=""):
    timestamp = _timestamp()
    sign = _sign(timestamp, method, path, body)
    headers = {
        "OK-ACCESS-KEY": API_KEY,
        "OK-ACCESS-SIGN": sign,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json",
    }
    if SIMULATED:
        headers["x-simulated-trading"] = "1"
    return headers


def place_order(inst_id, side, size, price=None, order_type="market"):
    """Ejecuta una orden en OKX (en cuenta demo o real)."""
    endpoint = "/api/v5/trade/order"
    url = BASE_URL + endpoint

    side = side.lower()
    if side not in ["buy", "sell"]:
        raise ValueError(f"Lado inválido: {side}. Debe ser 'buy' o 'sell'.")

    min_size = 0.001
    if float(size) < min_size:
        print(f"⚠️ Volumen {size} ajustado al mínimo permitido {min_size}")
        size = min_size

    body = {
        "instId": inst_id,
        "tdMode": "cash",
        "side": side,
        "ordType": order_type,
        "sz": str(size),
    }

    if order_type == "limit" and price:
        body["px"] = str(price)

    body_json = json.dumps(body)
    headers = _headers("POST", endpoint, body_json)

    response = requests.post(url, headers=headers, data=body_json)
    return response.json()

def close_position(inst_id, side, size):
    """Cierra una posición abierta ejecutando la orden contraria."""
    opposite = "sell" if side.lower() == "buy" else "buy"
    return place_order(inst_id, opposite, size)
