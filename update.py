#!/usr/bin/env python3
import json, requests, os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
    "Accept": "application/json",
}

WATCHLIST_FILE = "watchlist.json"

def log(msg):
    print(msg)

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        return {"watchlist": []}

    try:
        with open(WATCHLIST_FILE) as f:
            return json.load(f)
    except Exception as e:
        log(f"JSON load error: {e}")
        return {"watchlist": []}

def save_watchlist(data):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

def fetch_yahoo(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["finance"]["result"][0]["quotes"]]
    except Exception as e:
        log(f"Yahoo error: {e}")
        return []

def fetch_stocktwits():
    try:
        r = requests.get(
            "https://api.stocktwits.com/api/2/trending/symbols.json",
            headers=HEADERS,
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["symbols"]]
    except Exception as e:
        log(f"Stocktwits error: {e}")
        return []

# -------------------------
# MAIN PIPELINE
# -------------------------

data = load_watchlist()
watchlist = set(data.get("watchlist", []))

# Fetch from Yahoo
yahoo_url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=false&scrIds=day_gainers"
yahoo_tickers = fetch_yahoo(yahoo_url)
log(f"Yahoo returned {len(yahoo_tickers)} tickers")

# Fetch from Stocktwits
stocktwits_tickers = fetch_stocktwits()
log(f"Stocktwits returned {len(stocktwits_tickers)} tickers")

# Combine
before_count = len(watchlist)
combined = yahoo_tickers + stocktwits_tickers

added = []
for t in combined:
    if t not in watchlist:
        watchlist.add(t)
        added.append(t)

# Save
data["watchlist"] = sorted(list(watchlist))
save_watchlist(data)

# Final logs
log(f"Added {len(added)} new tickers")
if added:
    log("New tickers:")
    for t in added:
        log(f"  - {t}")

log(f"Final watchlist size: {len(watchlist)}")
