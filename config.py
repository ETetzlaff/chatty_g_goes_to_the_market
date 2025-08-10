import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file if present

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TICKERS = ["VOO", "VTI", "AAPLE", "GOOGL", "AAPL", "NVDA", "AMZN", "MSFT"]
