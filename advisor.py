import json
import csv
import os
import datetime
from pathlib import Path

import yfinance as yf

from fetch_prices import get_stock_performance
from news_fetcher import get_company_news


# -----------------------------
# Config
# -----------------------------
CSV_FILE = Path("data/schwab_holdings.csv")
JSON_FILE = Path("account.json")
LOGS_DIR = Path("logs")
STARTER_STOCKS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN"]


# -----------------------------
# CSV → JSON Conversion
# -----------------------------
def convert_schwab_csv(csv_file, json_file):
    holdings = []
    cash_balance = 0.0

    if not csv_file.exists():
        raise FileNotFoundError(f"Schwab CSV not found: {csv_file}")

    with open(csv_file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = row.get("Symbol", "").strip()
            if not symbol:
                continue

            try:
                quantity = float(row.get("Quantity", "0").replace(",", ""))
            except ValueError:
                quantity = 0

            try:
                market_value = float(row.get("Market Value", "0").replace(",", ""))
            except ValueError:
                market_value = 0

            # Cash or money market handling
            if (
                "CASH" in symbol.upper()
                or "MONEY MARKET" in row.get("Description", "").upper()
            ):
                cash_balance += market_value
                continue

            holdings.append(
                {"ticker": symbol, "shares": quantity, "market_value": market_value}
            )

    account_data = {
        "account_name": "Schwab Brokerage",
        "cash_balance": cash_balance,
        "holdings": holdings,
        "last_updated": datetime.datetime.now(datetime.UTC).isoformat(),
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(account_data, f, indent=2)

    print(f"✅ Converted {csv_file} → {json_file}")


# -----------------------------
# Fetch Prices
# -----------------------------
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


# -----------------------------
# Utilities
# -----------------------------
def contains_negative_news(headlines):
    negative_keywords = ["lawsuit", "drop", "recall", "miss", "decline", "warn"]
    return any(
        any(kw.lower() in headline.lower() for kw in negative_keywords)
        for headline in headlines
    )


# -----------------------------
# Advisor Logic (Buy/Sell)
# -----------------------------
def analyze_holdings(account_data):
    holdings = account_data.get("holdings", [])
    cash_balance = account_data.get("cash_balance", 0.0)

    # Starter stocks if no holdings or zero shares
    if not holdings or all(h.get("shares", 0) == 0 for h in holdings):
        return analyze_starter(account_data)

    tickers = [h["ticker"] for h in holdings]
    prices = get_prices(tickers)

    recommendations = {"buy": [], "sell": []}
    headlines = {}

    for h in holdings:
        ticker = h["ticker"]
        shares = h.get("shares", 0)
        market_value = h.get("market_value", 0)
        avg_price = market_value / shares if shares else 0
        current_price = prices.get(ticker)

        if current_price is None or avg_price == 0:
            continue

        change_pct = ((current_price - avg_price) / avg_price) * 100
        headlines[ticker] = get_company_news(ticker)

        # Performance data for last month (adjust period as needed)
        perf = get_stock_performance(ticker, period="1mo")

        # Sell rule #1: down >5% from avg purchase price
        if change_pct <= -5:
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": f"Down {change_pct:.2f}% from avg price",
            })
            continue  # skip further checks if already flagged to sell

        # Sell rule #2: negative news
        if contains_negative_news(headlines.get(ticker, [])):
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": "Negative news detected",
            })
            continue

        # Sell rule #3: negative recent performance (e.g., down >5% last month)
        if perf and perf["pct_change"] <= -5:
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": f"Down {perf['pct_change']:.2f}% over last month",
            })
            continue

        # Buy rule: positive recent performance (>5% up in last month)
        if perf and perf["pct_change"] >= 5:
            # Buy more if have cash
            if cash_balance > 100:
                shares_to_buy = round(cash_balance / current_price, 3)
                if shares_to_buy > 0:
                    recommendations["buy"].append({
                        "ticker": ticker,
                        "shares": shares_to_buy,
                        "reason": f"Up {perf['pct_change']:.2f}% over last month, positive momentum",
                    })

    # Buy fallback: buy QQQ if enough cash
    if cash_balance > 500:
        price = prices.get("QQQ")
        if price and price > 0:
            shares = round(cash_balance / price, 3)
            if shares > 0:
                recommendations["buy"].append({
                    "ticker": "QQQ",
                    "shares": shares,
                    "reason": "Tech sector momentum placeholder",
                })

    return recommendations, headlines, prices

def analyze_starter(account_data):
    cash_balance = account_data.get("cash_balance", 0.0)
    headlines = {}
    recommendations = {"buy": [], "sell": []}

    # Get prices for all starter stocks upfront
    prices = get_prices(STARTER_STOCKS)

    # Filter stocks without negative news and with positive recent performance
    filtered_stocks = []
    for ticker in STARTER_STOCKS:
        raw_headlines = get_company_news(ticker)
        headlines[ticker] = raw_headlines

        # Extract just the titles for negative news check
        titles = [h.get("title", "") for h in raw_headlines]

        if contains_negative_news(titles):
            print(f"Skipping {ticker} recommendation due to negative news")
            continue

        # Check recent performance (e.g., 1 month)
        perf = get_stock_performance(ticker, period="1mo")
        print(perf)
        if perf is None or perf["pct_change"] < 0:
            print(f"Skipping {ticker} recommendation due to negative or no recent performance")
            continue

        filtered_stocks.append(ticker)

    if not filtered_stocks:
        print("Warning: All starter stocks flagged by negative news or negative performance, no buys recommended.")
        return recommendations, headlines, prices

    # Recalculate per-stock cash allocation after filtering
    per_stock_cash = cash_balance / len(filtered_stocks)

    for ticker in filtered_stocks:
        price = prices.get(ticker)
        if price and price > 0:
            shares = round(per_stock_cash / price, 3)  # Fractional shares allowed
            if shares > 0:
                recommendations["buy"].append(
                    {
                        "ticker": ticker,
                        "shares": shares,
                        "reason": "Initial stock allocation with fractional shares and positive recent performance",
                    }
                )

    return recommendations, headlines, prices


# -----------------------------
# Run Advisor
# -----------------------------
def run_advisor():
    # Convert CSV to JSON
    convert_schwab_csv(CSV_FILE, JSON_FILE)

    # Load account data
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        account_data = json.load(f)

    # Analyze holdings and get recommendations
    recommendations, headlines, prices = analyze_holdings(account_data)

    # Log results with timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = LOGS_DIR / f"advisor_{timestamp}.json"

    log_data = {
        "timestamp": timestamp,
        "account_data": account_data,
        "prices": prices,
        "headlines": headlines,
        "recommendations": recommendations,
    }

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)

    # Print recommendations
    print(f"\n--- Advisor Recommendations ({timestamp}) ---\n")

    if recommendations["sell"]:
        print("Sell Recommendations:")
        for sell in recommendations["sell"]:
            print(
                f" - Sell {sell['shares']} shares of {sell['ticker']} ({sell['reason']})"
            )
    else:
        print("No sell recommendations.")

    if recommendations["buy"]:
        print("\nBuy Recommendations:")
        # for buy in recommendations["buy"]:
        # print(f" - Buy {buy['shares']} shares of {buy['ticker']} ({buy['reason']})")
        for buy in recommendations["buy"]:
            ticker = buy["ticker"]
            print(f" - Buy {buy['shares']} shares of {ticker} ({buy['reason']})")
            # Print headlines for this ticker
            if ticker in headlines:
                print("   Headlines:")
                for headline in headlines[ticker]:
                    print(f"     * {headline}")
    else:
        print("\nNo buy recommendations.")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    run_advisor()
