"""
Twitter Market MCP Service
Combines Twitter sentiment analysis with market data
"""

import yfinance as yf
from textblob import TextBlob
import logging
from typing import Dict, Any, Optional
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterMarketMCP:
    """Service for analyzing market sentiment using Twitter data and stock information."""
    
    def __init__(self, cache_duration: int = 3600):
        self.cache = {}
        self.cache_duration = cache_duration

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text using TextBlob."""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0

    def get_cached_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached sentiment if available and not expired."""
        if symbol in self.cache:
            cache_entry = self.cache[symbol]
            if time.time() - cache_entry['timestamp'] < self.cache_duration:
                return cache_entry['data']
        return None

    def cache_sentiment(self, symbol: str, sentiment_data: Dict[str, Any]):
        """Cache sentiment data for a symbol."""
        try:
            self.cache[symbol] = {
                'timestamp': time.time(),
                'data': sentiment_data
            }
            
            # Clean up old cache entries
            now = time.time()
            expired_keys = [
                k for k, v in self.cache.items()
                if now - v['timestamp'] > self.cache_duration
            ]
            for k in expired_keys:
                del self.cache[k]
        except Exception as e:
            logger.error(f"Error caching sentiment: {e}")

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get stock information and recent price history."""
        stock = yf.Ticker(symbol)
        info = stock.info
        history = stock.history(period="1mo")
        
        if history.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        
        current_price = history['Close'].iloc[-1]
        price_change = history['Close'].iloc[-1] - history['Close'].iloc[-2]
        price_change_pct = (price_change / history['Close'].iloc[-2]) * 100
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "company_name": info.get('longName', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "market_cap": info.get('marketCap', 0)
        }

    async def analyze_market_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze market sentiment for a stock using price data and news sentiment."""
        # Check cache first
        cached_result = self.get_cached_sentiment(symbol)
        if cached_result:
            return cached_result

        # Get stock data
        stock = yf.Ticker(symbol)
        history = stock.history(period="1mo")
        news = stock.news
        
        if history.empty:
            raise ValueError(f"No data found for symbol {symbol}")
        
        # Calculate technical indicators
        price_trend = "upward" if history['Close'].iloc[-1] > history['Close'].mean() else "downward"
        volatility = history['Close'].std() / history['Close'].mean() * 100
        
        # Analyze news sentiment
        sentiments = []
        news_items = []
        for article in news[:10]:  # Analyze up to 10 recent news articles
            sentiment = self.analyze_sentiment(article.get('title', ''))
            sentiments.append(sentiment)
            news_items.append({
                "title": article.get('title'),
                "link": article.get('link'),
                "sentiment": sentiment
            })
        
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        sentiment_label = "positive" if avg_sentiment > 0 else "negative" if avg_sentiment < 0 else "neutral"
        
        result = {
            "symbol": symbol,
            "price_trend": price_trend,
            "volatility": volatility,
            "sentiment": {
                "label": sentiment_label,
                "score": avg_sentiment
            },
            "news_analysis": news_items,
            "overall_assessment": "",
            "timestamp": datetime.now().isoformat()
        }
        
        if avg_sentiment > 0.2 and price_trend == "upward":
            result["overall_assessment"] = "Strong bullish sentiment with positive momentum"
        elif avg_sentiment > 0 and price_trend == "upward":
            result["overall_assessment"] = "Moderately bullish sentiment"
        elif avg_sentiment < -0.2 and price_trend == "downward":
            result["overall_assessment"] = "Strong bearish sentiment with negative momentum"
        elif avg_sentiment < 0 and price_trend == "downward":
            result["overall_assessment"] = "Moderately bearish sentiment"
        else:
            result["overall_assessment"] = "Mixed or neutral market sentiment"
        
        # Cache the results
        self.cache_sentiment(symbol, result)
        
        return result 