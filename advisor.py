import json
import os
import datetime
import yfinance as yf
from typing import Dict, Any


LOGS_DIR = "logs"


def run_advisor(account_data: Dict[str, Any]):
    """
    Main advisor function — runs an analysis on current holdings and
    outputs buy/sell recommendations with reasoning.
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOGS_DIR, f"advisor_{timestamp}.json")

    holdings = account_data.get("holdings", [])
    cash_balance = account_data.get("cash_balance", 0.0)

    # Get live market prices for current holdings
    tickers = [h["ticker"] for h in holdings]
    market_data = {}
    if tickers:
        prices = yf.download(tickers=tickers, period="1d", interval="1m")["Close"].iloc[
            -1
        ]
        for ticker in tickers:
            market_data[ticker] = float(prices[ticker]) if ticker in prices else None

    # Placeholder: Get news headlines for each holding
    headlines = {}
    for ticker in tickers:
        headlines[ticker] = [
            # TODO: Hook into your get_company_news() here
            f"Sample headline for {ticker} at {timestamp}"
        ]

    # Placeholder decision logic
    recommendations = {"buy": [], "sell": []}

    for h in holdings:
        ticker = h["ticker"]
        avg_price = h["avg_price"]
        current_price = market_data.get(ticker)

        if current_price is None:
            continue

        change_pct = ((current_price - avg_price) / avg_price) * 100

        # Sell rule: drop > 5%
        if change_pct <= -5:
            recommendations["sell"].append(
                {"ticker": ticker, "reason": f"Down {change_pct:.2f}% from avg price"}
            )

    # Example buy placeholder — just adds a tech ETF if we have cash
    if cash_balance > 500:
        recommendations["buy"].append(
            {"ticker": "QQQ", "reason": "Tech sector momentum placeholder"}
        )

    # Log everything
    log_data = {
        "log_timestamp": timestamp,
        "holdings": holdings,
        "cash_balance": cash_balance,
        "market_data": market_data,
        "headlines": headlines,
        "recommendations": recommendations,
    }

    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)

    print(json.dumps(log_data, indent=2))
    return log_data


# Example usage
if __name__ == "__main__":
    # Sample daily account data
    account_data_example = {
        "cash_balance": 12000.50,
        "holdings": [
            {"ticker": "AAPL", "shares": 20, "avg_price": 175.30},
            {"ticker": "SPY", "shares": 10, "avg_price": 510.00},
        ],
    }

    run_advisor(account_data_example)

    # Path to account file
    account_file = "account.json"

    # Make sure the file exists
    if not os.path.exists(account_file):
        raise FileNotFoundError(f"Account file '{account_file}' not found. Please create it.")

    # Read account data from JSON
    with open(account_file, "r") as f:
        account_data = json.load(f)

    # Run the advisor with provided data
    run_advisor(account_data)
