from __future__ import annotations
import argparse, os, tomli
from dotenv import load_dotenv

from utils.logger import info, warn, err
from data.feed_dummy import get_latest_bars, summarize_bars
from signals.llm_signal import get_signal
from risk.manager import RiskManager
from broker.adapter_base import PaperAdapter

# -----------------------------
# Broker selection
# -----------------------------
def choose_broker(name: str):
    if name == "paper":
        return PaperAdapter()
    elif name == "alpaca":
        from broker.alpaca_adapter import AlpacaAdapter
        return AlpacaAdapter(paper=True)
    else:
        warn("Unknown broker; falling back to PAPER", broker=name)
        return PaperAdapter()

# -----------------------------
# SL/TP helpers
# -----------------------------
def compute_sl_tp(last_price: float, sl_pct: float | None, tp_pct: float | None):
    sl = last_price * (1 - sl_pct / 100) if sl_pct else None
    tp = last_price * (1 + tp_pct / 100) if tp_pct else None
    return sl, tp

# -----------------------------
# Config loader
# -----------------------------
def load_cfg():
    with open("config.toml", "rb") as f:
        return tomli.load(f)

# -----------------------------
# Main
# -----------------------------
def main():
    load_dotenv()
    cfg = load_cfg()

    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="AAPL")
    ap.add_argument("--bars", type=int, default=50)
    ap.add_argument("--broker", default=cfg["broker"]["name"])
    ap.add_argument("--dry-run", type=int, default=1)
    args = ap.parse_args()

    # 1) Data feed (استبدل feed_dummy ببيانات حقيقية لاحقًا)
    bars = get_latest_bars(args.symbol, args.bars)
    summary = summarize_bars(bars)
    last_price = bars[-1]["close"]
    info("bars_ready", symbol=args.symbol, last_price=last_price)

    # 2) Signal (LLM or Offline)
    use_offline = os.getenv("OFFLINE_SIGNALS", "0") == "1"
    if use_offline:
        # وضع اختباري بدون استدعاء LLM
        sig = {"action": "BUY", "size_pct": 10.0, "stop_loss_pct": 1.0, "take_profit_pct": 2.0}
    else:
        sig = get_signal(
            summary,
            model=cfg["signals"]["model"],
            temperature=cfg["signals"]["temperature"],
        )

    # --- Fallbacks لتجنّب HOLD أو حجم صفقة = 0 ---
    # حد أدنى لحجم الصفقة عند وجود BUY/SELL
    MIN_SIZE_PCT = 5.0

    # إذا رجّع LLM HOLD أو حجم 0، نولّد قرارًا بسيطًا من الميل (trend)
    if sig["action"] == "HOLD" or float(sig.get("size_pct", 0)) <= 0:
        closes = [b["close"] for b in bars]
        last = closes[-1]
        avg = sum(closes) / len(closes)
        sig["action"] = "BUY" if last > avg else "SELL"
        sig["size_pct"] = max(MIN_SIZE_PCT, float(sig.get("size_pct", 0)))
        # قيم افتراضية معقولة لإدارة المخاطر
        if not sig.get("stop_loss_pct"):
            sig["stop_loss_pct"] = max(0.5, float(cfg["risk"].get("default_sl_pct", 1.0)))
        if not sig.get("take_profit_pct"):
            sig["take_profit_pct"] = max(1.0, float(cfg["risk"].get("default_tp_pct", 2.0)))

    # ضمان الحد الأدنى عند BUY/SELL
    if sig["action"] in ["BUY", "SELL"]:
        sig["size_pct"] = max(MIN_SIZE_PCT, float(sig.get("size_pct", 0)))

    info("signal", **sig)

    # 3) Risk management (حجم الصفقة + ضوابط)
    rm = RiskManager(
        account_cash=float(os.getenv("ACCOUNT_CASH", cfg["general"]["account_cash"])),
        max_daily_loss_pct=cfg["risk"]["max_daily_loss_pct"],
        max_position_pct=cfg["risk"]["max_position_pct"],
    )
    qty = rm.size_from_pct(price=last_price, size_pct=float(sig["size_pct"]))

    # 4) Execute via broker
    broker = choose_broker(args.broker)
    sl, tp = compute_sl_tp(last_price, sig.get("stop_loss_pct"), sig.get("take_profit_pct"))
    side = "buy" if sig["action"] == "BUY" else "sell"

    if sig["action"] in ["BUY", "SELL"] and qty > 0 and rm.can_open_new_position():
        if args.dry_run:
            info("DRY_RUN", action=sig["action"], symbol=args.symbol, qty=qty, sl=sl, tp=tp)
        else:
            res = broker.place_order(args.symbol, side, qty, sl, tp)
            # قص الرد لكي لا يطول اللوج
            info("order_placed", broker=args.broker, qty=qty, sl=sl, tp=tp, response=str(res)[:300])
    else:
        info("HOLD_or_zero_qty", action=sig["action"], qty=qty)

if __name__ == "__main__":
    main()
