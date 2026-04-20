#!/usr/bin/env python3
import json
import yfinance as yf
import os
from datetime import datetime

WATCHLIST_PATH = "watchlist.json"
LOG_PATH = "/root/storage/downloads/pv-log.txt"

def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[IM] {datetime.now()} - {msg}\n")

def load_watchlist():
    if not os.path.exists(WATCHLIST_PATH):
        log("watchlist.json missing — creating empty structure")
        return {"tickers": [], "favorites": [], "price_buckets": {}}

    try:
        with open(WATCHLIST_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        log(f"ERROR loading watchlist.json: {e}")
        return {"tickers": [], "favorites": [], "price_buckets": {}}

def save_watchlist(data):
    with open(WATCHLIST_PATH, "w") as f:
        json.dump(data, f, indent=4)
    log("watchlist.json updated")

def categorize_by_price(tickers):
    bucket_1_50 = []
    bucket_50_100 = []
    bucket_100_plus = []

    for t in tickers:
        try:
            info = yf.Ticker(t).fast_info
            price = info.get("last_price")

            if price is None:
                log(f"{t}: No price returned")
                continue

            if 1 <= price < 50:
                bucket_1_50.append(t)
            elif 50 <= price < 100:
                bucket_50_100.append(t)
            elif price >= 100:
                bucket_100_plus.append(t)

            log(f"{t}: price={price}")

        except Exception as e:
            log(f"Failed price fetch for {t}: {e}")

    return bucket_1_50, bucket_50_100, bucket_100_plus

def main():
    data = load_watchlist()

    tickers = data.get("tickers", [])
    favorites = data.get("favorites", [])

    log(f"Loaded {len(tickers)} tickers")

    b1, b2, b3 = categorize_by_price(tickers)

    data["price_buckets"] = {
        "1_to_50": b1,
        "50_to_100": b2,
        "100_plus": b3
    }

    save_watchlist(data)

    log("Bucket update complete")

if __name__ == "__main__":
    main()
