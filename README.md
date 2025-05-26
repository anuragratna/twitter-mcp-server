# Twitter Market MCP Server

A Model Context Protocol (MCP) server that provides market sentiment analysis by combining Twitter data with stock market information.

## Features

- Real-time stock data analysis using yfinance
- Sentiment analysis using TextBlob
- MCP protocol compliance
- RESTful API endpoints
- Rate limiting and caching
- CORS support

## API Endpoints

- `GET /` - Health check
- `POST /analyze` - Analyze market sentiment for a stock symbol
- `GET /stock/{symbol}` - Get basic stock information
- `POST /_mcp/analyze` - MCP protocol endpoint for analysis
- `GET /_mcp/capabilities` - MCP protocol capabilities

## Deployment on Smithery

1. Build the Docker image:
```bash
docker build -t twitter-market-mcp .
```

2. Test locally:
```bash
docker run -p 8000:8000 twitter-market-mcp
```

3. Deploy to Smithery:
```bash
smithery deploy
```

## Environment Variables

- `PORT` - Server port (default: 8000)
- `CACHE_DURATION` - Cache duration in seconds (default: 3600)
- `LOG_LEVEL` - Logging level (default: INFO)

## Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
uvicorn src.mcp_server:app --reload
```

## Testing

Run the test suite:
```bash
python src/test_twitter_market_mcp.py
```

## API Documentation

Once running, visit:
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
