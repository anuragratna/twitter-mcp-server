import asyncio
from services.twitter_market_mcp import TwitterMarketMCP

async def test_market_sentiment():
    """Test the Twitter Market MCP service with a sample stock symbol."""
    try:
        # Initialize the service
        mcp = TwitterMarketMCP()
        
        # Test stock symbol
        symbol = "AAPL"  # Apple Inc.
        
        print(f"\nTesting market sentiment analysis for {symbol}...")
        
        # Test stock info
        stock_info = await mcp.get_stock_info(symbol)
        print("\nStock Information:")
        print(f"Company: {stock_info['company_name']}")
        print(f"Current Price: ${stock_info['current_price']:.2f}")
        print(f"Price Change: ${stock_info['price_change']:.2f} ({stock_info['price_change_pct']:.2f}%)")
        print(f"Industry: {stock_info['industry']}")
        print(f"Market Cap: ${stock_info['market_cap']:,}")
        
        # Test sentiment analysis
        sentiment_data = await mcp.analyze_market_sentiment(symbol)
        print("\nSentiment Analysis:")
        print(f"Price Trend: {sentiment_data['price_trend']}")
        print(f"Volatility: {sentiment_data['volatility']:.2f}%")
        print(f"Sentiment: {sentiment_data['sentiment']['label']} (score: {sentiment_data['sentiment']['score']:.2f})")
        print(f"\nOverall Assessment: {sentiment_data['overall_assessment']}")
        
        # Print recent news headlines and their sentiment
        print("\nRecent News Analysis:")
        for idx, news in enumerate(sentiment_data['news_analysis'][:5], 1):
            print(f"\n{idx}. {news['title']}")
            print(f"   Sentiment: {news['sentiment']:.2f}")
            print(f"   Link: {news['link']}")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_market_sentiment()) 