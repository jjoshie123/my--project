import os
import json
import yfinance as yf
import matplotlib.pyplot as plt

WATCHLIST = "/root/my--project/watchlist.json"
GRAPH_DIR = "/root/graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

def load_tickers():
    with open(WATCHLIST, "r") as f:
        data = json.load(f)
    return data.get("tickers", [])

def make_graph(ticker, period, filename):
    try:
        data = yf.Ticker(ticker).history(period=period)
        if data.empty:
            return

        plt.figure(figsize=(10,5))
        plt.plot(data.index, data["Close"], linewidth=2)
        plt.title(f"{ticker} - {period}")
        plt.grid(True)
        plt.savefig(os.path.join(GRAPH_DIR, filename), dpi=300, bbox_inches="tight")
        plt.close()
    except:
        pass

tickers = load_tickers()

for t in tickers[:10]:  # limit for speed
    make_graph(t, "1wk", f"{t}_1w.png")
    make_graph(t, "1mo", f"{t}_1m.png")
    make_graph(t, "1y", f"{t}_1y.png")

print("Graphs generated.")
