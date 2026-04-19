#!/usr/bin/env python3
import json, os, datetime

WATCHLIST = "/data/data/com.termux/files/home/stockdata/watchlist.json"
LOGDIR = "/data/data/com.termux/files/home/stockdata/logs"

def log(msg):
    os.makedirs(LOGDIR, exist_ok=True)
    today = datetime.date.today().isoformat()
    path = f"{LOGDIR}/{today}.log"
    with open(path, "a") as f:
        f.write(msg + "\n")

def load():
    with open(WATCHLIST, "r") as f:
        return json.load(f)

def main():
    data = load()
    tickers = data.get("tickers", [])
    favorites = data.get("favorites", [])
    movers = data.get("movers", [])  # im.py will populate this

    log(f"=== {datetime.datetime.now()} ===")
    log(f"Tickers: {len(tickers)}")
    log(f"Favorites: {len(favorites)}")

    if movers:
        log("Daily Movers:")
        for m in movers:
            log(f"  {m}")

    log("")

if __name__ == "__main__":
    main()
