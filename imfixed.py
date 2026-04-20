import os
import json
import requests
from datetime import datetime

WATCHLIST = "/root/my--project/watchlist.json"
LOG = "/root/my--project/imfixed.log"

def log(msg):
    with open(LOG, "a") as f:
        f.write(msg + "\n")
    print(msg)

def load_watchlist():
    if not os.path.exists(WATCHLIST):
        data = {"tickers": [], "favorites": [], "last_updated": ""}
        save_watchlist(data)
        return data

    try:
        with open(WATCHLIST, "r") as f:
            return json.load(f)
    except:
        data = {"tickers": [], "favorites": [], "last_updated": ""}
        save_watchlist(data)
        return data

def save_watchlist(data):
    with open(WATCHLIST, "w") as f:
        json.dump(data, f, indent=4)

def fetch_yahoo(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["finance"]["result"][0]["quotes"]]
    except Exception as e:
        log(f"Yahoo error: {e}")
        return []

def fetch_stocktwits():
    try:
        r = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json", timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["symbols"]]
    except Exception as e:
        log(f"Stocktwits error: {e}")
        return []

log("=== Running imfixed.py ===")

GAINERS_URL = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=50&scrIds=day_gainers"
ACTIVE_URL  = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=50&scrIds=most_actives"

gainers = fetch_yahoo(GAINERS_URL)
active = fetch_yahoo(ACTIVE_URL)
trending = fetch_stocktwits()

log(f"Gainers: {len(gainers)}")
log(f"Active: {len(active)}")
log(f"Trending: {len(trending)}")

combined = []
for lst in [gainers, trending, active]:
    for t in lst:
        if t not in combined:
            combined.append(t)

log(f"Combined tickers: {len(combined)}")

data = load_watchlist()
data["tickers"] = combined
data["last_updated"] = datetime.utcnow().isoformat()

save_watchlist(data)

log("Watchlist updated successfully.")
