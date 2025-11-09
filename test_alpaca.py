import os, requests
from dotenv import load_dotenv

load_dotenv()  # يقرأ .env من نفس المجلد

KEY = os.getenv("ALPACA_API_KEY_ID")
SECRET = os.getenv("ALPACA_API_SECRET_KEY")
BASE = os.getenv("ALPACA_PAPER_BASE_URL", "https://paper-api.alpaca.markets")

if not KEY or not SECRET:
    raise SystemExit("Missing Alpaca keys in .env (ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY)")

r = requests.get(
    f"{BASE}/v2/account",
    headers={
        "APCA-API-KEY-ID": KEY,
        "APCA-API-SECRET-KEY": SECRET
    },
    timeout=20
)

print("Status:", r.status_code)
print(r.json())
