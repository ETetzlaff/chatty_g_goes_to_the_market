import feedparser
import random


def get_company_news(ticker, max_items=5):
    url = f"https://news.google.com/rss/search?q={ticker}+stock"
    feed = feedparser.parse(url)
    headlines = []
    for entry in feed.entries[:max_items]:
        headlines.append({"title": entry.title, "link": entry.link})
    return headlines


def get_balanced_headlines(tickers, per_ticker=1, max_total=10):
    all_headlines = []
    for ticker in tickers:
        url = f"https://news.google.com/rss/search?q={ticker}+stock"
        feed = feedparser.parse(url)
        count = 0
        for entry in feed.entries:
            all_headlines.append(
                {"ticker": ticker, "title": entry.title, "link": entry.link}
            )
            count += 1
            if count >= per_ticker:
                break
    random.shuffle(all_headlines)
    return all_headlines[:max_total]
