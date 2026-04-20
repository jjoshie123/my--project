#!/usr/bin/env python3
import json
import os
import tempfile
import shutil
import requests
import matplotlib.pyplot as plt

WATCHLIST_PATH = "/root/my--project/watchlist.json"
GRAPH_DIR = "/root/storage/downloads/graphs"
LOG_PATH = "/root/storage/downloads/pv-log.txt"
YF_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="


def log(msg: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")


def atomic_save(path, data):
    dirpath = os.path.dirname(path)
    os.makedirs(dirpath, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
    shutil.move(tmp, path)


def load_data():
    if not os.path.exists(WATCHLIST_PATH):
        raise FileNotFoundError(f"Missing watchlist.json at {WATCHLIST_PATH}")
    with open(WATCHLIST_PATH, "r") as f:
        data = json.load(f)
    return data


def get_current_prices(tickers):
    if not tickers:
        return {}

    url = YF_QUOTE_URL + ",".join(tickers)
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        result = r.json().get("quoteResponse", {}).get("result", [])
    except Exception as e:
        log(f"[ERROR] Fetching prices failed: {e}")
        return {}

    prices = {}
    for q in result:
        symbol = q.get("symbol")
        price = q.get("regularMarketPrice")
        if symbol is not None and price is not None:
            prices[symbol] = price
    return prices


def plot_bar(prices, title, filename):
    if not prices:
        log(f"[WARN] No prices to plot for {title}")
        return

    os.makedirs(GRAPH_DIR, exist_ok=True)

    tickers = list(prices.keys())
    values = [prices[t] for t in tickers]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(tickers, values, color="steelblue")
    ax.set_title(title)
    ax.set_ylabel("Price")
    ax.set_xticks(range(len(tickers)))
    ax.set_xticklabels(tickers, rotation=45, ha="right")

    plt.tight_layout()
    out_path = os.path.join(GRAPH_DIR, filename)
    plt.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"Saved {out_path}")
    log(f"Saved graph: {out_path}")


def main():
    log("=== graph.py START ===")

    data = load_data()
    log(f"Loaded watchlist.json from: {WATCHLIST_PATH}")
    log(f"Raw keys: {list(data.keys())}")

    # --- Auto-repair structure ---
    changed = False

    if "tickers" not in data or not isinstance(data["tickers"], list):
        data["tickers"] = []
        changed = True

    if "favorites" not in data or not isinstance(data["favorites"], list):
        data["favorites"] = []
        changed = True

    if "history" not in data or not isinstance(data["history"], list):
        data["history"] = []
        changed = True

    if "portfolio" not in data or not isinstance(data["portfolio"], dict):
        data["portfolio"] = {}
        changed = True

    for key in ["portfolio_value", "daily_gain", "daily_gain_pct", "last_fetch"]:
        if key not in data:
            data[key] = 0
            changed = True

    if changed:
        log("[AUTO-REPAIR] watchlist.json structure fixed in graph.py")
        atomic_save(WATCHLIST_PATH, data)

    tickers = data["tickers"]
    favorites = data["favorites"]

    # --- Auto-repair empty tickers ---
    if not tickers:
        log("[AUTO-REPAIR] No tickers found in graph.py. Using placeholder AAPL.")
        tickers = ["AAPL"]
        data["tickers"] = tickers
        atomic_save(WATCHLIST_PATH, data)

    log(f"Tickers for graphing: {tickers}")
    log(f"Favorites for graphing: {favorites}")

    if not tickers:
        print("No tickers found.")
        log("No tickers found in graph.py")
        return

    print(f"Tickers: {', '.join(tickers)}")

    # Fetch current prices
    prices_all = get_current_prices(tickers)
    log(f"Fetched prices for {len(prices_all)} tickers")

    # Plot all tickers
    plot_bar(prices_all, "All Tickers - Current Prices", "all_tickers.png")

    # Plot favorites if any
    fav_tickers = [t for t in favorites if t in prices_all]
    if fav_tickers:
        prices_fav = {t: prices_all[t] for t in fav_tickers}
        plot_bar(prices_fav, "Favorites - Current Prices", "favorites.png")
    else:
        log("No favorites with prices to plot.")


if __name__ == "__main__":
    main()
