#!/usr/bin/env python3
import requests
import json
import os
import matplotlib.pyplot as plt

DATA_FILE = "/root/my--project/watchlist.json"
EXPORT_DIR = "/root/storage/downloads/graphs"
# -----------------------------
# Load / Save JSON
# -----------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"history": [], "portfolio": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -----------------------------
# Fetch Yahoo Finance Lists
# -----------------------------
def fetch_yahoo_list(scrId, pages=3):
    tickers = []
    for p in range(pages):
        url = (
            "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved"
            f"?count=50&offset={p*50}&scrIds={scrId}"
        )
        try:
            r = requests.get(url, timeout=5).json()
            quotes = r["finance"]["result"][0]["quotes"]
            for q in quotes:
                tickers.append(q["symbol"])
        except:
            pass
    return tickers

# -----------------------------
# Fetch Stocktwits Trending
# -----------------------------
def fetch_trending_stocktwits(limit=50):
    url = "https://api.stocktwits.com/api/2/trending/symbols.json"
    try:
        r = requests.get(url, timeout=5).json()
        return [s["symbol"] for s in r["symbols"]][:limit]
    except:
        return []

# -----------------------------
# Fetch Quote Data
# -----------------------------
def fetch_quote(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    try:
        r = requests.get(url, timeout=5).json()
        q = r["quoteResponse"]["result"][0]
        return {
            "price": q.get("regularMarketPrice", 0),
            "change": q.get("regularMarketChangePercent", 0)
        }
    except:
        return {"price": 0, "change": 0}

# -----------------------------
# Merge Lists (priority)
# -----------------------------
def merge_lists(gainers, trending, active, history):
    merged = []

    for t in gainers:
        if t not in merged:
            merged.append(t)

    for t in trending:
        if t not in merged:
            merged.append(t)

    for t in active:
        if t not in merged:
            merged.append(t)

    for t in history:
        if t not in merged:
            merged.append(t)

    return merged

# -----------------------------
# Build Portfolio Table
# -----------------------------
def build_portfolio_table(tickers):
    table = []
    for t in tickers:
        q = fetch_quote(t)
        table.append({
            "symbol": t,
            "price": q["price"],
            "change": q["change"]
        })
    table.sort(key=lambda x: x["change"], reverse=True)
    return table

# -----------------------------
# Print Clean Output
# -----------------------------
def print_table(table):
    print("\n=== Portfolio View ===")
    for row in table:
        print(f"{row['symbol']:6} | ${row['price']:>8.2f} | {row['change']:>6.2f}%")

# -----------------------------
# Graph Export
# -----------------------------
def export_graph(table):
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    symbols = [row["symbol"] for row in table[:20]]
    changes = [row["change"] for row in table[:20]]

    plt.figure(figsize=(12, 6))
    plt.bar(symbols, changes, color="cyan")
    plt.xticks(rotation=75)
    plt.title("Top 20 % Change")
    plt.tight_layout()

    out = os.path.join(EXPORT_DIR, "gainers_graph.png")
    plt.savefig(out)
    plt.close()

    print(f"\nGraph exported → {out}")

# -----------------------------
# Main
# -----------------------------
def main():
    print("Fetching lists...")

    data = load_data()

    # Safety repair
    if "history" not in data:
        data["history"] = []
    if "portfolio" not in data:
        data["portfolio"] = {}

    gainers = fetch_yahoo_list("day_gainers", pages=3)
    active = fetch_yahoo_list("most_actives", pages=3)
    trending = fetch_trending_stocktwits(limit=50)

    merged = merge_lists(gainers, trending, active, data["history"])
    data["history"] = merged
    save_data(data)

    print(f"Total tickers merged: {len(merged)}")

    table = build_portfolio_table(merged)
    print_table(table)

    export_graph(table)

if __name__ == "__main__":
    main()
