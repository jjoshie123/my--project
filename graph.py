#!/usr/bin/env python3
import os, json, glob, datetime
import yfinance as yf
import matplotlib.pyplot as plt

# --- PATHS (Termux + Arch PRoot safe) ---
WATCHLIST = "/data/data/com.termux/files/home/stockdata/watchlist.json"
GRAPH_DIR = "/root/storage/downloads/graphs"
LOG_FILE = "/root/storage/downloads/graph_log.txt"

os.makedirs(GRAPH_DIR, exist_ok=True)

# --- DELETE OLD GRAPHS ---
for f in glob.glob(os.path.join(GRAPH_DIR, "*.png")):
    try:
        os.remove(f)
    except:
        pass

# --- LOAD WATCHLIST + AUTO-REPAIR ---
def load_watchlist():
    if not os.path.exists(WATCHLIST):
        return {"tickers": [], "favorites": []}

    try:
        with open(WATCHLIST, "r") as f:
            data = json.load(f)
    except:
        data = {}

    # Auto-repair missing keys
    if "tickers" not in data or not isinstance(data["tickers"], list):
        data["tickers"] = []
    if "favorites" not in data or not isinstance(data["favorites"], list):
        data["favorites"] = []

    return data

wl = load_watchlist()
tickers = wl["tickers"]
favorites = wl["favorites"]

# --- LOG TICKERS USED ---
with open(LOG_FILE, "a") as log:
    log.write("\n--- Graph Run: {} ---\n".format(datetime.datetime.utcnow()))
    log.write("Tickers: {}\n".format(tickers))
    log.write("Favorites: {}\n".format(favorites))

# --- FETCH + PLOT ---
def plot_ticker(ticker):
    try:
        data = yf.download(ticker, period="1mo", interval="1d")
        if data.empty:
            return

        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data["Close"], label=ticker, linewidth=2)
        plt.title(f"{ticker} - 1 Month Close Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.grid(True)
        plt.legend()

        out = os.path.join(GRAPH_DIR, f"{ticker}.png")
        plt.savefig(out)
        plt.close()

    except Exception as e:
        with open(LOG_FILE, "a") as log:
            log.write(f"Error plotting {ticker}: {e}\n")

# --- GENERATE GRAPHS ---
for t in tickers:
    plot_ticker(t)

for f in favorites:
    plot_ticker(f)
