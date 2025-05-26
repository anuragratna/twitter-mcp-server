"""
Twitter MCP Service
Provides Twitter functionality through MCP tools including tweeting,
sentiment analysis, and tweet deletion.
"""

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import tweepy
from textblob import TextBlob
import os
from dotenv import load_dotenv
import nltk

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
    
    def __init__(self):
        settings = Settings()
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