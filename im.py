#!/usr/bin/env python3
import json, os, requests, time, tempfile, shutil
WATCHLIST_PATH = "/root/my--project/watchlist.json"
# === ATOMIC SAVE ===
def atomic_save(path, data):
    dirpath = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
    shutil.move(tmp, path)

# === LOAD WATCHLIST ===
if not os.path.exists(WATCHLIST_PATH):
    raise FileNotFoundError(f"Missing watchlist.json at {WATCHLIST_PATH}")

with open(WATCHLIST_PATH, "r") as f:
    data = json.load(f)

TICKERS = data.get("tickers", [])

# === LOAD FAVORITES ===
def load_favorites():
    if not os.path.exists(WATCHLIST_PATH):
        return []
    with open(WATCHLIST_PATH, "r") as f:
        d = json.load(f)
    return sorted(list(set(d.get("favorites", []))))

FAVORITES = load_favorites()

# Merge favorites into tickers
for t in FAVORITES:
    if t not in TICKERS:
        TICKERS.append(t)

# === MOVERS GLOBAL ===
MOVERS = []

# === FETCH LOOP ===
YF_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="

def fetch_quotes(tickers):
    url = YF_URL + ",".join(tickers)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return r.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        print(f"[ERROR] Fetch failed: {e}")
        return []

def process_quotes(quotes):
    results = {}

    for q in quotes:
        try:
            ticker = q.get("symbol")
            price = q.get("regularMarketPrice", 0)
            change = q.get("regularMarketChange", 0)
            change_pct = q.get("regularMarketChangePercent", 0)
            volume = q.get("regularMarketVolume", 0)
            avg_volume = q.get("averageDailyVolume3Month", 0)

            # Detect movers
            if abs(change_pct) >= 5:
                MOVERS.append(f"{ticker}: {change_pct:.2f}%")

            results[ticker] = {
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "avg_volume": avg_volume
            }

        except Exception as e:
            print(f"[PARSE ERROR] {e}")
            continue

    return results

print("Fetching quotes...")
quotes = fetch_quotes(TICKERS)
time.sleep(0.3)

DATA = process_quotes(quotes)
print(f"Fetched {len(DATA)} tickers.")

# === PORTFOLIO MATH ===
portfolio_value = 0
daily_gain = 0

for t, info in DATA.items():
    price = info["price"]
    change = info["change"]

    portfolio_value += price
    daily_gain += change

data["portfolio_value"] = round(portfolio_value, 2)
data["daily_gain"] = round(daily_gain, 2)

if portfolio_value != 0:
    data["daily_gain_pct"] = round((daily_gain / (portfolio_value - daily_gain)) * 100, 2)
else:
    data["daily_gain_pct"] = 0

# === SAVE RESULTS ===
data["movers"] = MOVERS
data["last_fetch"] = time.time()

atomic_save(WATCHLIST_PATH, data)

print("=== im.py complete ===")
