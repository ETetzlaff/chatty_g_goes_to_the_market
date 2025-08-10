import yfinance as yf
from datetime import datetime

def get_stock_prices(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        data[ticker] = round(price, 2)
    return data

if __name__ == "__main__":
    from config import TICKERS
    print(get_stock_prices(TICKERS))
