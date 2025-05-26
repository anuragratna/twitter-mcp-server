# Twitter MCP Server

A Machine Control Protocol (MCP) server that provides Twitter functionality through Claude Desktop. This server enables tweeting, tweet deletion, and powerful sentiment analysis capabilities. The sentiment analysis feature helps you understand the emotional tone of text content, making it a valuable tool for social media analysis and content moderation.

## Features

- Advanced sentiment analysis for text content
  - Analyze emotional tone of tweets
  - Get sentiment insights before posting
  - Evaluate content sentiment for moderation
- Post tweets
- Delete tweets
- FastAPI-based MCP server
- Docker support for easy deployment

## Prerequisites

- Python 3.8+
- Twitter API credentials
- Docker (for containerized deployment)

## Environment Variables

Create a `.env` file with your Twitter API credentials:

```env
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Local Development

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

## Docker Deployment

1. Build the image:
```bash
docker build -t twitter-mcp-server .
```

2. Run the container:
```bash
docker run -p 8001:8001 --env-file .env twitter-mcp-server
```

## Smithery Deployment

1. Push your code to a Git repository
2. In Smithery:
   - Create a new service
   - Connect your Git repository
   - Set the following environment variables:
     - `TWITTER_API_KEY`
     - `TWITTER_API_SECRET`
     - `TWITTER_ACCESS_TOKEN`
     - `TWITTER_ACCESS_TOKEN_SECRET`
   - Deploy using the provided Dockerfile

## Claude Desktop Integration

1. Copy the following configuration to your Claude Desktop config:
```json
{
  "mcp_servers": [
    {
      "name": "Twitter MCP Server",
      "url": "http://your-smithery-url:8001",
      "tools": [
        {
          "name": "twitter.tweet",
          "description": "Post a tweet",
          "parameters": {
            "text": {
              "type": "string",
              "description": "The text content of the tweet"
            }
          }
        },
        {
          "name": "twitter.delete_tweet",
          "description": "Delete a tweet",
          "parameters": {
            "tweet_id": {
              "type": "string",
              "description": "The ID of the tweet to delete"
            }
          }
        },
        {
          "name": "twitter.analyze_sentiment",
          "description": "Analyze the sentiment of text",
          "parameters": {
            "text": {
              "type": "string",
              "description": "The text to analyze for sentiment"
            }
          }
        }
      ]
    }
  ]
}
```

2. Replace `your-smithery-url` with your actual Smithery deployment URL

## API Documentation

Once the server is running, visit:
- OpenAPI documentation: `http://localhost:8001/docs`
- ReDoc documentation: `http://localhost:8001/redoc`

## License

MIT
