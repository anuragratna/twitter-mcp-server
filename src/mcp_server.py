"""
Twitter Market MCP Server
Provides market sentiment analysis through MCP protocol
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from src.services.twitter_market_mcp import TwitterMarketMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Twitter Market MCP",
    description="Market sentiment analysis service using Twitter and stock data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the MCP service
mcp_service = TwitterMarketMCP()

class MarketSentimentRequest(BaseModel):
    symbol: str
    include_news: Optional[bool] = True

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Twitter Market MCP"}

@app.post("/analyze")
async def analyze_market_sentiment(request: MarketSentimentRequest):
    """
    Analyze market sentiment for a given stock symbol
    """
    try:
        result = await mcp_service.analyze_market_sentiment(request.symbol)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error analyzing market sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{symbol}")
async def get_stock_info(symbol: str):
    """
    Get basic stock information
    """
    try:
        result = await mcp_service.get_stock_info(symbol)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error getting stock info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# MCP Protocol Endpoints
@app.post("/_mcp/analyze")
async def mcp_analyze(request: Request):
    """
    MCP protocol endpoint for market sentiment analysis
    """
    try:
        data = await request.json()
        symbol = data.get("symbol")
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        result = await mcp_service.analyze_market_sentiment(symbol)
        return JSONResponse(content={
            "status": "success",
            "data": result,
            "metadata": {
                "version": "1.0.0",
                "provider": "twitter_market_mcp"
            }
        })
    except Exception as e:
        logger.error(f"MCP analyze error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "metadata": {
                    "version": "1.0.0",
                    "provider": "twitter_market_mcp"
                }
            }
        )

@app.get("/_mcp/capabilities")
async def mcp_capabilities():
    """
    MCP protocol capabilities endpoint
    """
    return {
        "version": "1.0.0",
        "provider": "twitter_market_mcp",
        "capabilities": {
            "analyze": {
                "description": "Analyze market sentiment for a stock symbol",
                "parameters": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL)",
                        "required": True
                    }
                }
            }
        }
    } 