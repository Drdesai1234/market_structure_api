from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Market Structure API is live"}

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
    }