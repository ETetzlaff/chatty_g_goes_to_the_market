from openai import OpenAI
from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_prices(prices):
    prompt = (
        f"""
Here are today's stock prices: {prices}.\n"
"Give me a short, insightful analysis of what might be going on in the market today."
        """
    )

    response = client.chat.completions.create(
        # model="gpt-5",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


def analyze_market(prices, top_ticker, headlines):
    headline_text = "\n".join(
        [f"- {h['title']} ({h['link']})" for h in headlines]
    ) if headlines else "No recent news found."

    prompt = (
        f"Here are today's stock prices and daily % changes: {prices}.\n"
        f"The top performer is {top_ticker}.\n"
        f"Here are the latest headlines for {top_ticker}:\n{headline_text}\n\n"
        "Provide a short but insightful analysis of what might be happening in the market today, "
        "and why the top performer is doing well."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from fetch_prices import get_stock_prices
    from config import TICKERS
    prices = get_stock_prices(TICKERS)
    print(analyze_prices(prices))
