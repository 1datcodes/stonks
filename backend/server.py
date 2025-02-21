import os
import yfinance as yf
import requests
from textblob import TextBlob
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()  # ensure your .env file is present with NEWS_API_KEY

def fetch_stock_data(symbols):
    data = {}
    symbols = list(symbols)  # convert dict_keys to list if needed
    for sym in symbols:
        try:
            ticker = yf.Ticker(sym)
            history = ticker.history(period="1d")
            if history.empty:
                print(f"No data available for {sym}")
                continue
            data[sym] = history['Close'].iloc[-1]
        except Exception as e:
            print(f"Error fetching data for {sym}: {e}")
    return data

def fetch_news_headlines(stock):
    # Accept a single stock symbol (or company name) as a string
    query = quote_plus(stock)  # URL encode the stock symbol
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        raise ValueError("NEWS_API_KEY environment variable not found.")
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        headlines = [article.get("title", "No Title") for article in articles]
        return headlines
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def analyze_news_sentiments(headlines):
    if not headlines:
        return 0
    sentiments = [TextBlob(headline).sentiment.polarity for headline in headlines]
    avg_sentiment = sum(sentiments) / len(sentiments)
    return avg_sentiment

def get_stock_sentiment(stock):
    headlines = fetch_news_headlines(stock)
    sentiment = analyze_news_sentiments(headlines)
    return sentiment, headlines

def generate_recommendations_individual(buying_power, portfolio, candidate_stocks):
    recommendations = {'buy': [], 'sell': []}
    stock_data = fetch_stock_data(candidate_stocks)
    sentiments = generate_news_sentiments(portfolio)
    print(stock_data)
    
    for stock in candidate_stocks:
        if stock not in stock_data or stock not in sentiments:
            continue
        sentiment = sentiments[stock]
        if sentiment > 0.1:
            recommendations['buy'].append([stock, stock_data[stock]])
        else:
            if stock in portfolio:
                recommendations['sell'].append(stock)
    return recommendations


def generate_news_sentiments(portfolio):
    sentiments = {}
    for stock in portfolio.keys():
        sentiment, headlines = get_stock_sentiment(stock)
        sentiments[stock] = sentiment
    return sentiments

# FastAPI app setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict origins appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    buying_power: float
    portfolio: dict  # Example: {"AAPL": 10, "TSLA": 5}
    # Optionally, add a field for a candidate watchlist:
    candidate_stocks: list = None

@app.post("/recommend")
async def recommend_stocks(user_input: UserInput):
    print("Received input:", user_input)
    
    # Determine candidate stocks:
    # Either use the provided candidate list or default to portfolio keys (or combine with a broader watchlist)
    if user_input.candidate_stocks:
        candidate_stocks = user_input.candidate_stocks
    else:
        candidate_stocks = list(user_input.portfolio.keys())
    
    recommendations = generate_recommendations_individual(
        user_input.buying_power, user_input.portfolio, candidate_stocks
    )
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
