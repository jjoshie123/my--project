#!/usr/bin/env python3
import json
import yfinance as yf
import os
from datetime import datetime

WATCHLIST_PATH = "watchlist.json"
LOG_PATH = "/root/storage/downloads/pv-log.txt"

def log(msg):
    """Append a timestamped log entry to pv-log.txt."""
    try:
        with open(LOG_PATH, "a") as f:
            f.write(f"[IM] {datetime.now()} - {msg}\n")
    except Exception:
        pass  # Logging should never break the pipeline

def load_watchlist():
    """Load watchlist.json with auto-repair fallback."""
    if not os.path.exists(WATCHLIST_PATH):
        log("watchlist.json missing — creating new structure")
        return {"tickers": [], "favorites": [], "price_buckets": {}}

    try:
        with open(WATCHLIST_PATH, "r") as f:
            data = json.load(f)

        # Auto-repair missing keys
        if "tickers" not in data:
            data["tickers"] = []
        if "favorites" not in data:
            data["favorites"] = []
        if "price_buckets" not in data:
            data["price_buckets"] = {}

        return data

    except Exception as e:
        log(f"ERROR loading watchlist.json: {e}")
        return {"tickers": [], "favorites": [], "price_buckets": {}}

def save_watchlist(data):
    """Write updated watchlist.json."""
    try:
        with open(WATCHLIST_PATH, "w") as f:
            json.dump(data, f, indent=4)
        log("watchlist.json updated successfully")
    except Exception as e:
        log(f"ERROR saving watchlist.json: {e}")

def categorize_by_price(tickers):
    """Sort tickers into price buckets using live market data."""
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
    log("=== IM.PY START ===")

    data = load_watchlist()
    tickers = data.get("tickers", [])
    favorites = data.get("favorites", [])

    log(f"Loaded {len(tickers)} tickers, {len(favorites)} favorites")

    # Build price buckets
    b1, b2, b3 = categorize_by_price(tickers)

    data["price_buckets"] = {
        "1_to_50": b1,
        "50_to_100": b2,
        "100_plus": b3
    }

    save_watchlist(data)

    log("Bucket update complete")
    log("=== IM.PY END ===")

if __name__ == "__main__":
    main()
