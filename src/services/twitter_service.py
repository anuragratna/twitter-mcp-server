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
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Configuration settings for the Twitter service."""
    twitter_api_key: Optional[str] = os.getenv("TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = os.getenv("TWITTER_API_SECRET")
    twitter_access_token: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    class Config:
        env_file = ".env"

    def validate_credentials(self) -> bool:
        """Check if all required credentials are present."""
        return all([
            self.twitter_api_key,
            self.twitter_api_secret,
            self.twitter_access_token,
            self.twitter_access_token_secret
        ])

class TwitterService:
    """
    Service class for handling Twitter operations.
    Provides methods for tweeting, deleting tweets, and sentiment analysis.
    """
    
    def __init__(self):
        self.settings = Settings()
        if not self.settings.validate_credentials():
            logger.warning("Twitter credentials not fully configured. Some features may be limited to sentiment analysis only.")
            self.api = None
        else:
            try:
                self.auth = tweepy.OAuthHandler(
                    self.settings.twitter_api_key,
                    self.settings.twitter_api_secret
                )
                self.auth.set_access_token(
                    self.settings.twitter_access_token,
                    self.settings.twitter_access_token_secret
                )
                self.api = tweepy.API(self.auth)
                self.api.verify_credentials()
                logger.info("Twitter API initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twitter API: {str(e)}")
                self.api = None

    def _check_api(self):
        """Check if Twitter API is available."""
        if not self.api:
            raise HTTPException(
                status_code=503,
                detail="Twitter API not available. Please check your credentials and try again."
            )

    async def create_tweet(self, text: str) -> Dict[str, Any]:
        """Create a new tweet."""
        self._check_api()
        try:
            tweet = self.api.update_status(text)
            return {
                "id": str(tweet.id),
                "text": tweet.text
            }
        except tweepy.TweepError as e:
            logger.error(f"Failed to create tweet: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating tweet: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def delete_tweet(self, tweet_id: str) -> Dict[str, str]:
        """Delete a tweet by ID."""
        self._check_api()
        try:
            self.api.destroy_status(tweet_id)
            return {"message": f"Tweet {tweet_id} deleted successfully"}
        except tweepy.TweepError as e:
            logger.error(f"Failed to delete tweet {tweet_id}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error deleting tweet {tweet_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

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
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to analyze sentiment") 