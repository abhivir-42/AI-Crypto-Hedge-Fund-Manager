#!/usr/bin/env python3

"""
Agent Testing Script

This script tests all agents in the system by running a dedicated test agent
that communicates with them using the uAgents framework.
"""

import time
import logging
import sys
import json
from uagents import Agent, Context

# Import models
from src.models.requests import CryptonewsRequest, CoinRequest, FGIRequest
from src.models.responses import CryptonewsResponse, CoinResponse, FGIResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Global flags to track responses
news_response_received = False
coin_response_received = False
fgi_response_received = False

# Agent addresses (from running instances)
NEWS_AGENT_ADDRESS = "agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9"
COIN_INFO_AGENT_ADDRESS = "agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq"
FGI_AGENT_ADDRESS = "agent1q248t3vk8f60y3dqsr2nzu93h7tpz26dy62l4ejdtl9ces2sml8ask8zmdp"

class TestAgent:
    def __init__(self):
        # Create test agent
        self.agent = Agent(
            name="TestAgent",
            port=9999,
            seed="test_agent_seed_for_testing_all_agents",
            endpoint=["http://127.0.0.1:9999/submit"],
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
        
        logger.info(f"✅ Received news response from {sender}")
        try:
            news = json.loads(msg.cryptoupdates)
            article_count = len(news.get('articles', []))
            logger.info(f"Received {article_count} news articles")
            
            if article_count > 0:
                logger.info(f"First article title: {news['articles'][0]['title']}")
            logger.info("✅ News agent test PASSED")
        except Exception as e:
            logger.error(f"❌ Failed to parse news response: {e}")
    
    async def handle_coin_response(self, ctx: Context, sender: str, msg: CoinResponse):
        global coin_response_received
        coin_response_received = True
        
        logger.info(f"✅ Received coin info response from {sender}")
        logger.info(f"Coin: {msg.name} ({msg.symbol})")
        logger.info(f"Price: ${msg.current_price:.2f}")
        logger.info(f"Market cap: ${msg.market_cap:.2f}")
        logger.info(f"24h change: {msg.price_change_24h:.2f}%")
        logger.info("✅ Coin info agent test PASSED")
    
    async def handle_fgi_response(self, ctx: Context, sender: str, msg: FGIResponse):
        global fgi_response_received
        fgi_response_received = True
        
        logger.info(f"✅ Received FGI response from {sender}")
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
    # Create and run the test agent
    test_agent = TestAgent()
    
    # Start the agent in background thread
    import threading
    agent_thread = threading.Thread(target=test_agent.agent.run)
    agent_thread.daemon = True
    agent_thread.start()
    
    logger.info("Agent started in background thread")
    
    # Wait for responses or timeout
    timeout = 30
    for _ in range(timeout):
        if news_response_received and coin_response_received and fgi_response_received:
            logger.info("✅ All tests passed!")
            break
        
        # Print waiting status
        waiting_for = []
        if not news_response_received: waiting_for.append("News")
        if not coin_response_received: waiting_for.append("Coin Info")
        if not fgi_response_received: waiting_for.append("FGI")
        
        if waiting_for:
            logger.info(f"Waiting for responses from: {', '.join(waiting_for)}")
        
        time.sleep(1)
    
    # Report results
    logger.info("\n--- TEST RESULTS ---")
    logger.info(f"News Agent: {'✅ PASSED' if news_response_received else '❌ FAILED'}")
    logger.info(f"Coin Info Agent: {'✅ PASSED' if coin_response_received else '❌ FAILED'}")
    logger.info(f"Fear & Greed Index Agent: {'✅ PASSED' if fgi_response_received else '❌ FAILED'}")
    
    # Return overall result
    return news_response_received and coin_response_received and fgi_response_received

if __name__ == "__main__":
    logger.info("Starting agent tests...")
    success = run_test()
    logger.info("Tests completed")
    sys.exit(0 if success else 1) 