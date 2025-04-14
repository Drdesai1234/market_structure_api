# Market Structure API

A FastAPI service that detects market structure break-up and shift for entry signals.

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoint
POST /market-structure-signal
Sends a list of candles and returns signal, entry, stop loss, and target.
