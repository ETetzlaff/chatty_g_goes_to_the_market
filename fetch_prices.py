import yfinance as yf


def get_prices(tickers):
    prices = {}
    if not tickers:
        return prices

    try:
        data = yf.download(tickers=tickers, period="1d", interval="1m")["Close"].iloc[
            -1
        ]
        for ticker in tickers:
            prices[ticker] = float(data[ticker]) if ticker in data else None
    except Exception as e:
        print(f"Error fetching prices: {e}")

    return prices


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
                "change_pct": round(pct_change, 2),
            }
        else:
            data[ticker] = {"price": None, "change_pct": None}
    return data


def get_stock_performance(ticker, period="1mo"):
    data = yf.Ticker(ticker).history(period=period)
    if data.empty or len(data) < 2:
        return None
    start_price = data["Close"].iloc[0]
    end_price = data["Close"].iloc[-1]
    pct_change = ((end_price - start_price) / start_price) * 100
    return {
        "pct_change": pct_change,
        "start_price": start_price,
        "end_price": end_price,
    }


if __name__ == "__main__":
    from config import TICKERS

    print(get_stock_prices(TICKERS))
