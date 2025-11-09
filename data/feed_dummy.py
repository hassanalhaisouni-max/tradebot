from __future__ import annotations
from typing import List, Dict

def get_latest_bars(symbol: str, n: int = 50) -> List[Dict]:
    # Dummy bars; replace with real market data (TASI or global).
    # Each bar: {time, open, high, low, close, volume}
    import random, time
    last = 100.0
    bars = []
    for i in range(n):
        chg = random.uniform(-0.5, 0.5)
        o = last
        c = max(1.0, o + chg)
        h = max(o, c) + random.uniform(0, 0.3)
        l = min(o, c) - random.uniform(0, 0.3)
        bars.append({"time": int(time.time())- (n-i)*60, "open": o, "high": h, "low": l, "close": c, "volume": random.randint(100, 1000)})
        last = c
    return bars

def summarize_bars(bars) -> str:
    # Minimal summary sent to LLM (keep it short and structured)
    closes = [b["close"] for b in bars]
    last = closes[-1]
    avg = sum(closes)/len(closes)
    trend = "up" if last > avg else "down"
    return f"Last close={last:.2f}, avg={avg:.2f}, trend={trend}, bars={len(bars)}"
