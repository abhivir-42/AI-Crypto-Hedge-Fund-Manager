#!/usr/bin/env python3
"""
Fear & Greed Index Agent

This module implements an agent that fetches the Fear & Greed Index for 
cryptocurrency markets from the CoinMarketCap API.
"""

import logging
import os
import sys
import json
import requests
from typing import Optional, Dict, Any

from uagents import Context

# Use relative imports
from .base import BaseAgent
from ..models.requests import FGIRequest
from ..models.responses import FGIResponse
from ..utils.errors import APIError
from ..utils.logging import log_exception
from ..config.settings import COINGECKO_API_KEY

from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import List


class FearGreedIndexAgent(BaseAgent):
    """
    Agent that provides Fear & Greed Index data.
    
    This agent responds to requests for market sentiment data
    by querying the CoinMarketCap API and returning structured responses.
    """
    
    def __init__(self):
        """Initialize the Fear & Greed Index agent."""
        super().__init__(
            name="FearGreedIndexAgent",
            port=9010,
            seed=os.getenv("FGI_AGENT_SEED", "fgi_agent1_secret_phrase")
        )
        
        # Get API key from environment
        self.cmc_api_key = os.getenv("CMC_API_KEY")
        if not self.cmc_api_key:
            self.logger.error("CMC_API_KEY is not set in environment variables")
            raise ValueError("CMC_API_KEY is required for the Fear & Greed Index Agent")
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(FGIRequest, self.handle_fgi_request)
    
    async def handle_fgi_request(self, ctx: Context, sender: str, msg: FGIRequest) -> None:
        """
        Handle requests for Fear & Greed Index data.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: FGI request message
        """
        self.logger.info(f"Received FGI request from {sender} for {msg.limit} entries")
        print(f"DEBUG: Received FGI request from {sender} for {msg.limit} entries")
        
        try:
            # Get Fear & Greed Index data
            fgi_data = self.get_fear_and_greed_index(msg.limit)
            
            # Log the data for debugging
            for entry in fgi_data.data:
                self.logger.debug(f"Fear and Greed Index: {entry.value}")
                self.logger.debug(f"Classification: {entry.value_classification}")
                self.logger.debug(f"Timestamp: {entry.timestamp}")
            
            # Send response back to sender
            await self.send_message(ctx, sender, fgi_data)
            self.logger.info(f"Sent FGI data to {sender}")
            
        except Exception as e:
            self.logger.error(f"Error processing FGI request: {e}")
            print(f"ERROR: Failed to process FGI request: {str(e)}")
            
            # Send error response with empty data
            error_response = FGIResponse(
                data=[],
                status="error",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            await self.send_message(ctx, sender, error_response)
    
    def get_fear_and_greed_index(self, limit: int = 1) -> FGIResponse:
        """
        Fetch Fear and Greed index data from CoinMarketCap API.
        
        Args:
            limit: Number of historical entries to retrieve
            
        Returns:
            FGIResponse: Structured Fear & Greed Index data
            
        Raises:
            APIError: If the API request fails
        """
        url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
        
        headers = {
            "X-CMC_PRO_API_KEY": self.cmc_api_key
        }
        
        params = {
            "limit": limit
        }
        
        try:
            self.logger.debug(f"Requesting data from CoinMarketCap for {limit} entries")
            print(f"DEBUG: Requesting data from CoinMarketCap with API key: {self.cmc_api_key[:5]}...")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises error for non-200 responses
            
            raw_data = response.json()
            fear_greed_data: List[FearGreedData] = []
            
            for entry in raw_data.get("data", []):
                data = FearGreedData(
                    value=entry["value"],
                    value_classification=entry["value_classification"],
                    timestamp=entry["timestamp"]
                )
                fear_greed_data.append(data)
            
            return FGIResponse(
                data=fear_greed_data,
                status="success",
                timestamp=datetime.now(timezone.utc).isoformat()
            )
        
        except requests.exceptions.RequestException as e:
            log_exception(self.logger, e, "CoinMarketCap API request failed")
            self.logger.warning("Using mock FGI data instead")
            print("WARNING: Using mock FGI data instead")
            
            # Create mock FGI data
            mock_data = [
                FearGreedData(
                    value=70.0,
                    value_classification="Greed",
                    timestamp=datetime.now(timezone.utc).isoformat()
                )
            ]
            
            return FGIResponse(
                data=mock_data,
                status="mock",
                timestamp=datetime.now(timezone.utc).isoformat()
            )


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="fear_greed_index_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        fgi_agent = FearGreedIndexAgent()
        fgi_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 