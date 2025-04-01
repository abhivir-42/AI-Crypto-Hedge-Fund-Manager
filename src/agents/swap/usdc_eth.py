#!/usr/bin/env python3
"""
USDC to ETH Swap Agent

This module implements an agent that swaps USDC to ETH on the Uniswap decentralized
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


class UsdcToEthAgent(BaseAgent):
    """
    Agent that swaps USDC to ETH on Uniswap.
    
    This agent receives swap requests and executes the swap transactions
    on the Uniswap decentralized exchange on the Base network.
    """
    
    def __init__(self):
        """Initialize the USDC to ETH swap agent."""
        super().__init__(
            name="USDC_ETH_SwapAgent",
            port=5004,
            seed=os.getenv("USDC_ETH_AGENT_SEED", "usdc_eth_agent_seed_phrase")
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
        self.permit2_address = Web3.to_checksum_address("0x000000000022D473030F116dDEE9F6B43aC78BA3")
        self.chain_id = BASE_CHAIN_ID
        
        # Initialize contracts
        self.usdc_abi = '[{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},{"internalType":"uint256","name":"mintingAllowedAfter_","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegator","type":"address"},{"indexed":true,"internalType":"address","name":"fromDelegate","type":"address"},{"indexed":true,"internalType":"address","name":"toDelegate","type":"address"}],"name":"DelegateChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"delegate","type":"address"},{"indexed":false,"internalType":"uint256","name":"previousBalance","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newBalance","type":"uint256"}],"name":"DelegateVotesChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"minter","type":"address"},{"indexed":false,"internalType":"address","name":"newMinter","type":"address"}],"name":"MinterChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DELEGATION_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"DOMAIN_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"rawAmount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"checkpoints","outputs":[{"internalType":"uint32","name":"fromBlock","type":"uint32"},{"internalType":"uint96","name":"votes","type":"uint96"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"}]'
        self.usdc_contract = self.web3.eth.contract(address=self.usdc_address, abi=self.usdc_abi)
        
        # Initialize RouterCodec
        self.codec = RouterCodec()
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(SwapRequest, self.handle_swap_request)
    
    async def handle_swap_request(self, ctx: Context, sender: str, msg: SwapRequest) -> None:
        """
        Handle a swap request for USDC to ETH.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Swap request message with amount
        """
        self.logger.info(f"Received swap request from {sender}: {msg.amount} USDC to ETH")
        
        try:
            # Validate request
            if msg.blockchain.lower() != "base" or msg.signal.lower() != "buy":
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
            tx_hash = self.swap_usdc_to_eth(msg.amount)
            
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
            log_exception(self.logger, e, "USDC to ETH swap failed")
            
            # Send error response
            await self.send_message(
                ctx, 
                sender, 
                SwapResponse(
                    status="error",
                    message=f"Swap failed: {str(e)}"
                )
            )
    
    def ensure_permit2_approval(self) -> str:
        """
        Ensure USDC is approved for Permit2 contract.
        
        Returns:
            str: Transaction hash for approval if needed, empty string if already approved
            
        Raises:
            BlockchainError: If approval fails
        """
        permit2_allowance_needed = 2**256 - 1
        current_allowance = self.usdc_contract.functions.allowance(
            self.account.address, 
            self.permit2_address
        ).call()
        
        if current_allowance >= permit2_allowance_needed:
            self.logger.info("Permit2 already approved for USDC")
            return ""
        
        try:
            # Approve Permit2 for USDC
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            approve_tx = self.usdc_contract.functions.approve(
                self.permit2_address, 
                permit2_allowance_needed
            ).build_transaction({
                "from": self.account.address,
                "gas": 100_000,
                "maxPriorityFeePerGas": self.web3.eth.max_priority_fee * 2,
                "maxFeePerGas": self.web3.eth.gas_price * 3,
                "nonce": nonce,
                "chainId": self.chain_id,
                "value": 0,
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(approve_tx, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.logger.info(f"Permit2 approval transaction sent: {self.web3.to_hex(tx_hash)}")
            
            # Wait for transaction confirmation
            self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            self.logger.error(f"Error approving Permit2 for USDC: {e}")
            raise BlockchainError(f"Failed to approve Permit2: {e}")
    
    def swap_usdc_to_eth(self, amount: float) -> str:
        """
        Execute USDC to ETH swap on Uniswap.
        
        Args:
            amount: Amount of USDC to swap in floating point (e.g., 10 for 10 USDC)
            
        Returns:
            str: Transaction hash
            
        Raises:
            BlockchainError: If the swap fails
        """
        try:
            # Ensure Permit2 approval first
            approval_tx = self.ensure_permit2_approval()
            if approval_tx:
                self.logger.info(f"USDC approved for Permit2: {approval_tx}")
            
            # Convert amount to USDC units (6 decimals)
            amount_in_usdc = int(amount * 10**6)
            
            # Calculate minimum amount out (with 1% slippage)
            # Simplified calculation; in practice, should use a price oracle
            # For simplicity, assuming 1 ETH = ~$2500 USD
            estimated_eth_amount = amount / 2500.0  # Approximate ETH value
            min_amount_out = int(estimated_eth_amount * 0.99 * 10**18)  # ETH has 18 decimals
            
            # Define token path
            path = [self.usdc_address, self.weth_address]
            
            # Approve Universal Router to spend USDC
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            approve_tx = self.usdc_contract.functions.approve(
                self.router_address, 
                amount_in_usdc
            ).build_transaction({
                "from": self.account.address,
                "gas": 250_000,
                "maxPriorityFeePerGas": self.web3.eth.max_priority_fee,
                "maxFeePerGas": self.web3.eth.gas_price * 2,
                "nonce": nonce,
                "chainId": self.chain_id,
                "value": 0,
            })
            
            signed_approve_tx = self.web3.eth.account.sign_transaction(approve_tx, self.account.key)
            approve_tx_hash = self.web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
            
            self.logger.info(f"USDC approval transaction sent: {self.web3.to_hex(approve_tx_hash)}")
            
            # Wait for approval transaction confirmation
            self.web3.eth.wait_for_transaction_receipt(approve_tx_hash, timeout=120)
            
            # Encode swap transaction
            encoded_input = (
                self.codec
                .encode
                .chain()
                .v2_swap_exact_in(
                    FunctionRecipient.ROUTER, 
                    amount_in_usdc, 
                    min_amount_out, 
                    path, 
                    payer_is_sender=True
                )
                .unwrap_weth(FunctionRecipient.SENDER, 0)
                .build(self.codec.get_default_deadline())
            )
            
            # Prepare transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            tx_params = {
                "from": self.account.address,
                "to": self.router_address,
                "gas": 500_000,
                "maxPriorityFeePerGas": self.web3.eth.max_priority_fee,
                "maxFeePerGas": self.web3.eth.gas_price * 2,
                "type": '0x2',
                "chainId": self.chain_id,
                "value": 0,
                "nonce": nonce,
                "data": encoded_input,
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx_params, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.logger.info(f"USDC to ETH swap transaction sent: {self.web3.to_hex(tx_hash)}")
            return self.web3.to_hex(tx_hash)
            
        except Exception as e:
            self.logger.error(f"Error executing USDC to ETH swap: {e}")
            raise BlockchainError(f"Failed to swap USDC to ETH: {e}")


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="usdc_eth_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        usdc_eth_agent = UsdcToEthAgent()
        usdc_eth_agent.run()
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
                logging.FileHandler(filename="usdc_eth_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        usdc_eth_agent = UsdcToEthAgent()
        usdc_eth_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 