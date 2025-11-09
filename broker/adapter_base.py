from __future__ import annotations

class BrokerAdapter:
    def place_order(self, symbol: str, side: str, qty: float, sl: float | None = None, tp: float | None = None):
        raise NotImplementedError

class PaperAdapter(BrokerAdapter):
    def place_order(self, symbol: str, side: str, qty: float, sl: float | None = None, tp: float | None = None):
        print(f"[PAPER] {side.upper()} {qty} {symbol} | SL={sl} | TP={tp}")
