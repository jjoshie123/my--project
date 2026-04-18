#!/usr/bin/env python3
import os
import json
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, UTC

WATCHLIST_FILE = "watchlist.json"
GRAPH_DIR = "graphs"

# Create graph directory if missing
os.makedirs(GRAPH_DIR, exist_ok=True)

# Time windows
NOW = datetime.now(UTC)
WINDOWS = {
    "1w": NOW - timedelta(days=7),
    "1m": NOW - timedelta(days=30),
    "1y": NOW - timedelta(days=365),
}

def load_watchlist():
    if not os.path.exists(WATCHLIST_FILE):
        print("watchlist.json not found.")
        return []

    try:
        with open(WATCHLIST_FILE, "r") as f:
            data = json.load(f)
            return data.get("watchlist", [])
    except Exception as e:
        print("Error loading watchlist:", e)
        return []

def fetch_history(ticker, start):
    try:
        df = yf.download(ticker, start=start, end=NOW, progress=False)
        if df.empty:
            print(f"No data for {ticker}")
            return None
        return df["Close"]
    except Exception as e:
        print(f"Error fetching {ticker}:", e)
        return None

def plot_window(tickers, window_name, start_date):
    plt.figure(figsize=(12, 6))
    plt.title(f"{window_name.upper()} Price History")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")

    plotted = False

    for t in tickers:
        data = fetch_history(t, start_date)
        if data is None:
            continue
        plt.plot(data.index, data.values, label=t)
        plotted = True

    if not plotted:
        print(f"No data to plot for {window_name}")
        plt.close()
        return

    plt.legend()
    out_path = os.path.join(GRAPH_DIR, f"{window_name}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved {out_path}")

def main():
    tickers = load_watchlist()
    if not tickers:
        print("No tickers found in watchlist.json")
        return

    print("Generating graphs...")

    for name, start in WINDOWS.items():
        plot_window(tickers, name, start)

    print("Graph generation complete.")

if __name__ == "__main__":
    main()	
