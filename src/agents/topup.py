#!/usr/bin/env python3
"""
Topup Agent

This module implements an agent that handles token top-up operations on the 
Fetch.ai testnet. It processes top-up requests, interacts with the faucet, 
and manages token staking.
"""

import logging
import os
import sys
import time
from typing import Optional, Dict, Any

from uagents import Context
from uagents.network import get_faucet, get_ledger
from cosmpy.crypto.address import Address
from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.config import NetworkConfig
from cosmpy.aerial.faucet import FaucetApi
from cosmpy.aerial.wallet import LocalWallet

# Use relative imports
from .base import BaseAgent
from ..models.requests import TopupRequest
from ..models.responses import TopupResponse
from ..utils.errors import BlockchainError
from ..utils.logging import log_exception


class TopupAgent(BaseAgent):
    """
    Agent that handles token top-up operations.
    
    This agent provides functionality to request tokens from the Fetch.ai testnet
    faucet and stake tokens with validators.
    """
    
    def __init__(self):
        """Initialize the Top-up agent."""
        super().__init__(
            name="TopupAgent",
            port=8001,
            seed=os.getenv("TOPUP_AGENT_SEED", "kjpopoFJpwjofemwffreSTRgkgjkkjkjINGS")
        )
        
        # Initialize the ledger and faucet
        self.ledger: LedgerClient = get_ledger()
        self.faucet: FaucetApi = get_faucet()
        
        # Ensure this agent has funds to operate
        fund_agent_if_low(self.agent.wallet.address())
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(TopupRequest, self.handle_topup_request)
        self.agent.on_interval(60.0)(self.get_faucet_and_stake)  # Run every minute
    
    async def on_startup(self, ctx: Context) -> None:
        """
        Handle agent startup event.
        
        Args:
            ctx: Agent context
        """
        await super().on_startup(ctx)
        self.logger.info(f"Agent wallet address: {self.agent.wallet.address()}")
        
        # Check initial balance
        agent_balance = self.get_balance(self.agent.wallet.address())
        self.logger.info(f"Initial balance: {agent_balance} TESTFET")
    
    async def handle_topup_request(self, ctx: Context, sender: str, msg: TopupRequest) -> None:
        """
        Handle a top-up request.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Top-up request with amount
        """
        self.logger.info(f"Received top-up request from {sender} for {msg.amount} tokens")
        
        try:
            # Get the current balance
            initial_balance = self.get_balance(ctx.agent.wallet.address())
            self.logger.info(f"Current balance before top-up: {initial_balance} TESTFET")
            
            # Request tokens from the faucet
            self.faucet.get_wealth(ctx.agent.wallet.address())
            
            # Check new balance
            new_balance = self.get_balance(ctx.agent.wallet.address())
            self.logger.info(f"Balance after top-up: {new_balance} TESTFET")
            
            # Send success response
            await self.send_message(ctx, sender, TopupResponse(status="Success!"))
            self.logger.info(f"Sent top-up success response to {sender}")
            
        except Exception as e:
            log_exception(self.logger, e, "Top-up request failed")
            
            # Send error response
            await self.send_message(ctx, sender, TopupResponse(status=f"Error: {str(e)}"))
    
    async def get_faucet_and_stake(self, ctx: Context) -> None:
        """
        Periodically get tokens from the faucet and stake them.
        
        Args:
            ctx: Agent context
        """
        try:
            # Get the current balance
            initial_balance = self.get_balance(self.agent.wallet.address())
            self.logger.info(f"Current balance before faucet: {initial_balance} TESTFET")
            
            # Request tokens from the faucet
            self.faucet.get_wealth(self.agent.wallet.address())
            
            # Check new balance
            new_balance = self.get_balance(self.agent.wallet.address())
            self.logger.info(f"Balance after faucet: {new_balance} TESTFET")
            
            # Calculate the amount to stake (in atestfet)
            agent_balance_atestfet = self.ledger.query_bank_balance(Address(self.agent.wallet.address()))
            
            # Proceed with staking if there are tokens to stake
            if agent_balance_atestfet > 0:
                await self.stake_tokens(ctx, agent_balance_atestfet)
            else:
                self.logger.info("No tokens to stake")
            
        except Exception as e:
            log_exception(self.logger, e, "Faucet and stake operation failed")
    
    async def stake_tokens(self, ctx: Context, amount: int) -> None:
        """
        Stake tokens with a validator.
        
        Args:
            ctx: Agent context
            amount: Amount to stake in atestfet
            
        Raises:
            BlockchainError: If staking fails
        """
        try:
            # Initialize ledger client for staking
            ledger_client = LedgerClient(NetworkConfig.fetchai_stable_testnet())
            
            # Get validators
            validators = ledger_client.query_validators()
            
            # Choose a validator (index 2 as in the original code)
            validator = validators[2]
            self.logger.info(f"Selected validator: {validator.address}")
            
            # Delegate tokens to the validator
            tx = ledger_client.delegate_tokens(validator.address, amount, self.agent.wallet)
            tx.wait_to_complete()
            
            # Check staking summary
            summary = ledger_client.query_staking_summary(self.agent.wallet.address())
            total_staked = summary.total_staked / 1_000_000_000_000_000_000
            self.logger.info(f"Staking completed. Total staked: {total_staked} TESTFET")
            
        except Exception as e:
            log_exception(self.logger, e, "Staking operation failed")
            raise BlockchainError(f"Failed to stake tokens: {e}")
    
    def get_balance(self, address: str) -> float:
        """
        Get the token balance for an address in TESTFET.
        
        Args:
            address: The address to check
            
        Returns:
            float: The balance in TESTFET
        """
        try:
            # Query balance in atestfet (1 TESTFET = 10^18 atestfet)
            balance_atestfet = self.ledger.query_bank_balance(Address(address))
            
            # Convert to TESTFET
            balance_testfet = balance_atestfet / 1_000_000_000_000_000_000
            
            return balance_testfet
            
        except Exception as e:
            self.logger.error(f"Error querying balance: {e}")
            return 0.0


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="topup_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        topup_agent = TopupAgent()
        topup_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 