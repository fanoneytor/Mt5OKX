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
    """Ejecuta una orden en OKX."""
    endpoint = "/api/v5/trade/order"
    url = BASE_URL + endpoint

    body = {
        "instId": inst_id,
        "tdMode": "cash",
        "side": side.lower(),  # buy / sell
        "ordType": order_type,  # market / limit
        "sz": str(size),
    }

    if order_type == "limit" and price:
        body["px"] = str(price)

    # JSON real (no usar str.replace)
    body_json = json.dumps(body)

    headers = _headers("POST", endpoint, body_json)

    response = requests.post(url, headers=headers, data=body_json)
    return response.json()
