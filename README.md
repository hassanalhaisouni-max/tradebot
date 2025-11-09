# TradeBot (LLM-Signals + Broker API)

A minimal starter to build a trading bot where ChatGPT (via OpenAI API) generates signals (BUY/SELL/HOLD),
and your code executes orders through a broker API adapter (paper first, then real).

## Quick Start
1) Install Python 3.10+.
2) Create a virtual env and install requirements:
   ```bash
   python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3) Copy `.env.example` to `.env` and fill values.
4) Run a dry test:
   ```bash
   python main.py --symbol AAPL --dry-run 1
   ```
5) When ready, plug a real broker adapter and set `--broker alpaca` (or your adapter) + disable dry-run.

## Structure
- `main.py` — Orchestrates the pipeline.
- `config.toml` — Basic config.
- `signals/llm_signal.py` — Gets a trading signal from OpenAI LLM.
- `data/feed_dummy.py` — Dummy data feed; replace with your real feed (TASI or global).
- `risk/manager.py` — Position sizing + risk checks.
- `broker/adapter_base.py` — Base class for brokers.
- `broker/alpaca_adapter.py` — Example adapter (skeleton). Replace/extend for your broker.
- `utils/logger.py` — Structured logging.
- `.env.example` — Environment variables template.

## Notes
- Keep API keys in `.env` (never commit keys).
- Start with `--dry-run 1` + paper trading with your broker.
- Add alerts (Telegram/email) and robust logging before going live.
