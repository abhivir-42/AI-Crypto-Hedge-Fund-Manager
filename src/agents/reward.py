#!/usr/bin/env python3
"""
Reward Agent

This module implements an agent that handles reward payments and staking
on the Fetch.ai testnet. It receives payment requests, validates transactions,
and manages staking of tokens with validators.
"""

import logging
import os
import sys
from typing import Dict, Any

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.config import NetworkConfig
from cosmpy.aerial.faucet import FaucetApi
from cosmpy.crypto.address import Address
from dotenv import load_dotenv
from uagents import Context
from uagents.network import wait_for_tx_to_complete, get_faucet, get_ledger
from uagents.setup import fund_agent_if_low

from .base import BaseAgent
from ..models.requests import PaymentInquiry, RewardRequest
from ..models.responses import PaymentRequest, TransactionInfo, PaymentReceived
from ..utils.errors import BlockchainError
from ..utils.logging import log_exception


class RewardAgent(BaseAgent):
    """
    Agent that handles reward payments and staking.
    
    This agent receives and validates payment requests,
    confirms transactions, and stakes received tokens.
    """
    
    # Default payment amount and denomination
    AMOUNT = 1000000000000000000  # 1 TESTFET in atestfet
    DENOM = "atestfet"
    
    def __init__(self):
        """Initialize the Reward agent."""
        super().__init__(
            name="RewardAgent",
            port=8008,
            seed=os.getenv("REWARD_AGENT_SEED", "reward secret phrase agent oekwpfokw")
        )
        
        # Initialize ledger client
        self.ledger: LedgerClient = get_ledger()
        
        # Ensure agent has enough funds to operate
        fund_agent_if_low(self.agent.wallet.address(), min_balance=self.AMOUNT)
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(PaymentInquiry, self.handle_payment_inquiry)
        self.register_message_handler(TransactionInfo, self.handle_transaction_info)
        self.register_message_handler(RewardRequest, self.handle_reward_request)
    
    async def on_startup(self, ctx: Context) -> None:
        """
        Handle agent startup event.
        
        Args:
            ctx: Agent context
        """
        await super().on_startup(ctx)
        
        # Log wallet address and balance on startup
        wallet_address = self.agent.wallet.address()
        self.logger.info(f"Agent wallet address: {wallet_address}")
        
        agent_balance = self.get_balance(wallet_address)
        self.logger.info(f"Initial balance: {agent_balance} TESTFET")
    
    async def handle_payment_inquiry(self, ctx: Context, sender: str, msg: PaymentInquiry) -> None:
        """
        Handle a payment inquiry by sending payment instructions.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Payment inquiry message
        """
        self.logger.info(f"Received payment inquiry from {sender}: {msg.ready}")
        
        if msg.ready == "ready":
            # Send payment request with wallet address and amount
            await self.send_message(
                ctx, 
                sender, 
                PaymentRequest(
                    wallet_address=str(self.agent.wallet.address()),
                    amount=self.AMOUNT,
                    denom=self.DENOM
                )
            )
            self.logger.info(f"Sent payment request to {sender}")
    
    async def handle_transaction_info(self, ctx: Context, sender: str, msg: TransactionInfo) -> None:
        """
        Handle transaction information and confirm the transaction.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Transaction info message with transaction hash
        """
        self.logger.info(f"Received transaction info from {sender}: {msg.tx_hash}")
        
        try:
            # Wait for transaction to complete
            tx_resp = await wait_for_tx_to_complete(msg.tx_hash, ctx.ledger)
            
            # Verify transaction
            coin_received = tx_resp.events["coin_received"]
            wallet_address = str(self.agent.wallet.address())
            expected_amount = f"{self.AMOUNT}{self.DENOM}"
            
            if (coin_received["receiver"] == wallet_address and
                    coin_received["amount"] == expected_amount):
                self.logger.info(f"Transaction was successful: {coin_received}")
                status = "success"
            else:
                self.logger.info(f"Transaction was unsuccessful: {coin_received}")
                status = "failure"
            
            # Log new balance
            agent_balance = self.get_balance(self.agent.wallet.address())
            self.logger.info(f"Balance after transaction: {agent_balance} TESTFET")
            
            # Store transaction for later verification
            local_ledger = {"agent_address": self.agent.address, "tx": msg.tx_hash}
            ctx.storage.set(self.agent.wallet.address(), local_ledger)
            
            # Send confirmation
            await self.send_message(ctx, sender, PaymentReceived(status=status))
            
            # Stake received funds
            if status == "success":
                await self.stake_tokens(ctx)
            
        except Exception as e:
            log_exception(self.logger, e, "Transaction confirmation failed")
            await self.send_message(ctx, sender, PaymentReceived(status=f"Error: {str(e)}"))
    
    async def handle_reward_request(self, ctx: Context, sender: str, msg: RewardRequest) -> None:
        """
        Handle a reward request by checking stored transactions.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Reward request message
        """
        self.logger.info(f"Received reward request from {sender}: {msg.ready}")
        
        try:
            # Retrieve stored transaction for verification
            stored_data = ctx.storage.get(ctx.address)
            self.logger.info(f"Stored transaction data: {stored_data}")
            
            # Further processing would be implemented here
            # For now, just log the data
            
        except Exception as e:
            log_exception(self.logger, e, "Reward request processing failed")
    
    async def stake_tokens(self, ctx: Context) -> None:
        """
        Stake tokens with a validator.
        
        Args:
            ctx: Agent context
            
        Raises:
            BlockchainError: If staking fails
        """
        try:
            # Get current balance in atestfet
            wallet_address = self.agent.wallet.address()
            agent_balance = self.ledger.query_bank_balance(Address(wallet_address))
            
            if agent_balance <= 0:
                self.logger.info("No tokens to stake")
                return
            
            self.logger.info(f"Staking {agent_balance/1_000_000_000_000_000_000} TESTFET")
            
            # Initialize ledger client for staking
            ledger_client = LedgerClient(NetworkConfig.fetchai_stable_testnet())
            
            # Get validators
            validators = ledger_client.query_validators()
            
            # Choose a validator (index 2 as in the original code)
            validator = validators[2]
            self.logger.info(f"Selected validator: {validator.address}")
            
            # Delegate tokens to the validator
            tx = ledger_client.delegate_tokens(validator.address, agent_balance, self.agent.wallet)
            tx.wait_to_complete()
            
            # Check staking summary
            summary = ledger_client.query_staking_summary(wallet_address)
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
                logging.FileHandler(filename="reward_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        reward_agent = RewardAgent()
        reward_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 