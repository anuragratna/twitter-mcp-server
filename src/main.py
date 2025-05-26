"""
Main application entry point for the Twitter MCP Server.
"""

import uvicorn
from .services.twitter_service import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 