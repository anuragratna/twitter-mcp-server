"""
Twitter Market Sentiment MCP Server
Provides financial market sentiment analysis through Twitter data
"""

from fastapi import FastAPI, HTTPException, APIRouter
from textblob import TextBlob
import tweepy
from tweepy import errors as tweepy_errors
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from collections import Counter
import re
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize FastAPI app with Smithery-compatible configuration
app = FastAPI(
    title="Twitter Market Sentiment MCP",
    description="Financial market sentiment analysis using Twitter data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize MCP router with tags for better documentation
mcp = APIRouter(
    prefix="/mcp",
    tags=["Market Sentiment Analysis"]
)

# Twitter API setup
client = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)

# Pydantic models
class MarketSentimentRequest(BaseModel):
    symbol: str  # Stock symbol (e.g., "AAPL", "TSLA")
    lookback_hours: Optional[int] = 24

class MarketSentimentResponse(BaseModel):
    symbol: str
    sentiment_score: float
    sentiment_label: str
    tweet_count: int
    common_topics: List[str]
    price_mentions: Dict[str, int]  # Price points mentioned in tweets
    bullish_ratio: float  # Ratio of bullish to bearish tweets

class TrendAnalysisRequest(BaseModel):
    symbols: List[str]
    hours: Optional[int] = 24
    min_tweets: Optional[int] = 50

class TrendAnalysisResponse(BaseModel):
    market_insights: Dict[str, Dict]
    sector_sentiment: str
    correlated_topics: List[str]
    market_mood: str

class MarketMonitorRequest(BaseModel):
    watchlist: List[str]  # List of stock symbols to monitor
    timeframe_hours: Optional[int] = 1

class MarketMonitorResponse(BaseModel):
    symbols: List[str]
    sentiment_by_symbol: Dict[str, float]
    overall_market_sentiment: str
    trending_topics: List[str]
    price_sentiment_correlation: Dict[str, float]

def extract_price_mentions(texts: List[str]) -> Dict[str, int]:
    """Extract price mentions from tweets using regex"""
    price_pattern = r'\$\d+\.?\d*|\d+\.?\d*\$'
    prices = []
    for text in texts:
        matches = re.findall(price_pattern, text)
        prices.extend(matches)
    return Counter(prices)

def calculate_bullish_ratio(texts: List[str]) -> float:
    """Calculate ratio of bullish to bearish tweets"""
    bullish_count = 0
    bearish_count = 0
    bullish_words = {'buy', 'bull', 'long', 'up', 'calls', 'moon', 'higher'}
    bearish_words = {'sell', 'bear', 'short', 'down', 'puts', 'crash', 'lower'}
    
    for text in texts:
        text_lower = text.lower()
        if any(word in text_lower for word in bullish_words):
            bullish_count += 1
        if any(word in text_lower for word in bearish_words):
            bearish_count += 1
    
    total = bullish_count + bearish_count
    return bullish_count / total if total > 0 else 0.5

def extract_market_topics(texts: List[str], max_topics: int = 5) -> List[str]:
    """Extract key market-related topics from tweets"""
    combined_text = " ".join(texts)
    blob = TextBlob(combined_text)
    # Filter for finance-related phrases
    finance_phrases = [phrase for phrase in blob.noun_phrases 
                      if any(term in phrase for term in ['market', 'stock', 'trade', 'price', 'investor'])]
    return sorted(set(finance_phrases), key=lambda x: len(x), reverse=True)[:max_topics]

@mcp.get("/capabilities")
async def get_capabilities():
    return {
        "capabilities": [
            {
                "name": "analyze_market_sentiment",
                "description": "Analyze sentiment for a specific stock symbol",
                "input_schema": MarketSentimentRequest.schema(),
                "output_schema": MarketSentimentResponse.schema()
            },
            {
                "name": "analyze_market_trends",
                "description": "Analyze trends across multiple stocks",
                "input_schema": TrendAnalysisRequest.schema(),
                "output_schema": TrendAnalysisResponse.schema()
            },
            {
                "name": "monitor_market",
                "description": "Real-time market sentiment monitoring",
                "input_schema": MarketMonitorRequest.schema(),
                "output_schema": MarketMonitorResponse.schema()
            }
        ]
    }

@mcp.post("/analyze_market_sentiment")
async def analyze_market_sentiment(request: MarketSentimentRequest) -> MarketSentimentResponse:
    try:
        # Get tweets about the stock symbol using v2 API
        search_query = f"symbol:{request.symbol} OR #{request.symbol} lang:en -is:retweet"
        tweets = client.search_recent_tweets(
            query=search_query,
            max_results=100,
            tweet_fields=['created_at', 'public_metrics']
        )
        
        if not tweets.data:
            return MarketSentimentResponse(
                symbol=request.symbol,
                sentiment_score=0,
                sentiment_label="neutral",
                tweet_count=0,
                common_topics=[],
                price_mentions={},
                bullish_ratio=0.5
            )
        
        # Analyze sentiment
        texts = [tweet.text for tweet in tweets.data]
        sentiments = [TextBlob(text).sentiment.polarity for text in texts]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        # Determine sentiment label
        if avg_sentiment > 0.1:
            label = "bullish"
        elif avg_sentiment < -0.1:
            label = "bearish"
        else:
            label = "neutral"
        
        # Extract additional market insights
        price_mentions = extract_price_mentions(texts)
        bullish_ratio = calculate_bullish_ratio(texts)
        market_topics = extract_market_topics(texts)
            
        return MarketSentimentResponse(
            symbol=request.symbol,
            sentiment_score=avg_sentiment,
            sentiment_label=label,
            tweet_count=len(texts),
            common_topics=market_topics,
            price_mentions=price_mentions,
            bullish_ratio=bullish_ratio
        )
    except (tweepy_errors.Forbidden, tweepy_errors.Unauthorized) as e:
        raise HTTPException(
            status_code=403,
            detail=f"Twitter API access denied. Please check your API access level and credentials. Error: {str(e)}"
        )
    except tweepy_errors.TooManyRequests as e:
        raise HTTPException(
            status_code=429,
            detail="Twitter API rate limit exceeded. Please try again later."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@mcp.post("/analyze_market_trends")
async def analyze_market_trends(request: TrendAnalysisRequest) -> TrendAnalysisResponse:
    try:
        market_insights = {}
        all_topics = []
        total_sentiment = 0
        
        for symbol in request.symbols:
            # Get tweets for each symbol
            search_query = f"${symbol} OR #{symbol} lang:en -is:retweet"
            tweets = client.search_recent_tweets(
                query=search_query,
                max_results=request.min_tweets,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            texts = [tweet.text for tweet in tweets.data]
            sentiments = [TextBlob(text).sentiment.polarity for text in texts]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Get market topics and price mentions
            market_topics = extract_market_topics(texts)
            all_topics.extend(market_topics)
            price_mentions = extract_price_mentions(texts)
            bullish_ratio = calculate_bullish_ratio(texts)
            
            # Store insights for this symbol
            market_insights[symbol] = {
                "sentiment_score": avg_sentiment,
                "tweet_count": len(texts),
                "price_mentions": price_mentions,
                "bullish_ratio": bullish_ratio
            }
            
            total_sentiment += avg_sentiment
        
        # Calculate overall market mood
        avg_market_sentiment = total_sentiment / len(request.symbols)
        market_mood = "bullish" if avg_market_sentiment > 0.1 else "bearish" if avg_market_sentiment < -0.1 else "neutral"
        
        # Find correlated topics across symbols
        correlated_topics = [topic for topic, count in Counter(all_topics).most_common(5)]
        
        return TrendAnalysisResponse(
            market_insights=market_insights,
            sector_sentiment=market_mood,
            correlated_topics=correlated_topics,
            market_mood=market_mood
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@mcp.post("/monitor_market")
async def monitor_market(request: MarketMonitorRequest) -> MarketMonitorResponse:
    try:
        sentiment_by_symbol = {}
        all_texts = []
        
        for symbol in request.watchlist:
            # Get recent tweets for each symbol
            search_query = f"${symbol} OR #{symbol} lang:en -is:retweet"
            tweets = client.search_recent_tweets(
                query=search_query,
                max_results=50,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            texts = [tweet.text for tweet in tweets.data]
            all_texts.extend(texts)
            
            # Calculate sentiment for this symbol
            sentiments = [TextBlob(text).sentiment.polarity for text in texts]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            sentiment_by_symbol[symbol] = avg_sentiment
        
        # Calculate overall market sentiment
        overall_sentiment = sum(sentiment_by_symbol.values()) / len(sentiment_by_symbol)
        overall_label = "bullish" if overall_sentiment > 0.1 else "bearish" if overall_sentiment < -0.1 else "neutral"
        
        # Get trending topics across all symbols
        trending_topics = extract_market_topics(all_texts)
        
        # Calculate price-sentiment correlation
        price_sentiment = {}
        for symbol in request.watchlist:
            price_mentions = extract_price_mentions([t for t in all_texts if symbol in t])
            if price_mentions:
                avg_price = sum(float(p.strip('$')) for p in price_mentions.keys()) / len(price_mentions)
                price_sentiment[symbol] = {
                    'avg_mentioned_price': avg_price,
                    'sentiment_correlation': sentiment_by_symbol[symbol]
                }
        
        return MarketMonitorResponse(
            symbols=request.watchlist,
            sentiment_by_symbol=sentiment_by_symbol,
            overall_market_sentiment=overall_label,
            trending_topics=trending_topics,
            price_sentiment_correlation=price_sentiment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint (required by Smithery)
@app.get("/health")
async def health_check():
    """Health check endpoint for Smithery"""
    return {"status": "healthy"}

# Root endpoint redirects to docs
@app.get("/")
async def root():
    """Redirect root to documentation"""
    return {"message": "Welcome to Twitter Market Sentiment MCP", "docs_url": "/docs"}

# Include the MCP router
app.include_router(mcp) 