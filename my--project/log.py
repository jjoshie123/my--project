#!/usr/bin/env python3
import json
import os
import yfinance as yf
from datetime import datetime

PROJECT_DIR = "/root/my--project"
WATCHLIST_FILE = f"{PROJECT_DIR}/watchlist.json"
LOG_DIR = f"{PROJECT_DIR}/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def load_watchlist():
    with open(WATCHLIST_FILE, "r") as f:
        data = json.load(f)
        return data.get("tickers", []), data.get("favorites", [])

def fetch_info(ticker):
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker,
            "price": info.get("regularMarketPrice"),
            "change": info.get("regularMarketChangePercent"),
            "volume": info.get("regularMarketVolume"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "day_low": info.get("dayLow"),
            "day_high": info.get("dayHigh"),
        }
    except:
        return None

def write_log(favorites, tickers):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logfile = f"{LOG_DIR}/log_{timestamp}.txt"

    with open(logfile, "w") as f:
        f.write(f"=== DAILY LOG — {timestamp} ===\n\n")

        f.write("=== FAVORITES ===\n")
        for fav in favorites:
            info = fetch_info(fav)
            if info:
                f.write(f"{info}\n")
        f.write("\n")

        f.write("=== ALL TICKERS ===\n")
        for t in tickers:
            info = fetch_info(t)
            if info:
                f.write(f"{info}\n")

    print(f"[OK] Log saved: {logfile}")
    return logfile

def git_push(logfile):
    os.system(f"cd {PROJECT_DIR} && git add {logfile}")
    os.system(f"cd {PROJECT_DIR} && git commit -m 'Auto log update'")
    os.system(f"cd {PROJECT_DIR} && git push")
    print("[OK] Git push complete")

def main():
    tickers, favorites = load_watchlist()
    logfile = write_log(favorites, tickers)
    git_push(logfile)

if __name__ == "__main__":
    main()
