#!/usr/bin/env python3
import os, json, tempfile, subprocess
from datetime import datetime, UTC
import requests

FILE = "watchlist.json"

FINNHUB_KEY = os.environ.get("FINNHUB_KEY")
ALPHA_KEY   = os.environ.get("ALPHA_KEY")


# -----------------------------
# Safe JSON load / save
# -----------------------------
def load():
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        return {
            "watchlist": [],
            "favorites": [],
            "gainers": [],
            "trending": [],
            "active": [],
            "meta": {
                "last_sync": None,
                "trending_history": []
            }
        }
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "watchlist": [],
            "favorites": [],
            "gainers": [],
            "trending": [],
            "active": [],
            "meta": {
                "last_sync": None,
                "trending_history": []
            }
        }


def save(data):
    tmp_fd, tmp_path = tempfile.mkstemp()
    with os.fdopen(tmp_fd, "w") as tmp:
        json.dump(data, tmp, indent=2)
        tmp.flush()
        os.fsync(tmp.fileno())
    os.replace(tmp_path, FILE)


# -----------------------------
# Helpers
# -----------------------------
def get_json(url, params):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Fetch error:", url, e)
        return None


# -----------------------------
# Finnhub primary
# -----------------------------
def finnhub_gainers():
    if not FINNHUB_KEY:
        return []
    # NOTE: adjust endpoint/filters as you refine; this is a starting point.
    url = "https://finnhub.io/api/v1/scan/technical"
    payload = {
        "symbol": "US",
        "resolution": "D",
        "token": FINNHUB_KEY,
    }
    data = get_json(url, payload)
    if not data:
        return []
    # You’ll likely refine this based on actual Finnhub response structure.
    return []


def finnhub_active():
    if not FINNHUB_KEY:
        return []
    # Placeholder – you can wire to your preferred Finnhub endpoint/logic.
    return []


def finnhub_trending():
    if not FINNHUB_KEY:
        return []
    # Placeholder – e.g., based on news sentiment or your own Finnhub logic.
    return []


# -----------------------------
# Alpha Vantage fallback
# -----------------------------
def alpha_gainers_and_active():
    if not ALPHA_KEY:
        return [], []
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TOP_GAINERS_LOSERS",
        "apikey": ALPHA_KEY,
    }
    data = get_json(url, params)
    if not data:
        return [], []

    gainers = [x.get("ticker") for x in data.get("top_gainers", []) if x.get("ticker")]
    active  = [x.get("ticker") for x in data.get("most_actively_traded", []) if x.get("ticker")]
    return gainers, active


def alpha_trending():
    # Alpha doesn’t have a perfect “trending” concept; we can reuse gainers+active union.
    gainers, active = alpha_gainers_and_active()
    return sorted(set(gainers) | set(active))


# -----------------------------
# Unified fetch functions
# -----------------------------
def fetch_gainers():
    g = finnhub_gainers()
    if g:
        return g
    g2, _ = alpha_gainers_and_active()
    return g2


def fetch_active():
    a = finnhub_active()
    if a:
        return a
    _, a2 = alpha_gainers_and_active()
    return a2


def fetch_trending():
    t = finnhub_trending()
    if t:
        return t
    return alpha_trending()


# -----------------------------
# Auto-favorite logic
# -----------------------------
def auto_favorite(data):
    trending = set(data["trending"])
    gainers  = set(data["gainers"])
    active   = set(data["active"])

    combined = trending | gainers | active
    for t in combined:
        count = (t in trending) + (t in gainers) + (t in active)
        if count >= 2 and t not in data["favorites"]:
            data["favorites"].append(t)

    hist = data["meta"].get("trending_history", [])
    hist.append(list(trending))
    if len(hist) > 3:
        hist = hist[-3:]
    data["meta"]["trending_history"] = hist

    if len(hist) == 3:
        common = set(hist[0]) & set(hist[1]) & set(hist[2])
        for t in common:
            if t not in data["favorites"]:
                data["favorites"].append(t)

    return data


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    data = load()

    print("Fetching Gainers…")
    gainers = fetch_gainers()
    if gainers:
        data["gainers"] = gainers
    else:
        print("No new gainers – keeping previous list.")

    print("Fetching Most Active…")
    active = fetch_active()
    if active:
        data["active"] = active
    else:
        print("No new active – keeping previous list.")

    print("Fetching Trending…")
    trending = fetch_trending()
    if trending:
        data["trending"] = trending
    else:
        print("No new trending – keeping previous list.")

    print("Applying auto-favorite rules…")
    data = auto_favorite(data)

    data["meta"]["last_sync"] = datetime.now(UTC).isoformat()
    save(data)

    print("Import + separation + auto-favorite complete.")
    print("Updating graphs…")
    subprocess.run(["python", "graph.py"])
    print("Graphs updated.")
