#!/usr/bin/env python3
import os
import time
import json
import math
import textwrap
import yfinance as yf
import matplotlib.pyplot as plt

# -------- CONFIG --------
TICKER_LIST_PATH = "all_tickers.txt"  # one symbol per line
OUTPUT_DIR = "/root/storage/downloads/yahoo_all_graphs"
LOG_PATH = "/root/storage/downloads/yahoo_all_graphs_log.json"

# Safety cap so you don't nuke your device on first run
MAX_TICKERS = 200          # set to None to process all
BATCH_SIZE = 50            # yfinance.download batch size
HISTORY_PERIOD = "1mo"     # 1mo / 3mo / 6mo / 1y / max
SLEEP_BETWEEN_BATCHES = 2  # seconds, to be nice to Yahoo

# ------------------------


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_tickers():
    if not os.path.exists(TICKER_LIST_PATH):
        raise FileNotFoundError(
            f"Ticker list file not found: {TICKER_LIST_PATH}. "
            "Create all_tickers.txt with one symbol per line."
        )

    with open(TICKER_LIST_PATH, "r") as f:
        tickers = [line.strip().upper() for line in f if line.strip()]

    if MAX_TICKERS is not None:
        tickers = tickers[:MAX_TICKERS]

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    return unique


def save_log(entry):
    # Append‑style JSON log
    log = []
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                log = json.load(f)
        except Exception:
            log = []

    log.append(entry)

    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=4)


def plot_single_ticker(ticker, df):
    if df is None or df.empty:
        return False

    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Close"], label=ticker)
    plt.title(f"{ticker} — {HISTORY_PERIOD}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.grid(True)
    plt.legend()

    safe_ticker = ticker.replace("/", "_").replace("^", "_")
    filename = os.path.join(OUTPUT_DIR, f"{safe_ticker}_{HISTORY_PERIOD}.png")
    plt.savefig(filename)
    plt.close()
    return True


def process_batch(batch_tickers):
    """
    Use yfinance.download to fetch a batch of tickers at once.
    Returns dict: {ticker: success_bool}
    """
    result = {t: False for t in batch_tickers}

    try:
        data = yf.download(
            tickers=" ".join(batch_tickers),
            period=HISTORY_PERIOD,
            group_by="ticker",
            auto_adjust=False,
            threads=True,
            progress=False,
        )
    except Exception as e:
        # If batch fails completely, log and bail
        save_log({
            "type": "batch_error",
            "tickers": batch_tickers,
            "error": str(e),
            "time": time.time(),
        })
        return result

    # yfinance returns different shapes depending on number of tickers
    multiple = isinstance(data.columns, pd.MultiIndex) if hasattr(data, "columns") else False

    if multiple:
        # data[ticker]["Close"]
        for t in batch_tickers:
            try:
                df_t = data[t]
                if "Close" not in df_t.columns:
                    continue
                ok = plot_single_ticker(t, df_t)
                result[t] = ok
            except Exception as e:
                save_log({
                    "type": "ticker_error",
                    "ticker": t,
                    "error": str(e),
                    "time": time.time(),
                })
    else:
        # Single ticker case
        t = batch_tickers[0]
        try:
            if "Close" in data.columns:
                ok = plot_single_ticker(t, data)
                result[t] = ok
        except Exception as e:
            save_log({
                "type": "ticker_error",
                "ticker": t,
                "error": str(e),
                "time": time.time(),
            })

    return result


def main():
    import pandas as pd  # local import so script fails loudly if missing

    ensure_output_dir()
    tickers = load_tickers()

    total = len(tickers)
    print(f"Total tickers to process: {total}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"History period: {HISTORY_PERIOD}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Max tickers: {MAX_TICKERS}")

    all_results = {}
    num_batches = math.ceil(total / BATCH_SIZE)

    for i in range(num_batches):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, total)
        batch = tickers[start:end]

        print(f"\n[Batch {i+1}/{num_batches}] {start}–{end-1} ({len(batch)} tickers)")
        batch_result = process_batch(batch)
        all_results.update(batch_result)

        time.sleep(SLEEP_BETWEEN_BATCHES)

    # Summary log
    success = [t for t, ok in all_results.items() if ok]
    failed = [t for t, ok in all_results.items() if not ok]

    summary = {
        "time": time.time(),
        "total": total,
        "success_count": len(success),
        "failed_count": len(failed),
        "success_sample": success[:20],
        "failed_sample": failed[:20],
        "output_dir": OUTPUT_DIR,
        "period": HISTORY_PERIOD,
    }
    save_log({"type": "run_summary", **summary})

    print("\nDone.")
    print(f"Success: {len(success)}  |  Failed: {len(failed)}")
    print(f"Graphs are in: {OUTPUT_DIR}")
    print("Log:", LOG_PATH)


if __name__ == "__main__":
    main()
