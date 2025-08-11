from fetch_prices import get_stock_prices_with_change
from news_fetcher import get_company_news
from analyze import analyze_market
from config import TICKERS


def main():
    prices = get_stock_prices_with_change(TICKERS)
    
    # Determine top performer
    top_ticker = max(
        (t for t in prices if prices[t]["change_pct"] is not None),
        key=lambda t: prices[t]["change_pct"],
        default=None
    )

    if top_ticker:
        headlines = get_company_news(top_ticker)
    else:
        headlines = []

    # Market snapshot
    print("📊 Market Snapshot:")
    for ticker, info in prices.items():
        change_str = f"{info['change_pct']}%" if info['change_pct'] is not None else "N/A"
        print(f"{ticker}: ${info['price']} ({change_str})")

    # GPT analysis
    print(f"\n🏆 Top Performer: {top_ticker}")
    analysis = analyze_market(prices, top_ticker, headlines)
    print("\n💡 GPT Analysis:\n")
    print(analysis)

    # Headlines section
    print("\n📰 Headlines Used:")
    if headlines:
        for h in headlines:
            print(f"- {h['title']}\n  {h['link']}")
    else:
        print("No recent news found.")


if __name__ == "__main__":
    main()
