#!/usr/bin/env python3
import requests, json, os, tempfile
from datetime import datetime

FILE = "watchlist.json"
URL  = "https://api.stocktwits.com/api/2/trending/symbols.json"


# -----------------------------
# Safe JSON load
# -----------------------------
def load():
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        print("watchlist.json missing or empty — recreating.")
        return {
            "watchlist": [],
            "trending": [],
            "meta": {"last_sync": None}
        }

    with open(FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            print("watchlist.json corrupted — resetting.")
            return {
                "watchlist": [],
                "trending": [],
                "meta": {"last_sync": None}
            }


# -----------------------------
# Atomic‑safe JSON save
# -----------------------------
def save(data):
    tmp_fd, tmp_path = tempfile.mkstemp()
    with os.fdopen(tmp_fd, "w") as tmp:
        json.dump(data, tmp, indent=2)
        tmp.flush()
        os.fsync(tmp.fileno())
    os.replace(tmp_path, FILE)


# -----------------------------
# Fetch trending tickers
# -----------------------------
def fetch_trending():
    try:
        r = requests.get(URL, timeout=10)
    except Exception as e:
        print("Network error:", e)
        return []

    if r.status_code != 200:
        print("Bad response:", r.status_code)
        print(r.text[:200])
        return []

    try:
        payload = r.json()
    except Exception:
        print("Invalid JSON returned:")
        print(r.text[:200])
        return []

    trending = []
    for s in payload.get("symbols", []):
        trending.append({
            "ticker": s.get("symbol"),
            "name": s.get("title"),
            "price": None,
            "change": None,
            "change_pct": None
        })

    return trending


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    data = load()
    data["trending"] = fetch_trending()
    data["meta"]["last_sync"] = datetime.utcnow().isoformat()
    save(data)
    print("Trending updated successfully.")
