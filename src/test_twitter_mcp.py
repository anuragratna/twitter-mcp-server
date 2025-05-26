"""
Test file for Twitter MCP Server
"""
import asyncio
from twitter_mcp import app
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize test client
client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_capabilities():
    response = client.get("/_mcp/capabilities")
    assert response.status_code == 200
    capabilities = response.json()["capabilities"]
    assert len(capabilities) == 5  # Now we have 5 capabilities
    capability_names = [c["name"] for c in capabilities]
    assert "post_tweet" in capability_names
    assert "analyze_sentiment" in capability_names
    assert "analyze_trends" in capability_names
    assert "monitor_keywords" in capability_names
    assert "delete_tweet" in capability_names

def test_post_and_delete_tweet():
    # Post a test tweet
    test_text = "Test tweet from MCP server - will be deleted"
    response = client.post("/_mcp/post_tweet", json={"text": test_text})
    assert response.status_code == 200
    tweet_data = response.json()
    assert tweet_data["text"] == test_text
    
    # Delete the test tweet
    tweet_id = tweet_data["tweet_id"]
    response = client.post("/_mcp/delete_tweet", json={"tweet_id": tweet_id})
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_analyze_sentiment():
    response = client.post("/_mcp/analyze_sentiment", 
                         json={"topic": "#Python", "tweet_count": 10})
    assert response.status_code == 200
    data = response.json()
    
    # Check basic sentiment fields
    assert "sentiment_score" in data
    assert "sentiment_label" in data
    assert data["topic"] == "#Python"
    assert data["tweet_count"] <= 10
    
    # Check new fields
    assert "common_hashtags" in data
    assert "key_phrases" in data
    assert "engagement_stats" in data
    assert isinstance(data["engagement_stats"], dict)
    assert all(k in data["engagement_stats"] for k in ["likes", "retweets", "replies"])

def test_analyze_trends():
    response = client.post("/_mcp/analyze_trends",
                         json={"topics": ["#Python", "#AI"], "min_tweets": 10})
    assert response.status_code == 200
    data = response.json()
    
    # Check trend analysis fields
    assert "topic_insights" in data
    assert "overall_sentiment" in data
    assert "trending_hashtags" in data
    assert "peak_activity_hour" in data
    
    # Check topic insights
    assert "#Python" in data["topic_insights"]
    assert "#AI" in data["topic_insights"]
    for topic_data in data["topic_insights"].values():
        assert "sentiment_score" in topic_data
        assert "tweet_count" in topic_data
        assert "top_hashtags" in topic_data
        assert "engagement" in topic_data

def test_monitor_keywords():
    response = client.post("/_mcp/monitor_keywords",
                         json={"keywords": ["python", "programming"]})
    assert response.status_code == 200
    data = response.json()
    
    # Check monitoring fields
    assert "total_mentions" in data
    assert "sentiment_distribution" in data
    assert "top_influencers" in data
    assert "engagement_metrics" in data
    
    # Check sentiment distribution
    sentiment_dist = data["sentiment_distribution"]
    assert all(k in sentiment_dist for k in ["positive", "neutral", "negative"])
    assert abs(sum(sentiment_dist.values()) - 100) < 0.1  # Should sum to 100%
    
    # Check influencers
    assert len(data["top_influencers"]) <= 5
    for influencer in data["top_influencers"]:
        assert "username" in influencer
        assert "followers" in influencer
        assert "tweet" in influencer

if __name__ == "__main__":
    print("Running tests...")
    test_health_check()
    print("✓ Health check test passed")
    test_capabilities()
    print("✓ Capabilities test passed")
    test_post_and_delete_tweet()
    print("✓ Post and delete tweet test passed")
    test_analyze_sentiment()
    print("✓ Enhanced sentiment analysis test passed")
    test_analyze_trends()
    print("✓ Trend analysis test passed")
    test_monitor_keywords()
    print("✓ Keyword monitoring test passed")
    print("\nAll tests passed successfully!") 