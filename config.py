import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()  # loads .env file if present

CSV_FILE = Path("data/schwab_holdings.csv")
JSON_FILE = Path("account.json")
LOGS_DIR = Path("logs")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# TICKERS = ["VOO", "VTI", "AAPLE", "GOOGL", "AAPL", "NVDA", "AMZN", "MSFT"]

TICKERS = ["AAPL", "MSFT", "NVDA", "AMZN", "AMD"]
NEW_TICKERS = [
    # Technology
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "NVDA",  # Nvidia
    "GOOGL",  # Alphabet
    # Financials
    "JPM",  # JPMorgan Chase
    # "BRK.B",  # Berkshire Hathaway
    "V",  # Visa
    # Healthcare
    "JNJ",  # Johnson & Johnson
    "PFE",  # Pfizer
    "UNH",  # UnitedHealth
    # Consumer Discretionary
    "AMZN",  # Amazon
    "TSLA",  # Tesla
    "HD",  # Home Depot
    # Consumer Staples
    "PG",  # Procter & Gamble
    "KO",  # Coca-Cola
    "PEP",  # PepsiCo
    # Energy
    "XOM",  # Exxon Mobil
    "CVX",  # Chevron
    # Industrials
    "BA",  # Boeing
    "CAT",  # Caterpillar
    # Other / Diversifiers
    "GLD",  # SPDR Gold Trust (gold ETF)
    "BTC-USD",  # Bitcoin (USD)
    "SPY",  # S&P 500 ETF
    "VOO",
    "VTI",
    # ETF / Index Funds
    # "VOO",
    # "VTI",
    # "QQQ",
    # "XLF",
    # "XLK",
    # "XLE",
]
