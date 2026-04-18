#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime, UTC

FINNHUB_KEY = os.getenv("FINNHUB_KEY")
ALPHA_KEY = os.getenv("ALPHA_KEY")

WATCHLIST_FILE = "watchlist.json"

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        print("watchlist.json not found.")
        return {"watchlist": []}

    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("Error loading watchlist:", e)
        return {"watchlist": []}

def save_watchlist(data):
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(data, f, indent=4)
        print("Updated watchlist.json")
    except Exception as e:
        print("Error saving watchlist:", e)

def fetch_finnhub_price(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "c" in data and data["c"] != 0:
            return data["c"]
    except:
        pass
    return None

def fetch_alpha_price(ticker):
    try:
        url = (
            "https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_KEY}"
        )
        r = requests.get(url, timeout=5)
        data = r.json()
        price = data.get("Global Quote", {}).get("05. price")
        if price:
            return float(price)
    except:
        pass
    return None

def fetch_price(ticker):
    # Try Finnhub first
    price = fetch_finnhub_price(ticker)
    if price is not None:
        print(f"{ticker}: {price} (Finnhub)")
        return price

    # Fallback to Alpha Vantage
    price = fetch_alpha_price(ticker)
    if price is not None:
        print(f"{ticker}: {price} (Alpha)")
        return price

    print(f"{ticker}: FAILED")
    return None

def main():
    data = load_watchlist()
    tickers = data.get("watchlist", [])

    if not tickers:
        print("No tickers found in watchlist.json")
        return

    print("Fetching latest prices...")

    updated = {}
    for t in tickers:
        price = fetch_price(t)
        if price is not None:
            updated[t] = {
                "price": price,
                "updated": datetime.now(UTC).isoformat()
            }

    data["latest"] = updated
    save_watchlist(data)

    print("Price import complete.")

if __name__ == "__main__":
    main()
