#!/usr/bin/env python3
"""
Crypto News Agent

This module implements an agent that fetches cryptocurrency news articles
from the News API service.
"""

import logging
import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional

from uagents import Context

# Use relative imports
from .base import BaseAgent
from ..models.requests import NewsRequest
from ..models.responses import NewsResponse
from ..utils.errors import APIError
from ..utils.logging import log_exception

from dotenv import load_dotenv
from newsapi import NewsApiClient

from crypto_project.models.requests import CryptonewsRequest
from crypto_project.models.responses import CryptonewsResponse


class CryptoNewsAgent(BaseAgent):
    """
    Agent that provides cryptocurrency news.
    
    This agent responds to requests for cryptocurrency news
    by querying the News API and returning structured responses.
    """
    
    def __init__(self):
        """Initialize the Crypto News agent."""
        super().__init__(
            name="CryptoNewsAgent",
            port=8016,
            seed=os.getenv("CRYPTO_NEWS_AGENT_SEED", "newsnewshehhee_agent1_secret_phrase")
        )
        
        # Get API key from environment
        self.news_api_key = os.getenv("NEWS_API_KEY")
        if not self.news_api_key:
            self.logger.warning("NEWS_API_KEY is not set in environment variables, using hardcoded value")
            self.news_api_key = "94b2d38f6b104eafa2f041bc323ed03c"  # Fallback value from original code
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(CryptonewsRequest, self.handle_news_request)
    
    async def handle_news_request(self, ctx: Context, sender: str, msg: CryptonewsRequest) -> None:
        """
        Handle requests for cryptocurrency news.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Crypto news request message
        """
        self.logger.info(f"Received news request from {sender} for {msg.limit} entries")
        
        try:
            # Get crypto news
            news_data = self.get_recent_crypto_news(msg.limit)
            
            # Send response back to sender
            await self.send_message(ctx, sender, CryptonewsResponse(cryptoupdates=news_data))
            self.logger.info(f"Sent crypto news to {sender}")
            
        except Exception as e:
            self.logger.error(f"Error processing news request: {e}")
            
            # Send error response with empty data
            error_response = CryptonewsResponse(cryptoupdates=json.dumps({"error": str(e)}))
            await self.send_message(ctx, sender, error_response)
    
    def get_recent_crypto_news(self, limit: int = 1) -> str:
        """
        Fetch cryptocurrency news from News API.
        
        Args:
            limit: Number of news items to retrieve
            
        Returns:
            str: JSON string with news data
            
        Raises:
            APIError: If the API request fails
        """
        try:
            # Initialize News API client
            newsapi = NewsApiClient(api_key=self.news_api_key)
            
            # Query for crypto-related news
            crypto_news = newsapi.get_everything(
                q="crypto OR cryptocurrency OR bitcoin OR ethereum OR financial market OR crypto exchange OR bullish OR bearish OR recession OR FOMC",
                language="en",
                page_size=limit
            )
            
            self.logger.debug(f"Retrieved {len(crypto_news.get('articles', []))} news articles")
            
            # Return news data as JSON string
            return json.dumps(crypto_news)
            
        except Exception as e:
            log_exception(self.logger, e, "News API request failed")
            raise APIError(f"Failed to fetch data from News API: {e}")


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="crypto_news_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        news_agent = CryptoNewsAgent()
        news_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 