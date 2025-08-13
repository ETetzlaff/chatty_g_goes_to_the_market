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

    # -----------------------------
    # Sell Recommendations
    # -----------------------------
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
        perf = get_stock_performance(ticker, period="1mo")

        # Sell rules
        if change_pct <= -5:
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": f"Down {change_pct:.2f}% from avg price",
            })
            continue

        if contains_negative_news(headlines.get(ticker, [])):
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": "Negative news detected",
            })
            continue

        if perf and perf["pct_change"] <= -5:
            recommendations["sell"].append({
                "ticker": ticker,
                "shares": shares,
                "reason": f"Down {perf['pct_change']:.2f}% over last month",
            })
            continue

    # -----------------------------
    # Buy Recommendations
    # -----------------------------
    positive_candidates = []
    for h in holdings:
        ticker = h["ticker"]
        current_price = prices.get(ticker)
        if not current_price:
            continue

        perf = get_stock_performance(ticker, period="1mo")
        if perf and perf["pct_change"] > 0:
            positive_candidates.append((ticker, perf["pct_change"]))

    # Allocate cash proportionally to performance using the shared helper
    buy_recs = allocate_cash_weighted_by_performance(
        positive_candidates, prices, cash_balance, headlines
    )
    recommendations["buy"].extend(buy_recs)

    # Fallback buy: QQQ if significant cash remains
    if cash_balance > 500:
        price = prices.get("QQQ")
        if price and price > 0:
            shares = round(cash_balance / price, 3)
            if shares > 0:
                recommendations["buy"].append({
                    "ticker": "QQQ",
                    "shares": shares,
                    "cost_usd": round(shares * price, 2),
                    "reason": "Tech sector momentum placeholder"
                })

    return recommendations, headlines, prices


def analyze_starter(account_data):
    cash_balance = account_data.get("cash_balance", 0.0)
    headlines = {}
    recommendations = {"buy": [], "sell": []}

    prices = get_prices(STARTER_STOCKS)

    # Collect positive candidates with clean news
    candidates = []
    for ticker in STARTER_STOCKS:
        raw_headlines = get_company_news(ticker)
        headlines[ticker] = raw_headlines
        titles = [h.get("title", "") for h in raw_headlines]

        if contains_negative_news(titles):
            print(f"Skipping {ticker} due to negative news")
            continue

        perf = get_stock_performance(ticker, period="1mo")
        if perf and perf["pct_change"] > 0:
            candidates.append((ticker, perf["pct_change"]))

    # Allocate cash using the shared helper
    recommendations["buy"] = allocate_cash_weighted_by_performance(
        candidates, prices, cash_balance, headlines
    )

    return recommendations, headlines, prices


def allocate_cash_weighted_by_performance(candidates, prices, cash_balance, headlines):
    """
    candidates: list of tuples (ticker, perf_score)
    prices: dict of current prices {ticker: price}
    cash_balance: float
    headlines: dict to store news {ticker: headlines_list}

    Returns: list of buy recommendations
    """
    recommendations = []
    total_score = sum(score for _, score in candidates)
    if total_score == 0:
        return recommendations

    for ticker, score in candidates:
        weight = score / total_score
        cash_for_stock = cash_balance * weight
        price = prices.get(ticker)
        if price and price > 0:
            shares_to_buy = round(cash_for_stock / price, 3)
            if shares_to_buy > 0:
                recommendations.append({
                    "ticker": ticker,
                    "shares": shares_to_buy,
                    "cost_usd": round(shares_to_buy * price, 2),
                    "reason": f"Performance-weighted buy, up {score:.2f}% last month"
                })
    return recommendations


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
        for buy in recommendations["buy"]:
            ticker = buy["ticker"]
            cost_str = f"${buy['cost_usd']:.2f}" if "cost_usd" in buy else "N/A"
            print(f" - Buy {buy['shares']} shares of {ticker} for {cost_str} ({buy['reason']})")
            if ticker in headlines:
                print("   Headlines:")
                for headline in headlines[ticker]:
                    if isinstance(headline, dict):
                        print(f"     * {headline.get('title', headline)}")
                    else:
                        print(f"     * {headline}")
    else:
        print("\nNo buy recommendations.")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    run_advisor()
