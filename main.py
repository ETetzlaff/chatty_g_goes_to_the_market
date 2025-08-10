from fetch_prices import get_stock_prices
from analyze import analyze_prices
from config import TICKERS

def main():
    prices = get_stock_prices(TICKERS)
    print("📊 Stock Prices:", prices)
    analysis = analyze_prices(prices)
    print("\n💡 GPT Analysis:\n", analysis)

if __name__ == "__main__":
    main()

