import csv
import json
from datetime import datetime
from pathlib import Path


# Input & output paths
CSV_FILE = Path("data/schwab_holdings.csv")
OUTPUT_FILE = Path("account.json")


def convert_csv_to_json(csv_file, json_file):
    holdings = []
    cash_balance = 0.0

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

            # Schwab sometimes lists "Cash & Cash Investments" as a pseudo-symbol
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
        "last_updated": datetime.utcnow().isoformat(),
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(account_data, f, indent=2)

    print(f"✅ Converted {csv_file} → {json_file}")


if __name__ == "__main__":
    convert_csv_to_json(CSV_FILE, OUTPUT_FILE)
