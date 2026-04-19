#!/usr/bin/env python3
import yfinance as yf
import matplotlib.pyplot as plt
import os
import sys

# Ensure Python can import im.py from this folder
sys.path.append("/root/my--project")

from im import TICKERS, FAVORITES

# === GRAPH OUTPUT DIRECTORY ===
GRAPH_DIR = "/data/data/com.termux/files/home/stockdata/graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

# === PER-TICKER GRAPH ===
def generate_graph(ticker):
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if df.empty:
            return

        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df["Close"], label=ticker)
        plt.title(f"{ticker} — 1 Month")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"{GRAPH_DIR}/{ticker}.png")
        plt.close()

    except Exception as e:
        print(f"[GRAPH ERROR] {ticker}: {e}")

# === ALL TICKERS COMBINED GRAPH ===
def graph_all_month():
    plt.figure(figsize=(12, 8))

    for t in TICKERS:
        try:
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if df.empty:
                continue
            plt.plot(df.index, df["Close"], label=t)
        except:
            continue

    plt.title("All Tickers — 1 Month Combined")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{GRAPH_DIR}/all_month.png")
    plt.close()

# === FAVORITES COMBINED GRAPH ===
def graph_favorites_month():
    plt.figure(figsize=(12, 8))

    for t in FAVORITES:
        try:
            df = yf.download(t, period="1mo", interval="1d", progress=False)
            if df.empty:
                continue
            plt.plot(df.index, df["Close"], label=t)
        except:
            continue

    plt.title("Favorites — 1 Month Combined")
    plt.legend(fontsize=8)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{GRAPH_DIR}/favorites_month.png")
    plt.close()

# === RUN ALL GRAPH GENERATION ===
print("Generating per‑ticker graphs...")
for t in TICKERS:
    generate_graph(t)

print("Generating combined graphs...")
graph_all_month()
graph_favorites_month()

print("=== graph.py complete ===")
