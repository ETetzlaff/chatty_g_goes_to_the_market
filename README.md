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
