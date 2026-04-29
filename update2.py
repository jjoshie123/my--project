#!/usr/bin/env python3
import os, json, shutil, asyncio
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from yahooquery import Screener
from flask import Flask, send_from_directory, jsonify

# ============================================================
# CONFIG
# ============================================================
ROOT = "/root"
GRAPH_DIR = f"{ROOT}/graphs"
TERMUX_EXPORT = "/data/data/com.termux/files/home/storage/shared/StockGraphs"
WATCHLIST = f"{ROOT}/watchlist.json"

BATCH_SIZE = 15
MAX_CONCURRENT = 4

BUCKETS = {
    "1_10": (1, 10),
    "10_100": (10, 100),
    "100_plus": (100, 999999)
}

# ============================================================
# WATCHLIST
# ============================================================
def load_watchlist():
    if not os.path.exists(WATCHLIST):
        return {"tickers": [], "favorites": []}
    with open(WATCHLIST) as f:
        return json.load(f)

def save_watchlist(data):
    with open(WATCHLIST, "w") as f:
        json.dump(data, f, indent=2)

def add_tickers(new):
    wl = load_watchlist()
    combined = list(dict.fromkeys(new + wl.get("tickers", [])))
    wl["tickers"] = combined
    save_watchlist(wl)
    return combined

# ============================================================
# SCREENER
# ============================================================
def fetch_all_sources():
    s = Screener()
    names = ["day_gainers", "most_actives", "trending_tickers"]
    tickers = []
    for n in names:
        try:
            data = s.get_screeners([n])
            tickers += [q["symbol"] for q in data[n]["quotes"]]
        except:
            pass
    return list(dict.fromkeys(tickers))

# ============================================================
# ASYNC DATA FETCH
# ============================================================
def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

async def fetch_batch(tickers, period, sem):
    async with sem:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: yf.download(" ".join(tickers),
                                period=period,
                                group_by="ticker",
                                progress=False)
        )

async def fetch_all(tickers, periods):
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    data = {p: {} for p in periods}

    for p in periods:
        tasks = [fetch_batch(batch, p, sem) for batch in chunk(tickers, BATCH_SIZE)]
        results = await asyncio.gather(*tasks)

        for batch, df in zip(chunk(tickers, BATCH_SIZE), results):
            for t in batch:
                try:
                    data[p][t] = df[t]
                except:
                    continue
    return data

# ============================================================
# INDICATORS
# ============================================================
def compute_indicators(df):
    if df is None or df.empty:
        return df

    df = df.copy()

    # EMA
    df["EMA20"] = df["Close"].ewm(span=20).mean()

    # RSI
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Volume spike
    df["VolAvg"] = df["Volume"].rolling(20).mean()
    df["VolSpike"] = df["Volume"] > (2 * df["VolAvg"])

    return df

# ============================================================
# ALERTS
# ============================================================
def detect_signals(ticker, df):
    signals = []
    if df is None or df.empty:
        return signals

    last = df.iloc[-1]

    # Breakout (price > EMA)
    if last["Close"] > last["EMA20"]:
        signals.append("EMA_BREAKOUT")

    # RSI
    if last["RSI"] > 70:
        signals.append("OVERBOUGHT")
    elif last["RSI"] < 30:
        signals.append("OVERSOLD")

    # Volume spike
    if last["VolSpike"]:
        signals.append("VOLUME_SPIKE")

    return signals

# ============================================================
# GRAPHING
# ============================================================
def normalize(df):
    return (df["Close"] / df["Close"].iloc[0]) * 100

def plot_with_indicators(t, df, path):
    if df is None or df.empty:
        return

    plt.figure(figsize=(10,5))
    plt.plot(df.index, df["Close"], label="Price")
    plt.plot(df.index, df["EMA20"], label="EMA20")

    plt.title(t)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def plot_normalized(group, data, period, out):
    plt.figure(figsize=(12,6))
    for t in group:
        df = data[period].get(t)
        if df is None or df.empty:
            continue
        plt.plot(df.index, normalize(df), label=t)

    plt.title(f"Normalized % — {period}")
    plt.legend(fontsize=8)
    plt.grid()
    plt.tight_layout()
    plt.savefig(out)
    plt.close()

# ============================================================
# BUCKETING
# ============================================================
def bucketize(tickers, data_1d):
    buckets = {b: [] for b in BUCKETS}
    for t in tickers:
        try:
            price = data_1d[t]["Close"].iloc[-1]
        except:
            continue

        for name, (low, high) in BUCKETS.items():
            if low <= price < high:
                buckets[name].append(t)
                break
    return buckets

# ============================================================
# DASHBOARD
# ============================================================
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "running", "graphs": os.listdir(GRAPH_DIR)})

@app.route("/graphs/<path:path>")
def graphs(path):
    return send_from_directory(GRAPH_DIR, path)

# ============================================================
# MAIN
# ============================================================
async def main():
    tickers = fetch_all_sources()
    tickers = add_tickers(tickers)

    wl = load_watchlist()
    favs = wl.get("favorites", [])

    all_tickers = list(set(tickers + favs))
    periods = ["1d","1mo","3mo","6mo","5y"]

    data = await fetch_all(all_tickers, periods)

    # compute indicators
    signals_out = {}

    for p in data:
        for t in data[p]:
            data[p][t] = compute_indicators(data[p][t])

    # bucket
    buckets = bucketize(tickers, data["1d"])

    # reset graph dir
    if os.path.exists(GRAPH_DIR):
        shutil.rmtree(GRAPH_DIR)
    os.makedirs(GRAPH_DIR, exist_ok=True)

    # generate graphs + signals
    for b, ts in buckets.items():
        for t in ts:
            for p in ["1mo","3mo"]:
                df = data[p].get(t)
                plot_with_indicators(t, df,
                    f"{GRAPH_DIR}/{b}_{t}_{p}.png")

                sigs = detect_signals(t, df)
                if sigs:
                    signals_out[t] = sigs

        # normalized group chart
        plot_normalized(ts, data, "1mo",
            f"{GRAPH_DIR}/{b}_normalized.png")

    # favorites long-term
    for p in ["6mo","5y"]:
        plot_normalized(favs, data, p,
            f"{GRAPH_DIR}/favorites_{p}.png")

    # export
    if os.path.exists(TERMUX_EXPORT):
        shutil.rmtree(TERMUX_EXPORT)
    shutil.copytree(GRAPH_DIR, TERMUX_EXPORT)

    # save signals
    with open(f"{GRAPH_DIR}/signals.json","w") as f:
        json.dump(signals_out, f, indent=2)

    print("Signals:", signals_out)

# ============================================================
if __name__ == "__main__":
    asyncio.run(main())

    # optional dashboard
    # run separately if needed
    # app.run(host="0.0.0.0", port=5000)
