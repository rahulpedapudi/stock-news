import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Globals
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_API_KEY = os.getenv("STOCK_API_KEY")
STOCK_ENDPOINT = f"https://www.alphavantage.co/query?"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_ENDPOINT = "https://newsapi.org/v2/everything?"
TW_AUTH = os.getenv("TW_AUTH")
TW_SID = os.getenv("TW_SID")

fromNum = os.getenv("FROM")
toNum = os.getenv("TO")

# Stock API Call
stock_api_response = requests.get(url=STOCK_ENDPOINT, params={
    "function": "TIME_SERIES_DAILY",
    "symbol": "TSLA",
    "apikey": f"{STOCK_API_KEY}"
})
stock_api_response.raise_for_status()
stock_data = stock_api_response.json()  # Actual data from the response


# News API call
news_api_response = requests.get(url=NEWS_ENDPOINT, params={
    "apiKey": f"{NEWS_API_KEY}",
    "pageSize": 4,
    "q": f"Tesla",
    "language": "en"
})

news_api_response.raise_for_status()
news_data = news_api_response.json()

# Extracting articles from entire news data
news_articles = news_data["articles"]


# function to get stock data for the given date
def get_stock_data(date):
    global stock_data
    close_stock_price = stock_data['Time Series (Daily)'][date]['4. close']
    return close_stock_price


# latest stock data
last_refreshed_date = (stock_data['Meta Data']['3. Last Refreshed'])

# converting string to datatime object
last_refreshed_datetime = datetime.strptime(last_refreshed_date, "%Y-%m-%d")
# slicing the string from yyyy-mm-dd hh-mm-ss to yyyy-mm-dd
previous_date = str(last_refreshed_datetime - timedelta(1))[:10]

# gets latest stock data and previous days stock data
current_stock_price = float(get_stock_data(f"{last_refreshed_date}"))
previous_stock_price = float(get_stock_data(f"{previous_date}"))

print(current_stock_price)
print(previous_stock_price)


# calculating percentage increase or decrease
percentage_change = (
    (current_stock_price - previous_stock_price) / previous_stock_price) * 100
print(f"Percentage Change: {percentage_change:.2f}%")


# checking if the percentage is >= 3, if so sending sms to the phone number
if abs(percentage_change) >= 3:
    message_body = ""
    indicator = "🔺" if percentage_change > 0 else "🔻"
    print(f"\n{COMPANY_NAME}: {indicator} {abs(percentage_change):.2f}%\n\n")
    message_body += (f"{COMPANY_NAME}: {indicator} {abs(percentage_change):.2f}%\n\n")
    for article in news_articles:
        message_body += (
            f"Headline: {article['title']}\nBrief: {article['description']}\n\n")

    client = Client(TW_SID, TW_AUTH)
    message = client.messages.create(
        from_=fromNum, to=toNum, body=f"{message_body}")
    print(message.status)
