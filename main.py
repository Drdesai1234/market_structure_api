from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Candle(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float

class TradeSignal(BaseModel):
    signal: str
    entry: float = None
    stop_loss: float = None
    target: float = None

def is_bullish_candle(candle):
    return candle['close'] > candle['open']

@app.post("/market-structure-signal", response_model=TradeSignal)
def market_structure_signal(data: List[Candle]):
    resistance_level = max([c.high for c in data[-20:]])
    avg_volume = sum([c.volume for c in data[-20:]]) / 20
    buffer = 0.002 * resistance_level  # 0.2% buffer

    breakup_confirmed = False

    for i in range(50, len(data)):
        c = data[i]
        if not breakup_confirmed:
            if c.close > resistance_level and c.volume > avg_volume:
                breakup_confirmed = True
                demand_zone = resistance_level
        else:
            if demand_zone - buffer <= c.low <= demand_zone + buffer:
                prev = data[i-2]
                if c.low > prev.low and c.high > prev.high:
                    if is_bullish_candle(c.dict()):
                        entry = data[i+1].open if i+1 < len(data) else c.close
                        stop_loss = c.low
                        target = entry + 2 * (entry - stop_loss)
                        return TradeSignal(signal="BUY", entry=entry, stop_loss=stop_loss, target=target)

    return TradeSignal(signal="WAIT")
