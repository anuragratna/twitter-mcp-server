"""
Twitter MCP Service
Provides Twitter functionality through MCP tools including tweeting,
sentiment analysis, and tweet deletion.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import tweepy
from textblob import TextBlob
import os
from dotenv import load_dotenv
import nltk
from .. import mcp

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Configuration settings for the Twitter service."""
    twitter_api_key: str = os.getenv("TWITTER_API_KEY")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    class Config:
        env_file = ".env"

class TwitterService:
    """
    Service class for handling Twitter operations.
    Provides methods for tweeting, deleting tweets, and sentiment analysis.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.auth = tweepy.OAuthHandler(
            settings.twitter_api_key,
            settings.twitter_api_secret
        )
        self.auth.set_access_token(
            settings.twitter_access_token,
            settings.twitter_access_token_secret
        )
        self.api = tweepy.API(self.auth)

    async def create_tweet(self, text: str) -> Dict[str, Any]:
        """Create a new tweet."""
        try:
            tweet = self.api.update_status(text)
            return {
                "id": str(tweet.id),
                "text": tweet.text
            }
        except tweepy.TweepError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def delete_tweet(self, tweet_id: str) -> Dict[str, str]:
        """Delete a tweet by ID."""
        try:
            self.api.destroy_status(tweet_id)
            return {"message": f"Tweet {tweet_id} deleted successfully"}
        except tweepy.TweepError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze text sentiment."""
        try:
            analysis = TextBlob(text)
            
            if analysis.sentiment.polarity > 0:
                sentiment = "positive"
            elif analysis.sentiment.polarity < 0:
                sentiment = "negative"
            else:
                sentiment = "neutral"
                
            return {
                "text": text,
                "sentiment": sentiment,
                "polarity": analysis.sentiment.polarity,
                "subjectivity": analysis.sentiment.subjectivity
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

# Initialize settings and service
settings = Settings()
twitter_service = TwitterService(settings)

# Initialize FastAPI and MCP Tool Registry
app = FastAPI(title="Twitter MCP Server")

@mcp.tool(
    name="twitter.tweet",
    description="Create a new tweet with the given text",
    parameters={
        "text": {
            "type": "string",
            "description": "The text content of the tweet"
        }
    },
    returns={
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "text": {"type": "string"}
        }
    }
)
async def create_tweet(text: str) -> Dict[str, Any]:
    """Create a new tweet with the given text."""
    return await twitter_service.create_tweet(text)

@mcp.tool(
    name="twitter.delete_tweet",
    description="Delete a tweet by its ID",
    parameters={
        "tweet_id": {
            "type": "string",
            "description": "The ID of the tweet to delete"
        }
    },
    returns={
        "type": "object",
        "properties": {
            "message": {"type": "string"}
        }
    }
)
async def delete_tweet(tweet_id: str) -> Dict[str, str]:
    """Delete a tweet by its ID."""
    return await twitter_service.delete_tweet(tweet_id)

@mcp.tool(
    name="twitter.analyze_sentiment",
    description="Analyze the sentiment of the given text",
    parameters={
        "text": {
            "type": "string",
            "description": "The text to analyze for sentiment"
        }
    },
    returns={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "sentiment": {"type": "string"},
            "polarity": {"type": "number"},
            "subjectivity": {"type": "number"}
        }
    }
)
async def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze the sentiment of the given text."""
    return await twitter_service.analyze_sentiment(text)

# Add FastAPI routes for the MCP tools
app.include_router(mcp.router)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "message": "Twitter MCP Server is running",
        "tools": ["twitter.tweet", "twitter.delete_tweet", "twitter.analyze_sentiment"]
    } 