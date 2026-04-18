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
        return {"watchlist": [], "latest": {}}

    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except:
        return {"watchlist": [], "latest": {}}

def save_watchlist(data):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

def fetch_finnhub_price(ticker):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "c" in data and data["c"] != 0:
            return data["c"], data.get("pc", None)
    except:
        pass
    return None, None

def fetch_alpha_price(ticker):
    try:
        url = (
            "https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_KEY}"
        )
        r = requests.get(url, timeout=5)
        data = r.json().get("Global Quote", {})
        price = data.get("05. price")
        prev = data.get("08. previous close")
        if price:
            return float(price), float(prev) if prev else None
    except:
        pass
    return None, None

def fetch_price(ticker):
    price, prev = fetch_finnhub_price(ticker)
    if price:
        return price, prev, "Finnhub"

    price, prev = fetch_alpha_price(ticker)
    if price:
        return price, prev, "Alpha"

    return None, None, None

def main():
    data = load_watchlist()
    tickers = data.get("watchlist", [])

    if not tickers:
        print("No tickers in watchlist.json")
        return

    print("Fetching prices...")

    results = []
    portfolio_value = 0

    for t in tickers:
        price, prev, source = fetch_price(t)

        if price is None:
            print(f"{t}: FAILED")
            continue

        change = None
        pct = None

        if prev:
            change = price - prev
            pct = (change / prev) * 100

        results.append({
            "ticker": t,
            "price": price,
            "prev": prev,
            "change": change,
            "pct": pct,
            "source": source,
            "updated": datetime.now(UTC).isoformat()
        })

        portfolio_value += price

    # Sort by biggest movers (descending %)
    results_sorted = sorted(
        results,
        key=lambda x: x["pct"] if x["pct"] is not None else -9999,
        reverse=True
    )

    # Save to watchlist.json
    data["latest"] = {r["ticker"]: r for r in results_sorted}
    save_watchlist(data)

    # Pretty output for pv
    print("\n=== Portfolio Update ===")
    for r in results_sorted:
        t = r["ticker"]
        p = r["price"]
        c = r["change"]
        pct = r["pct"]

        if pct is None:
            print(f"{t}: {p:.2f} ({r['source']})")
        else:
            arrow = "▲" if pct >= 0 else "▼"
            print(f"{t}: {p:.2f}  {arrow} {c:.2f} ({pct:.2f}%)")

    print(f"\nPortfolio Value: ${portfolio_value:.2f}")
    print("Import complete.")

if __name__ == "__main__":
    main()
