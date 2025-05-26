"""
Main application entry point for the Twitter MCP Server.
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from .services.twitter_service import app
from src.mcp import MCPServer
from src.services.twitter_service import TwitterService

app = FastAPI()
mcp = MCPServer()
twitter_service = TwitterService()

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 