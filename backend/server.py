import yfinance as yf
import requests
from textblob import TextBlob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

def fetch_stock_data(symbols):
    data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        history = ticker.history(period="1d")
        data[sym] = history['Close'].iloc[-1]
    return data

def fetch_news_headlines(query):
    api_key = "46dab4f78b084ffa878da8cdeb882943"
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get('articles', [])
        return [article['title'] for article in articles]
    return []

def analyze_news_sentiments(headlines):
    total_sentiment = 0
    for headline in headlines:
        total_sentiment += TextBlob(headline).sentiment.polarity
    return total_sentiment / len(headlines) if headlines else 0

def generate_recommendations(buying_power, portfolio, stock_data, sentiment):
    recommendations = {'buy': [], 'sell': []}
    for stock, price in stock_data.items():
        if sentiment > 0.1 and stock not in portfolio and buying_power >= price:
            recommendations['buy'].append({'stock': stock, 'price': price})
        elif stock in portfolio and sentiment < -0.1:
            recommendations['sell'].append({'stock': stock, 'price': price})
            
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
    stock_symbols = ["AAPL", "GOOGL", "AMZN", "MSFT", "TSLA"]
    stock_data = fetch_stock_data(stock_symbols)
    headlines = fetch_news_headlines(user_input.news_query)
    sentiment = analyze_news_sentiments(headlines)
    recommentations = generate_recommendations(
        user_input.buying_power, user_input.portfolio, stock_data, sentiment
    )
    return recommentations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)