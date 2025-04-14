from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Candle(BaseModel):
    open: float
    high: float
    low: float
    close: float

class CandleList(BaseModel):
    candles: List[Candle]

@app.post("/analyze")
def analyze_market(candle_data: CandleList):
    candles = candle_data.candles
    if len(candles) < 10:
        return {"error": "Need at least 10 candles for analysis"}

    last = candles[-1]
    recent_highs = [c.high for c in candles[-5:]]
    recent_lows = [c.low for c in candles[-5:]]

    support = min(recent_lows)
    resistance = max(recent_highs)

    structure = "Consolidation"
    suggestion = "Wait for clear structure"
    demand_zone = None
    entry_price = None
    stop_loss = None
    take_profit = None

    # Break-Up Structure
    if last.close > resistance:
        structure = "Break-Up"
        suggestion = "Wait for pullback to demand zone"
        # Get last bullish candle before breakout
        last_bullish = next((c for c in reversed(candles[:-1]) if c.close > c.open), None)
        if last_bullish:
            demand_zone = {"high": last_bullish.high, "low": last_bullish.low}
            entry_price = round(last_bullish.low + (last_bullish.high - last_bullish.low) / 2, 2)
            stop_loss = round(last_bullish.low, 2)
            take_profit = round(last.high, 2)

    # Liquidation Phase
    elif last.close < support:
        structure = "Liquidation"
        suggestion = "Watch for reversal signs (MSS)"

    # Market Structure Shift
    elif last.low < candles[-2].low and last.high > candles[-2].high:
        structure = "Market Structure Shift (MSS)"
        suggestion = "Look for entry after confirmation"

    return {
        "structure": structure,
        "last_price": last.close,
        "support": support,
        "resistance": resistance,
        "suggestion": suggestion,
        "demand_zone": demand_zone,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }from fastapi import FastAPI, HTTPException
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
