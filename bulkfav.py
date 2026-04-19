#!/usr/bin/env python3
import json, os, tempfile, shutil

WATCHLIST_PATH = "/data/data/com.termux/files/home/stockdata/watchlist.json"

TICKERS = [
    "AAPL","AMD","BABA","BA","BB","BINI","BTC","CING","FUSN","FLNA","GME",
    "INTC","MARA","MVIS","NIO","NVAX","NVDA","NVFY","OCGN","PLTR","QQQ",
    "SNDL","SOFI","TLRY","TSLA","UP","VSTD","ZJYL"
]

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def atomic_save(path, data):
    dirpath = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=dirpath)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=2)
    shutil.move(tmp, path)

def main():
    data = load_json(WATCHLIST_PATH)

    if "favorites" not in data:
        data["favorites"] = []

    for t in TICKERS:
        if t not in data["favorites"]:
            data["favorites"].append(t)

    atomic_save(WATCHLIST_PATH, data)
    print(f"Added {len(TICKERS)} tickers to favorites.")

if __name__ == "__main__":
    main()
