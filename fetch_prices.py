import yfinance as yf


def get_stock_prices(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")

        if hist.empty:
            # Try last 5 days as a fallback
            hist = stock.history(period="5d")

        if not hist.empty:
            price = hist["Close"].iloc[-1]
            data[ticker] = round(price, 2)
        else:
            data[ticker] = None  # Could not fetch price
    return data


if __name__ == "__main__":
    from config import TICKERS
    print(get_stock_prices(TICKERS))
