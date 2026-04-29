#!/usr/bin/env python3
import json

FILE = "watchlist.json"

with open(FILE) as f:
    data = json.load(f)

# Ensure watchlist is a list
if not isinstance(data.get("watchlist"), list):
    data["watchlist"] = []

for item in data.get("trending", []):
    ticker = item.get("ticker")
    if ticker and ticker not in data["watchlist"]:
        data["watchlist"].append(ticker)
        print(f"Added {ticker} to watchlist")

with open(FILE, "w") as f:
    json.dump(data, f, indent=2)

print("Watchlist updated.")
