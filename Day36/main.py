import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()
# ================= CONFIG =================
STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_NUMBER = "+19129785502"
TO_NUMBER = "+917019095847"

# ================= STOCK DATA =================
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()

data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

# Yesterday closing price
yesterday_data = data_list[0]
yesterday_closing_price = float(yesterday_data["4. close"])

# Day before yesterday closing price
day_before_yesterday_data = data_list[1]
day_before_yesterday_closing_price = float(
    day_before_yesterday_data["4. close"]
)

# ================= PRICE DIFFERENCE =================
difference = (
    yesterday_closing_price -
    day_before_yesterday_closing_price
)

up_down = "🔺" if difference > 0 else "🔻"

diff_percentage = round(
    abs(difference) / day_before_yesterday_closing_price * 100
)

print(f"Difference Percentage: {diff_percentage}%")

# ================= NEWS SECTION =================
if diff_percentage > 1:

    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
        "language": "en",
        "sortBy": "publishedAt",
    }

    news_response = requests.get(
        NEWS_ENDPOINT,
        params=news_params
    )

    news_response.raise_for_status()

    articles = news_response.json()["articles"]

    # First 3 articles
    three_articles = articles[:3]

    # Format articles
    formatted_articles = [
        f"{STOCK_NAME}: {up_down}{diff_percentage}%\n"
        f"Headline: {article['title']}\n"
        f"Brief: {article['description']}"
        for article in three_articles
    ]

    # ================= TWILIO SMS =================
    client = Client(
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN
    )

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_=FROM_NUMBER,
            to=TO_NUMBER,
        )

        print("Message Sent:", message.sid)

else:
    print("Stock movement less than 5% — No news sent.")