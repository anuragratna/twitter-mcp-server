# Twitter Market Sentiment MCP Server

A powerful financial market sentiment analysis tool that leverages Twitter data to provide real-time market insights through the Model Context Protocol (MCP). This server analyzes tweets about stocks and financial markets to gauge market sentiment, track price mentions, and identify market trends.

## Features

### 1. Market Sentiment Analysis
- Stock symbol-specific sentiment analysis (e.g., $AAPL, $TSLA)
- Bullish/bearish sentiment classification
- Price mention extraction and analysis
- Calculation of bullish-to-bearish ratio

### 2. Market Trend Analysis
- Multi-stock analysis
- Sector-wide sentiment tracking
- Correlated market topics identification
- Market mood assessment

### 3. Real-time Market Monitoring
- Watchlist-based monitoring
- Symbol-specific sentiment tracking
- Price-sentiment correlation analysis
- Trending market topics detection

## Setup Guide

### Prerequisites
- Python 3.9 or higher
- Twitter API v2 credentials (Developer Account required)
- pip or uv package manager

### Twitter API Setup
1. Create a Twitter Developer Account at https://developer.twitter.com
2. Create a new project and app
3. Enable OAuth 2.0
4. Generate the following credentials:
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token (for v2 API)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/twitter-mcp-server.git
cd twitter-mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with your Twitter API credentials:
```env
# Twitter API v2 Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here  # Required for v2 API

# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

5. Test your setup:
```bash
python src/test_env.py
```

### Running the Server

Start the server with:
```bash
uvicorn src.twitter_mcp:app --reload
```

The server will be available at:
- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- MCP Endpoint: http://localhost:8000/mcp

## API Endpoints

### 1. Market Sentiment Analysis
```http
POST /mcp/analyze_market_sentiment
```
Analyzes sentiment for a specific stock symbol.

Example request:
```json
{
    "symbol": "AAPL",
    "lookback_hours": 24
}
```

Example response:
```json
{
    "symbol": "AAPL",
    "sentiment_score": 0.42,
    "sentiment_label": "bullish",
    "tweet_count": 100,
    "common_topics": ["earnings", "stock price", "market performance"],
    "price_mentions": {
        "$150": 5,
        "$155.50": 3
    },
    "bullish_ratio": 0.75
}
```

### 2. Market Trends Analysis
```http
POST /mcp/analyze_market_trends
```
Analyzes trends across multiple stocks.

Example request:
```json
{
    "symbols": ["AAPL", "TSLA", "MSFT"],
    "hours": 24,
    "min_tweets": 50
}
```

### 3. Market Monitoring
```http
POST /mcp/monitor_market
```
Real-time market sentiment monitoring.

Example request:
```json
{
    "watchlist": ["AAPL", "GOOGL", "AMZN"],
    "timeframe_hours": 1
}
```

## Smithery Deployment

The server is configured for deployment on Smithery. Configuration is available in `smithery.yaml`.

Key deployment features:
- HTTP transport
- Environment variable management
- CORS support
- JSON logging
- Health check endpoint

## Development

### Running Tests
```bash
pytest src/test_twitter_mcp.py
```

### Environment Testing
```bash
python src/test_env.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Twitter API v2 for providing real-time market data
- TextBlob for sentiment analysis
- FastAPI for the web framework
- Smithery for deployment support 