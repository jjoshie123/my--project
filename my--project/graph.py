#!/usr/bin/env python3
import json
import yfinance as yf
import matplotlib.pyplot as plt
import os

WATCHLIST_PATH = "watchlist.json"
GRAPH_DIR = "/root/my--project/graphs"

def load_watchlist():
    with open(WATCHLIST_PATH, "r") as f:
        data = json.load(f)
    return data.get("tickers", [])

def ensure_graph_dir():
    if not os.path.exists(GRAPH_DIR):
        os.makedirs(GRAPH_DIR)

def fetch_history(ticker, period):
    try:
        return yf.Ticker(ticker).history(period=period)
    except:
        return None

def plot_history(ticker, df, label):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Close"], label=ticker)
    plt.title(f"{ticker} — {label}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()

    filename = f"{GRAPH_DIR}/{ticker}_{label}.png"
    plt.savefig(filename)
    plt.close()

def main():
    ensure_graph_dir()
    tickers = load_watchlist()

    for t in tickers:
        week = fetch_history(t, "1wk")
        month = fetch_history(t, "1mo")
        alltime = fetch_history(t, "max")

        if week is not None and not week.empty:
            plot_history(t, week, "1_week")

        if month is not None and not month.empty:
            plot_history(t, month, "1_month")

        if alltime is not None and not alltime.empty:
            plot_history(t, alltime, "all_time")

    print("Graphs generated.")

if __name__ == "__main__":
    main()
