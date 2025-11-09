from __future__ import annotations
import os, requests

class AlpacaAdapter:
    def __init__(self, paper: bool = True):
        self.key = os.getenv("ALPACA_API_KEY_ID")
        self.secret = os.getenv("ALPACA_API_SECRET_KEY")
        self.base = os.getenv("ALPACA_PAPER_BASE_URL","https://paper-api.alpaca.markets") if paper else "https://api.alpaca.markets"
        if not (self.key and self.secret):
            raise RuntimeError("ALPACA credentials missing in environment")

    def place_order(self, symbol: str, side: str, qty: float, sl: float | None = None, tp: float | None = None):
        # Basic market order; extend for SL/TP brackets as needed.
        payload = {
            "symbol": symbol,
            "qty": qty,
            "side": side.lower(),
            "type": "market",
            "time_in_force": "gtc",
        }
        r = requests.post(
            f"{self.base}/v2/orders",
            headers={
                "APCA-API-KEY-ID": self.key,
                "APCA-API-SECRET-KEY": self.secret,
                "Content-Type": "application/json"
            },
            json=payload, timeout=30
        )
        r.raise_for_status()
        return r.json()
