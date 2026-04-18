#!/usr/bin/env python3
import yfinance as yf
import matplotlib.pyplot as plt
import os, json

DATA_FILE = "watchlist.json"
EXPORT_DIR = "/root/storage/shared/IM/graphs"   # Arch → Termux bind mount

TIMEFRAMES = {
    "1D": "1d",
    "5D": "5d",
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y"
}

# -----------------------------------
# Load tickers from im.py output
# -----------------------------------
def load_tickers():
    if not os.path.exists(DATA_FILE):
        print("watchlist.json missing")
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data.get("history", [])

# -----------------------------------
# Fetch historical data
# -----------------------------------
def fetch_history(symbol, period):
    try:
        return yf.Ticker(symbol).history(period=period)
    except:
        return None

# -----------------------------------
# Plot with labels
# -----------------------------------
def plot_timeframe(tickers, label, period):
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    plt.figure(figsize=(14, 7))

    for t in tickers[:20]:  # limit to 20 for readability
        hist = fetch_history(t, period)
        if hist is None or hist.empty:
            continue
        plt.plot(hist.index, hist["Close"], label=t)

    plt.title(f"{label} Performance (Top 20)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()

    out = os.path.join(EXPORT_DIR, f"{label}.png")
    plt.savefig(out)
    plt.close()

    print(f"Saved → {out}")

# -----------------------------------
# Main
# -----------------------------------
def main():
    tickers = load_tickers()
    if not tickers:
        print("No tickers found.")
        return

    print(f"Loaded {len(tickers)} tickers")

    for label, period in TIMEFRAMES.items():
        print(f"Generating {label} graph...")
        plot_timeframe(tickers, label, period)

if __name__ == "__main__":
    main()
