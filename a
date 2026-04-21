#!/usr/bin/env python3
import os
import json
import time
import math
import requests
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# -------- CONFIG --------
WATCHLIST_PATH = "watchlist.json"
BASE_DIR = "/root/storage/downloads/watchlist_graphs"
LOG_PATH = "/root/storage/downloads/watchlist_graphs_log.json"

BATCH_SIZE = 25
PERIODS = {
    "1mo": "1 Month",
    "1y": "1 Year"
}
SLEEP_BETWEEN_BATCHES = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
    "Accept": "application/json",
}
# ------------------------


def ensure_dirs():
    for bucket in ["1_10", "10_100", "100_plus"]:
        for period in PERIODS.keys():
            path = os.path.join(BASE_DIR, bucket, period)
            os.makedirs(path, exist_ok=True)


def load_watchlist():
    if not os.path.exists(WATCHLIST_PATH):
        return []

    with open(WATCHLIST_PATH, "r") as f:
        data = json.load(f)

    tickers = data.get("tickers", [])
    favorites = data.get("favorites", [])

    merged = []
    seen = set()

    for t in tickers + favorites:
        t = t.upper().strip()
        if t and t not in seen:
            seen.add(t)
            merged.append(t)

    return merged


def fetch_yahoo_list(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["finance"]["result"][0]["quotes"]]
    except Exception:
        return []


def fetch_yahoo_gainers():
    return fetch_yahoo_list(
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=100&scrIds=day_gainers"
    )


def fetch_yahoo_most_active():
    return fetch_yahoo_list(
        "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=100&scrIds=most_actives"
    )


def fetch_stocktwits_trending():
    try:
        r = requests.get(
            "https://api.stocktwits.com/api/2/trending/symbols.json",
            headers=HEADERS,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["symbols"]]
    except Exception:
        return []


def save_log(entry):
    log = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                log = json.load(f)
        except:
            log = []

    log.append(entry)

    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=4)


def get_price(ticker):
    try:
        info = yf.Ticker(ticker).fast_info
        return info.get("last_price", None)
    except:
        return None


def bucket_for_price(price):
    if price is None:
        return None
    if price < 10:
        return "1_10"
    elif price < 100:
        return "10_100"
    else:
        return "100_plus"


def plot_single_ticker(ticker, df, bucket, period_key):
    if df is None or df.empty:
        return False

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Close"], label=ticker)
    plt.title(f"{ticker} — {PERIODS[period_key]}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()

    safe = ticker.replace("/", "_").replace("^", "_")
    filename = os.path.join(BASE_DIR, bucket, period_key, f"{safe}_{period_key}.png")
    plt.savefig(filename)
    plt.close()
    return True


def process_batch(batch, bucket_map):
    result = {t: False for t in batch}

    for period_key in PERIODS.keys():
        try:
            data = yf.download(
                tickers=" ".join(batch),
                period=period_key,
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
        except Exception as e:
            save_log({
                "type": "batch_error",
                "period": period_key,
                "tickers": batch,
                "error": str(e),
                "time": time.time(),
            })
            continue

        multiple = isinstance(data.columns, pd.MultiIndex)

        if multiple:
            for t in batch:
                try:
                    df = data[t]
                    if "Close" not in df.columns:
                        continue
                    bucket = bucket_map.get(t)
                    if bucket:
                        ok = plot_single_ticker(t, df, bucket, period_key)
                        if ok:
                            result[t] = True
                except Exception as e:
                    save_log({
                        "type": "ticker_error",
                        "ticker": t,
                        "period": period_key,
                        "error": str(e),
                        "time": time.time(),
                    })
        else:
            t = batch[0]
            try:
                if "Close" in data.columns:
                    bucket = bucket_map.get(t)
                    if bucket:
                        ok = plot_single_ticker(t, data, bucket, period_key)
                        if ok:
                            result[t] = True
            except Exception as e:
                save_log({
                    "type": "ticker_error",
                    "ticker": t,
                    "period": period_key,
                    "error": str(e),
                    "time": time.time(),
                })

    return result


def main():
    ensure_dirs()

    # Load from watchlist
    tickers = load_watchlist()

    # Add Yahoo + Stocktwits
    tickers += fetch_yahoo_gainers()
    tickers += fetch_yahoo_most_active()
    tickers += fetch_stocktwits_trending()

    # Deduplicate
    seen = set()
    merged = []
    for t in tickers:
        t = t.upper().strip()
        if t and t not in seen:
            seen.add(t)
            merged.append(t)

    tickers = merged

    # Fetch prices + assign buckets
    bucket_map = {}
    for t in tickers:
        price = get_price(t)
        bucket = bucket_for_price(price)
        if bucket:
            bucket_map[t] = bucket

    tickers = [t for t in tickers if t in bucket_map]

    total = len(tickers)
    print(f"Total tickers with valid prices: {total}")

    all_results = {}
    num_batches = math.ceil(total / BATCH_SIZE)

    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, total)
        batch = tickers[start:end]

        print(f"\n[Batch {i+1}/{num_batches}] {start}–{end-1}")
        batch_result = process_batch(batch, bucket_map)
        all_results.update(batch_result)

        time.sleep(SLEEP_BETWEEN_BATCHES)

    success = [t for t, ok in all_results.items() if ok]
    failed = [t for t, ok in all_results.items() if not ok]

    summary = {
        "time": time.time(),
        "total": total,
        "success_count": len(success),
        "failed_count": len(failed),
        "success_sample": success[:20],
        "failed_sample": failed[:20],
        "output_dir": BASE_DIR,
        "periods": list(PERIODS.keys()),
    }
    save_log({"type": "run_summary", **summary})

    print("\nDone.")
    print(f"Success: {len(success)} | Failed: {len(failed)}")
    print(f"Graphs saved under: {BASE_DIR}")
    print(f"Log saved to: {LOG_PATH}")


if __name__ == "__main__":
    main()
