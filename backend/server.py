import yfinance as yf
import requests
from textblob import TextBlob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_stock_data(symbols):
    data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        history = ticker.history(period="1d")
        data[sym] = history['Close'].iloc[-1]
    print(data)
    return data

def fetch_company_names(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.info['longName']

def fetch_news_headlines(query):
    if not query:
        query = "US stocks"
    api_key = os.getenv('NEWS_API_KEY')
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        # print("Articles:", articles)
        return [article['title'] for article in articles]
    return []

def analyze_news_sentiments(headlines):
    total_sentiment = 0
    for headline in headlines:
        total_sentiment += TextBlob(headline).sentiment.polarity
    
    sentiment = total_sentiment / len(headlines) if headlines else 0
    print(f"Sentiment: {sentiment}")
    return total_sentiment / len(headlines) if headlines else 0

def generate_recommendations(buying_power, portfolio, stock_data, sentiment):
    recommendations = {'buy': [], 'sell': []}
    print("Stock_data:", stock_data)
    for stock, price in stock_data.items():
        print("Stock:", stock)
        print("Price:", price)
        print(sentiment)
        if sentiment > 0.1 and stock not in portfolio.keys() and float(buying_power) >= price:
            recommendations['buy'].append({'stock': stock, 'price': price})
        elif stock in portfolio.keys() and sentiment < -0.1:
            recommendations['sell'].append({'stock': stock, 'price': price})
            
    print("recommendations:", recommendations)
    return recommendations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    buying_power: float
    portfolio: dict
    news_query: str = "US stocks"
    
    
@app.post("/recommend")
async def recommend_stocks(user_input: UserInput):
    print(user_input)
    stock_symbols = user_input.portfolio
    stock_data = fetch_stock_data(stock_symbols)
    headlines = fetch_news_headlines(user_input.news_query)
    sentiment = analyze_news_sentiments(headlines)
    print("sentiment:", sentiment)
    recommendations = generate_recommendations(
        user_input.buying_power, user_input.portfolio, stock_data, sentiment
    )
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)