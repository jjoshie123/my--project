HEADERS = {	
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
    "Accept": "application/json",
}

def fetch_yahoo(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["finance"]["result"][0]["quotes"]]
    except Exception as e:
        log(f"Yahoo error: {e}")
        return []

def fetch_stocktwits():
    try:
        r = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json",
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [x["symbol"] for x in data["symbols"]]
    except Exception as e:
        log(f"Stocktwits error: {e}")
        return []
