from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_prices(prices):
    prompt = (
        f"Here are today's stock prices: {prices}.\n"
        "Give me a short, insightful analysis of what might be going on in the market today."
    )

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    from fetch_prices import get_stock_prices
    from config import TICKERS
    prices = get_stock_prices(TICKERS)
    print(analyze_prices(prices))

