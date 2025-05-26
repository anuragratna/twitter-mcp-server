"""
Test environment variables and Twitter API connection
"""

import os
from dotenv import load_dotenv
import tweepy
from typing import Dict

def test_env_variables() -> Dict[str, bool]:
    """Test if all required environment variables are set"""
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    
    results = {}
    for var in required_vars:
        value = os.getenv(var)
        results[var] = value is not None and len(value) > 0
    
    return results

def test_twitter_connection() -> Dict[str, bool]:
    """Test Twitter API connection"""
    try:
        auth = tweepy.OAuthHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET")
        )
        auth.set_access_token(
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        api = tweepy.API(auth)
        api.verify_credentials()
        
        return {
            "auth_success": True,
            "api_connection": True
        }
    except Exception as e:
        return {
            "auth_success": False,
            "api_connection": False,
            "error": str(e)
        }

def main():
    print("Loading environment variables...")
    load_dotenv()
    
    print("\nTesting environment variables:")
    env_results = test_env_variables()
    for var, exists in env_results.items():
        status = "✅" if exists else "❌"
        print(f"{status} {var}")
    
    if all(env_results.values()):
        print("\nTesting Twitter API connection:")
        api_results = test_twitter_connection()
        
        if api_results.get("auth_success"):
            print("✅ Authentication successful")
            print("✅ API connection established")
        else:
            print("❌ Twitter API connection failed")
            print(f"Error: {api_results.get('error', 'Unknown error')}")
    else:
        print("\n❌ Environment variables missing. Please set them in .env file")
        print("\nRequired format:")
        print("""
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
        """)

if __name__ == "__main__":
    main() 