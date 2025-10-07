from fastapi import FastAPI, Request
from okx_client import place_order, close_position

app = FastAPI()

symbol_map = {
    "BTCUSD": "BTC-USDT",
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

    symbol_raw = data.get("symbol", "BTCUSD").replace("/", "").upper()
    inst_id = symbol_map.get(symbol_raw, symbol_raw)
    signal_type = data.get("type", "BUY").upper()
    volume = float(data.get("volume", 0.01))
    price = data.get("price", None)

    print(f"📘 Símbolo recibido: {symbol_raw} → usado en OKX: {inst_id}")

    try:
        if signal_type in ["BUY", "SELL"]:
            response = place_order(inst_id, signal_type.lower(), volume, price)
        
        elif signal_type == "CLOSE":
            print(f"🔵 Señal de cierre recibida para {inst_id}")
            response_buy = close_position(inst_id, "buy", volume)
            response_sell = close_position(inst_id, "sell", volume)
            response = {
                "buy_close": response_buy,
                "sell_close": response_sell
            }
        else:
            return {"status": "ignored", "reason": f"Tipo de señal no reconocido: {signal_type}"}

        print(f"✅ Orden enviada a OKX: {response}")
        return {"status": "ok", "exchange_response": response}

    except Exception as e:
        print(f"❌ Error procesando señal: {e}")
        import traceback; traceback.print_exc()
        return {"status": "error", "message": str(e)}
