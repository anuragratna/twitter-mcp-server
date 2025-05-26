"""
Main application entry point for the Twitter MCP Server.
"""

import uvicorn
from fastapi import FastAPI
from src.mcp import MCPServer
from src.services.twitter_service import TwitterService
from typing import Dict, Any

app = FastAPI(title="Twitter MCP Server")
mcp = MCPServer()
twitter_service = TwitterService()

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "message": "Twitter MCP Server is running",
        "tools": ["twitter.tweet", "twitter.delete_tweet", "twitter.analyze_sentiment"]
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

# Set up MCP routes
mcp.setup_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True) 