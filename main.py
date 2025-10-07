from fastapi import FastAPI, Request
from okx_client import place_order

app = FastAPI()

symbol_map = {
    "BTCUSD": "BTC-USDT",
    "ETHUSD": "ETH-USDT",
    "XAUUSD": "XAU-USDT-SWAP",
    "NAS100": "US100-USDT-SWAP",
    "SPX500": "SP500-USDT-SWAP",
}


@app.post("/signal")
async def receive_signal(request: Request):
    raw_body = await request.body()
    body_str = raw_body.decode("utf-8").strip().replace("\0", "")
    print(f"🟡 Cuerpo recibido crudo: {body_str}")

    import json
    try:
        data = json.loads(body_str)
    except Exception as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return {"status": "error", "message": str(e)}

    # Datos clave
    symbol_raw = data.get("symbol", "BTCUSD").replace("/", "").upper()
    inst_id = symbol_map.get(symbol_raw, symbol_raw)
    side = data.get("type", "BUY").lower()
    volume = data.get("volume", 0.01)
    price = data.get("price", None)

    # Debug
    print(f"📘 Símbolo recibido: {symbol_raw} → usado en OKX: {inst_id}")

    # Enviar orden
    response = place_order(inst_id, side, volume, price)

    print(f"✅ Orden enviada a OKX: {response}")
    return {"status": "ok", "exchange_response": response}
