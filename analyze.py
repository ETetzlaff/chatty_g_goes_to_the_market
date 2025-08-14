from openai import OpenAI
from config import OPENAI_API_KEY
import json
import re


client = OpenAI(api_key=OPENAI_API_KEY)


def analyze_prices(prices):
    prompt = f"""
Here are today's stock prices: {prices}.\n"
"Give me a short, insightful analysis of what might be going on in the market today."
        """

    response = client.chat.completions.create(
        # model="gpt-5",
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content


def analyze_market(prices, top_ticker, headlines):
    headline_text = (
        "\n".join([f"- {h['title']} ({h['link']})" for h in headlines])
        if headlines
        else "No recent news found."
    )

    prompt = (
        f"Here are today's stock prices and daily % changes: {prices}.\n"
        f"The top performer is {top_ticker}.\n"
        f"Here are the latest headlines for {top_ticker}:\n{headline_text}\n\n"
        "Provide a short but insightful analysis of what might be happening in the market today, "
        "and why the top performer is doing well."
    )

    response = client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}], temperature=0.7
    )

    return response.choices[0].message.content


def suggest_high_performing_tickers(preferred_universe=None, exclude=None, max_count=5):
    """
    Ask GPT for a list of currently high-performing, liquid US-listed tickers.

    preferred_universe: optional hint list of tickers to prioritize
    exclude: tickers to avoid suggesting (e.g., already in holdings)
    max_count: maximum number of tickers to return

    Returns: list of ticker strings (uppercased)
    """
    exclude = exclude or []
    preferred_universe = preferred_universe or []

    instructions = (
        "Return ONLY a JSON object like {\"tickers\":[\"AAPL\",\"MSFT\"]} with up to "
        f"{max_count} large/mega-cap, liquid US-listed stocks that have shown strong recent momentum. "
        "Avoid micro-caps and illiquid names. Prefer household names if unsure. "
        "If a preferred universe is provided, prioritize from it. Exclude any tickers in the exclude list. "
        "Do not include commentary or extra keys."
    )

    payload = {
        "preferred_universe": preferred_universe,
        "exclude": exclude,
        "max_count": max_count,
    }

    prompt = (
        f"Instructions: {instructions}\n"
        f"Preferred universe: {preferred_universe}\n"
        f"Exclude: {exclude}\n"
        f"Max: {max_count}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    text = response.choices[0].message.content or ""

    # Try strict JSON parsing first
    tickers = []
    try:
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("tickers"), list):
            tickers = [str(t).upper() for t in data["tickers"]]
    except Exception:
        # Fallback: extract plausible tickers (1-5 uppercase letters) from text
        tickers = re.findall(r"\b[A-Z]{1,5}\b", text)

    # De-duplicate and filter excluded
    seen = set()
    result = []
    for t in tickers:
        if t in seen or t in (exclude or []):
            continue
        seen.add(t)
        result.append(t)
        if len(result) >= max_count:
            break

    return result


if __name__ == "__main__":
    from fetch_prices import get_stock_prices
    from config import TICKERS

    prices = get_stock_prices(TICKERS)
    print(analyze_prices(prices))
