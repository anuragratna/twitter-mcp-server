"""
Main application entry point for the Twitter MCP Server.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from src.mcp import MCPServer
from src.services.twitter_service import TwitterService
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Twitter MCP Server")
mcp = MCPServer()

# Initialize services
try:
    twitter_service = TwitterService()
    logger.info("Twitter service initialized")
except Exception as e:
    logger.error(f"Failed to initialize Twitter service: {str(e)}")
    twitter_service = None

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    status = "healthy"
    if not twitter_service or not twitter_service.api:
        status = "degraded"
    return {"status": status}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "Twitter MCP Server is running",
        "tools": ["twitter.tweet", "twitter.delete_tweet", "twitter.analyze_sentiment"],
        "twitter_api_status": "available" if twitter_service and twitter_service.api else "unavailable"
    }

# Register Twitter MCP tools
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
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not initialized")
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
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not initialized")
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
    if not twitter_service:
        raise HTTPException(status_code=503, detail="Twitter service not initialized")
    return await twitter_service.analyze_sentiment(text)

# Set up MCP routes
mcp.setup_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 