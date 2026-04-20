#!/usr/bin/env python3
import json, os, time, requests
from datetime import datetime

WATCHLIST_PATH = "/root/my--project/watchlist.json"
LOG_PATH = "/root/storage/downloads/pv-log.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

YF_SOURCES = {
    "gainers": "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers",
    "trending": "https://query1.finance.yahoo.com/v1/finance/trending/US",
    "active": "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=most_actives"
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def fetch_json(url):
    for attempt in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            log(f"Fetch error {url}: {e}")
        time.sleep(1)
    return None

def load_auto_tickers():
    tickers = set()

    # GAINERS
    data = fetch_json(YF_SOURCES["gainers"])
    if data:
        for item in data.get("finance", {}).get("result", [{}])[0].get("quotes", []):
            if "symbol" in item:
                tickers.add(item["symbol"])

    # TRENDING
    data = fetch_json(YF_SOURCES["trending"])
    if data:
        for item in data.get("finance", {}).get("result", [{}])[0].get("quotes", []):
            if "symbol" in item:
                tickers.add(item["symbol"])

    # MOST ACTIVE
    data = fetch_json(YF_SOURCES["active"])
    if data:
        for item in data.get("finance", {}).get("result", [{}])[0].get("quotes", []):
            if "symbol" in item:
                tickers.add(item["symbol"])

    tickers = sorted(list(tickers))
    log(f"Auto-loaded {len(tickers)} tickers")
    return tickers

def fetch_price(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    data = fetch_json(url)
    if not data:
        return None

    try:
        q = data["quoteResponse"]["result"][0]
        return {
            "price": q.get("regularMarketPrice", 0),
            "change": q.get("regularMarketChangePercent", 0),
            "volume": q.get("regularMarketVolume", 0)
        }
    except:
        return None

def build_watchlist(tickers):
    wl = {"tickers": tickers, "favorites": []}
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(wl, f, indent=4)
    log("Wrote new full-auto watchlist.json")

def main():
    log("=== RUN START ===")

    tickers = load_auto_tickers()

    if not tickers:
        log("ERROR: No tickers loaded — inserting fallback AAPL")
        tickers = ["AAPL"]

    build_watchlist(tickers)

    # Fetch loop
    results = []
    for t in tickers:
        info = fetch_price(t)
        if info:
            results.append({
                "symbol": t,
                "price": info["price"],
                "change": info["change"],
                "volume": info["volume"]
            })
            log(f"Fetched {t}: {info}")
        else:
            log(f"FAILED fetch: {t}")

    # Sort by biggest movers
    results.sort(key=lambda x: abs(x["change"]), reverse=True)

    # Print clean PV output
    print("\n=== Portfolio View ===")
    for r in results:
        print(f"{r['symbol']:6}  ${r['price']:>8}  {r['change']:>6}%  Vol {r['volume']}")

    log("=== RUN END ===\n")

if __name__ == "__main__":
    main()
