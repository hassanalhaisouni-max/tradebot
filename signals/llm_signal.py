import os, json, requests, time, random
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

class Signal(TypedDict):
    action: str
    size_pct: float
    stop_loss_pct: float | None
    take_profit_pct: float | None

PROMPT_TEMPLATE = """You are a cautious trading signal generator.
Return JSON with keys: action(BUY/SELL/HOLD), size_pct(0..100), stop_loss_pct, take_profit_pct.
Rules:
- Use the provided trend: if trend=up → favor BUY, if trend=down → favor SELL.
- If action is BUY or SELL, size_pct must be at least 5 (never 0).
- Prefer HOLD only when trend is unclear. Do not output HOLD twice in a row if trend is clearly up or down.
- Default stops: stop_loss_pct ≈ 1.0, take_profit_pct ≈ 2.0.
Input:
{market_summary}
Output JSON only:
"""


def get_signal(market_summary: str, model: str = "gpt-4o-mini", temperature: float = 0.0) -> Signal:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing in environment")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT_TEMPLATE.format(market_summary=market_summary)}],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    # retry with exponential backoff on 429/5xx
    max_retries = 5
    delay = 2.0
    for attempt in range(1, max_retries + 1):
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            sig = json.loads(content)
            sig["action"] = sig.get("action", "HOLD")
            sig["size_pct"] = float(sig.get("size_pct", 0))
            sig["stop_loss_pct"] = sig.get("stop_loss_pct", None)
            sig["take_profit_pct"] = sig.get("take_profit_pct", None)
            return sig  # ✅ نهاية صحيحة

        if r.status_code in (429, 500, 502, 503, 504):
            retry_after = float(r.headers.get("Retry-After", 0) or 0)
            time.sleep(max(retry_after, delay + random.random()))
            delay *= 2
            continue

        r.raise_for_status()

    # لو فشل كل شيء، ارجع HOLD كوقاية
    return {"action": "HOLD", "size_pct": 0.0, "stop_loss_pct": None, "take_profit_pct": None}

