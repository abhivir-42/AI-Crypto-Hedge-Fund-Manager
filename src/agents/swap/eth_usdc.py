#!/usr/bin/env python3
"""
ETH to USDC Swap Agent

This module implements an agent that swaps ETH to USDC on the Uniswap decentralized
exchange on the Base network.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional

from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec
from web3 import Account, Web3
from uagents import Context, Model

from ..base import BaseAgent
from ...models.requests import SwapRequest
from ...models.responses import SwapResponse
from ...utils.errors import BlockchainError, ConfigurationError
from ...utils.logging import log_exception
from ...config.settings import (
    METAMASK_PRIVATE_KEY,
    BASE_RPC_URL,
    USDC_ADDRESS,
    WETH_ADDRESS,
    UNIVERSAL_ROUTER_ADDRESS,
    BASE_CHAIN_ID
)


class EthToUsdcAgent(BaseAgent):
    """
    Agent that swaps ETH to USDC on Uniswap.
    
    This agent receives swap requests and executes the swap transactions
    on the Uniswap decentralized exchange on the Base network.
    """
    
    def __init__(self):
        """Initialize the ETH to USDC swap agent."""
        super().__init__(
            name="ETH_USDC_SwapAgent",
            port=5002,
            seed=os.getenv("ETH_USDC_AGENT_SEED", "eth_usdc_agent_seed_phrase")
        )
        
        # Initialize Web3 and account
        self.web3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        
        # Ensure private key is available
        private_key = METAMASK_PRIVATE_KEY
        if not private_key:
            raise ConfigurationError("METAMASK_PRIVATE_KEY is not set in environment variables")
        
        self.account = Account.from_key(private_key)
        self.logger.info(f"Agent account: {self.account.address}")
        
        # Token addresses and chain configuration
        self.usdc_address = Web3.to_checksum_address(USDC_ADDRESS)
        self.weth_address = Web3.to_checksum_address(WETH_ADDRESS)
        self.router_address = Web3.to_checksum_address(UNIVERSAL_ROUTER_ADDRESS)
        self.chain_id = BASE_CHAIN_ID
        
        # Initialize RouterCodec
        self.codec = RouterCodec()
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(SwapRequest, self.handle_swap_request)
    
    async def handle_swap_request(self, ctx: Context, sender: str, msg: SwapRequest) -> None:
        """
        Handle a swap request for ETH to USDC.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Swap request message with amount
        """
        self.logger.info(f"Received swap request from {sender}: {msg.amount} ETH to USDC")
        
        try:
            # Validate request
            if msg.blockchain.lower() != "base" or msg.signal.lower() != "sell":
                await self.send_message(
                    ctx, 
                    sender, 
                    SwapResponse(
                        status="error",
                        message=f"Unsupported request: {msg.blockchain}/{msg.signal}"
                    )
                )
                return
            
            # Execute swap
            tx_hash = self.swap_eth_to_usdc(msg.amount)
            
            # Send success response
            await self.send_message(
                ctx, 
                sender, 
                SwapResponse(
                    status="success",
                    message=f"Swap executed. Transaction hash: {tx_hash}",
                    transaction_hash=tx_hash
                )
            )
            
        except Exception as e:
            log_exception(self.logger, e, "ETH to USDC swap failed")
            
            # Send error response
            await self.send_message(
                ctx, 
                sender, 
                SwapResponse(
                    status="error",
                    message=f"Swap failed: {str(e)}"
                )
            )
    
    def swap_eth_to_usdc(self, amount: float) -> str:
        """
        Execute ETH to USDC swap on Uniswap.
        
        Args:
            amount: Amount of ETH to swap in floating point (e.g., 0.1 for 0.1 ETH)
            
        Returns:
            str: Transaction hash
            
        Raises:
            BlockchainError: If the swap fails
        """
        try:
            # Convert amount to wei (1 ETH = 10^18 wei)
            amount_in_wei = int(amount * 10**18)
            
            # Calculate minimum amount out (with 1% slippage)
            # Simplified calculation; in practice, should use a price oracle
            # For simplicity, assuming 1 ETH = ~$2500 USD
            estimated_usdc_amount = amount * 2500.0  # Approximate USD value
            min_amount_out = int(estimated_usdc_amount * 0.99 * 10**6)  # USDC has 6 decimals
            
            # Define token path
            path = [self.weth_address, self.usdc_address]
            
            # Encode swap transaction
            encoded_input = (
                self.codec
                .encode
                .chain()
                .wrap_eth(FunctionRecipient.ROUTER, amount_in_wei)
                .v2_swap_exact_in(
                    FunctionRecipient.SENDER, 
                    amount_in_wei, 
                    min_amount_out, 
                    path, 
                    payer_is_sender=False
                )
                .build(self.codec.get_default_deadline())
            )
            
            # Prepare transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            tx_params = {
                "from": self.account.address,
                "to": self.router_address,
                "gas": 500_000,
                "maxPriorityFeePerGas": self.web3.eth.max_priority_fee,
                "maxFeePerGas": self.web3.eth.gas_price * 2,
                "type": '0x2',
                "chainId": self.chain_id,
                "value": amount_in_wei,
                "nonce": nonce,
                "data": encoded_input,
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx_params, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.logger.info(f"ETH to USDC swap transaction sent: {self.web3.to_hex(tx_hash)}")
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            self.logger.error(f"Error executing ETH to USDC swap: {e}")
            raise BlockchainError(f"Failed to swap ETH to USDC: {e}")


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="eth_usdc_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        eth_usdc_agent = EthToUsdcAgent()
        eth_usdc_agent.run()
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
                logging.FileHandler(filename="eth_usdc_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        eth_usdc_agent = EthToUsdcAgent()
        eth_usdc_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 