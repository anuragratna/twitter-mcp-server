import tweepy
import os
from dotenv import load_dotenv

def test_twitter_credentials():
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    print("Testing Twitter API credentials...")
    
    try:
        # Initialize client
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Test API access with a simple search
        print("\nTesting search endpoint...")
        tweets = client.search_recent_tweets(
            query="test",
            max_results=10
        )
        print("✓ Search endpoint working")
        
        # Get API v2 rate limit status
        print("\nChecking rate limits...")
        response = client.get_me()
        print("✓ Authentication successful")
        print(f"Username: {response.data.username}")
        print(f"Account ID: {response.data.id}")
        
        return True
        
    except tweepy.errors.TooManyRequests as e:
        print(f"❌ Rate limit exceeded. Reset after: {e.response.headers.get('x-rate-limit-reset', 'unknown')}")
        return False
    except tweepy.errors.Unauthorized as e:
        print("❌ Authentication failed. Invalid credentials.")
        print(f"Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_twitter_credentials() 