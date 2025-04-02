#!/usr/bin/env python3

import asyncio
import logging
from uagents import Agent, Context, Model
import json
import sys
from typing import List, Optional

# Import models
from src.models.requests import CryptonewsRequest, CoinRequest, FGIRequest
from src.models.responses import CryptonewsResponse, CoinResponse, FGIResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set flag for response tracking
news_response_received = False
coin_response_received = False
fgi_response_received = False

# Addresses of our agents - use actual addresses from running agents
NEWS_AGENT_ADDRESS = "agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9"
COIN_INFO_AGENT_ADDRESS = "agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq"
FGI_AGENT_ADDRESS = "agent1q248t3vk8f60y3dqsr2nzu93h7tpz26dy62l4ejdtl9ces2sml8ask8zmdp"

class TestAgent:
    def __init__(self):
        # Create test agent
        self.agent = Agent(
            name="TestAgent",
            port=9999,
            seed="test_agent_secret_seed_phrase"
        )
        
        # Register message handlers
        self.agent.on_message(model=CryptonewsResponse)(self.handle_news_response)
        self.agent.on_message(model=CoinResponse)(self.handle_coin_response)
        self.agent.on_message(model=FGIResponse)(self.handle_fgi_response)
        
        # Register startup handler
        self.agent.on_event("startup")(self.on_startup)
    
    async def handle_news_response(self, ctx: Context, sender: str, msg: CryptonewsResponse):
        global news_response_received
        news_response_received = True
        
        logger.info(f"Received news response from {sender}")
        try:
            news = json.loads(msg.cryptoupdates)
            article_count = len(news.get('articles', []))
            logger.info(f"Received {article_count} news articles")
            
            if article_count > 0:
                logger.info(f"First article title: {news['articles'][0]['title']}")
                logger.info(f"First article source: {news['articles'][0]['source']['name']}")
            logger.info("✅ News agent test PASSED")
        except Exception as e:
            logger.error(f"❌ Failed to parse news response: {e}")
            logger.error(f"Raw response: {msg.cryptoupdates[:200]}...")
    
    async def handle_coin_response(self, ctx: Context, sender: str, msg: CoinResponse):
        global coin_response_received
        coin_response_received = True
        
        logger.info(f"Received coin info response from {sender}")
        logger.info(f"Coin: {msg.name} ({msg.symbol})")
        logger.info(f"Price: ${msg.current_price:.2f}")
        logger.info(f"Market cap: ${msg.market_cap:.2f}")
        logger.info(f"24h change: {msg.price_change_24h:.2f}%")
        logger.info("✅ Coin info agent test PASSED")
    
    async def handle_fgi_response(self, ctx: Context, sender: str, msg: FGIResponse):
        global fgi_response_received
        fgi_response_received = True
        
        logger.info(f"Received FGI response from {sender}")
        if msg.data and len(msg.data) > 0:
            logger.info(f"Fear & Greed Index: {msg.data[0].value} ({msg.data[0].value_classification})")
            logger.info(f"Timestamp: {msg.data[0].timestamp}")
            logger.info("✅ Fear & Greed Index agent test PASSED")
        else:
            logger.error("❌ No data in FGI response")
    
    async def on_startup(self, ctx: Context):
        logger.info(f"Test agent started with address: {ctx.agent.address}")
        
        # Send request to news agent
        logger.info(f"Sending request to News Agent at {NEWS_AGENT_ADDRESS}")
        await ctx.send(NEWS_AGENT_ADDRESS, CryptonewsRequest(limit=3))
        
        # Send request to coin info agent
        logger.info(f"Sending request to Coin Info Agent at {COIN_INFO_AGENT_ADDRESS}")
        await ctx.send(COIN_INFO_AGENT_ADDRESS, CoinRequest(blockchain="ethereum"))
        
        # Send request to fear & greed index agent
        logger.info(f"Sending request to Fear & Greed Index Agent at {FGI_AGENT_ADDRESS}")
        await ctx.send(FGI_AGENT_ADDRESS, FGIRequest(limit=1))

def run_test():
    # Create test agent
    test_agent = TestAgent()
    
    # Run the agent for 30 seconds max
    try:
        logger.info("Starting test agent...")
        
        # Run agent directly (this will block until timeout)
        test_agent.agent.run(timeout=30)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    
    # Report results
    logger.info("\n--- TEST RESULTS ---")
    logger.info(f"News Agent: {'✅ PASSED' if news_response_received else '❌ FAILED'}")
    logger.info(f"Coin Info Agent: {'✅ PASSED' if coin_response_received else '❌ FAILED'}")
    logger.info(f"Fear & Greed Index Agent: {'✅ PASSED' if fgi_response_received else '❌ FAILED'}")
    
    # Return overall test result
    if news_response_received and coin_response_received and fgi_response_received:
        logger.info("✅ All tests passed successfully!")
        return True
    else:
        logger.error("❌ Some tests failed")
        return False

if __name__ == "__main__":
    logger.info("Starting agent tests...")
    success = run_test()
    logger.info("Tests completed")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 