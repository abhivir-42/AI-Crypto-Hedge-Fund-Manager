#!/usr/bin/env python3
"""
Coin Info Agent

This module implements an agent that provides cryptocurrency information
by fetching data from the CoinGecko API. It responds to requests for
specific blockchain information with current price, market cap, and other data.
"""

import logging
import os
import sys
import requests
from typing import Dict, Any, Optional

from uagents import Context

# Use relative imports
from .base import BaseAgent
from ..models.requests import CoinRequest
from ..models.responses import CoinResponse
from ..utils.errors import APIError
from ..utils.logging import log_exception


class CoinInfoAgent(BaseAgent):
    """
    Agent that fetches cryptocurrency information.
    
    This agent receives requests for specific blockchain information
    and retrieves current price, market cap, and other relevant data
    from the CoinGecko API.
    """
    
    def __init__(self):
        """Initialize the Coin Info agent."""
        super().__init__(
            name="CoinInfoAgent",
            port=9009,
            seed=os.getenv("COIN_INFO_AGENT_SEED", "coin_info_agent1_secret_phrase")
        )
        
        # Map of supported blockchains to their CoinGecko IDs
        self.blockchain_map = {
            "ethereum": "ethereum",
            "base": "ethereum",  # Maps to ethereum
            "bitcoin": "bitcoin",
            "matic-network": "matic-network"
        }
    
    def register_handlers(self) -> None:
        """Register message handlers."""
        self.register_message_handler(CoinRequest, self.handle_coin_request)
    
    async def handle_coin_request(self, ctx: Context, sender: str, msg: CoinRequest) -> None:
        """
        Handle a coin information request.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Coin request message with blockchain name
        """
        self.logger.info(f"Received coin info request from {sender}: {msg.blockchain}")
        
        try:
            # Get cryptocurrency information
            crypto_data = self.get_crypto_info(msg.blockchain)
            
            # Send response back to sender
            await self.send_message(ctx, sender, crypto_data)
            self.logger.info(f"Sent crypto info response to {sender}")
            
        except Exception as e:
            log_exception(self.logger, e, f"Failed to process coin info request for {msg.blockchain}")
            
            # Send fallback response
            fallback_response = CoinResponse(
                name="Unknown",
                symbol="N/A",
                current_price=0.0,
                market_cap=0.0,
                total_volume=0.0,
                price_change_24h=0.0
            )
            await self.send_message(ctx, sender, fallback_response)
    
    def get_crypto_info(self, blockchain: str) -> CoinResponse:
        """
        Fetch cryptocurrency information from CoinGecko API.
        
        Args:
            blockchain: The blockchain name to fetch information for
            
        Returns:
            CoinResponse: The cryptocurrency information
            
        Raises:
            ValueError: If the blockchain is not supported
            APIError: If the API request fails
        """
        # Get coin ID from the blockchain map
        if blockchain not in self.blockchain_map:
            self.logger.error(f"Unsupported blockchain: {blockchain}")
            raise ValueError(f"Unsupported blockchain: {blockchain}")
        
        coin_id = self.blockchain_map[blockchain]
        self.logger.debug(f"Fetching data for {blockchain} (coin_id: {coin_id})")
        
        # Construct API URL
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        
        try:
            # Make API request
            response = requests.get(url)
            self.logger.info(f"URL for {coin_id} received...")
            response.raise_for_status()  # Raises an error for non-200 responses
            
            # Parse response data
            data = response.json()
            
            # Create and return coin response
            return CoinResponse(
                name=data['name'],
                symbol=data['symbol'].upper(),
                current_price=data['market_data']['current_price']['usd'],
                market_cap=data['market_data']['market_cap']['usd'],
                total_volume=data['market_data']['total_volume']['usd'],
                price_change_24h=data['market_data']['price_change_percentage_24h']
            )
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Request Failed: {e}")
            raise APIError(f"Failed to fetch data from CoinGecko API: {e}")


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="coin_info_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        coin_info_agent = CoinInfoAgent()
        coin_info_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


def main():
    """Entry point for the console script."""
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="coin_info_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        coin_info_agent = CoinInfoAgent()
        coin_info_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 