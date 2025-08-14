# Chatty G Goes to the Market



# Buy Recommendation Idea
1️⃣ Core Idea

For each stock, fetch its recent performance (pct_change) over the last month (or configurable period).

Filter out stocks with negative news or negative/no performance.

Normalize the positive performance values to get a “weight” for each stock:

weighti=pct_changei∑pct_changeall_stocks
weight
i
	​

=
∑pct_change
all_stocks
	​

pct_change
i
	​

	​


Allocate cash proportionally: cash_for_stock = cash_balance * weight_i

Buy fractional shares: shares = round(cash_for_stock / price, 3)



## TODOS

1. News Integration
	* Ensure headlines are printed properly in logs and recommendations.
	* Possibly include a summary or sentiment score for each ticker in recommendations.

2. Buy Strategy
	* Implement dynamic allocation based on performance weighting for both starter stocks and existing holdings (we discussed earlier, may already be partially implemented).
	* Decide if there’s a cap per stock or max % of portfolio.

3. Sell Strategy
	* Possibly refine sell thresholds (e.g., based on volatility, news sentiment, or performance over multiple timeframes).

4. Portfolio Metrics
	* Track total portfolio value and cash balance daily.
	* Calculate and log unrealized gains/losses.

5. Error Handling / Robustness
	* Handle tickers with missing or NaN price data.
	* Retry fetching prices or news if APIs fail.

6. Scheduling / Automation
	* Make it easy to run run_advisor() multiple times a day.
	* Possibly implement daily/weekly summary reports.

7. User Input / Configuration
	* Allow users to adjust starter stocks, cash allocation strategy, and buy/sell thresholds.
	* Support switching between CSV and API-based account data ingestion in the future.

8. Testing
	* Add unit tests for CSV conversion, buy/sell logic, and news filtering.
