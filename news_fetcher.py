import yfinance as yf


def get_company_news(ticker, max_items=3):
    stock = yf.Ticker(ticker)
    try:
        news_items = stock.news or []
    except Exception:
        return []

    headlines = []
    for item in news_items:
        title = item.get("title")
        link = item.get("link")
        if title and link:  # Only include valid entries
            headlines.append({"title": title, "link": link})
        if len(headlines) >= max_items:
            break

    return headlines
