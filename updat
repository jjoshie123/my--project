#!/usr/bin/env python3
import json
import os
import yfinance as yf
from datetime import datetime

WATCHLIST_PATH = "watchlist.json"
TMP_PATH = "watchlist_tmp.json"

def load_watchlist():
    if not os.path.exists(WATCHLIST_PATH):
        return {"tickers": [], "favorites": []}

    with open(WATCHLIST_PATH, "r") as f:
        try:
            data = json.load(f)
        except:
            return {"tickers": [], "favorites": []}

    if "tickers" not in data:
        data["tickers"] = []
    if "favorites" not in data:
        data["favorites"] = []

    return data


def fetch_price(ticker):
    try:
        info = yf.Ticker(ticker).fast_info
        return info.get("last_price", None)
    except:
        return None


def update_watchlist():
    wl = load_watchlist()
    tickers = wl.get("tickers", [])
    favorites = wl.get("favorites", [])

    # Deduplicate
    tickers = sorted(list(set(tickers)))
    favorites = sorted(list(set(favorites)))

    # Fetch prices
    prices = {}
    for t in tickers:
        prices[t] = fetch_price(t)

    updated = {
        "tickers": tickers,
        "favorites": favorites,
        "prices": prices,
        "last_update": datetime.now().isoformat()
    }

    # Atomic write
    with open(TMP_PATH, "w") as f:
        json.dump(updated, f, indent=4)

    os.replace(TMP_PATH, WATCHLIST_PATH)

    print("Watchlist updated.")


if __name__ == "__main__":
    update_watchlist()
