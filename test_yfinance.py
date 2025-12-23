"""
Quick test to see if yfinance can get real-time index prices.
Run: pip install yfinance && python test_yfinance.py
"""
import yfinance as yf

symbols = ["^GSPC", "^DJI", "^IXIC", "^RUT"]

print("Testing yfinance for real-time index prices...\n")

for symbol in symbols:
    ticker = yf.Ticker(symbol)

    # Get current price info
    info = ticker.info

    # Try different price fields
    price = info.get("regularMarketPrice") or info.get("currentPrice")
    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
    change = info.get("regularMarketChange")
    change_pct = info.get("regularMarketChangePercent")

    print(f"{symbol}:")
    print(f"  Price: {price}")
    print(f"  Prev Close: {prev_close}")
    print(f"  Change: {change}")
    print(f"  Change %: {change_pct}")
    print()
