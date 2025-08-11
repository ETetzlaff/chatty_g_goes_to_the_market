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


def get_stock_prices_with_change(tickers):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")  # Ensure we have at least 2 days
        if len(hist) >= 2:
            latest = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2]
            pct_change = ((latest - prev) / prev) * 100
            data[ticker] = {
                "price": round(latest, 2),
                "change_pct": round(pct_change, 2)
            }
        else:
            data[ticker] = {"price": None, "change_pct": None}
    return data


if __name__ == "__main__":
    from config import TICKERS
    print(get_stock_prices(TICKERS))


