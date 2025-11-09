from __future__ import annotations

class RiskManager:
    def __init__(self, account_cash: float, max_daily_loss_pct: float = 2.0, max_position_pct: float = 10.0):
        self.account_cash = float(account_cash)
        self.max_daily_loss_pct = float(max_daily_loss_pct)
        self.max_position_pct = float(max_position_pct)

    def size_from_pct(self, price: float, size_pct: float) -> float:
        alloc_cash = self.account_cash * (size_pct/100.0)
        qty = max(0.0, round(alloc_cash / max(price, 0.01), 4))
        return qty

    # TODO: implement real PnL tracking/circuit breakers
    def can_open_new_position(self) -> bool:
        return True
