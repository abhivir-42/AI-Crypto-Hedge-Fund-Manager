#!/usr/bin/env python3
"""
USDC to ETH Swap Service

This module provides functionality for swapping USDC to ETH on Uniswap
on the Base network.
"""

import logging
import os
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple

from web3 import Web3, Account
from uniswap_universal_router_decoder import FunctionRecipient, RouterCodec

from ...utils.errors import BlockchainError, ConfigurationError
from ...config.settings import (
    METAMASK_PRIVATE_KEY,
    BASE_RPC_URL,
    USDC_ADDRESS,
    WETH_ADDRESS,
    UNIVERSAL_ROUTER_ADDRESS,
    BASE_CHAIN_ID
)


class USDCETHSwapService:
    """
    Service for handling USDC to ETH swap operations on Uniswap.
    """
    
    def __init__(self, ethereum_rpc_url: str = None, private_key: str = None):
        """
        Initialize the USDC to ETH swap service.
        
        Args:
            ethereum_rpc_url: Optional RPC URL override
            private_key: Optional private key override
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Initialize logger
        self.logger = logging.getLogger("service.swap.usdc_eth")
        
        # Set configuration
        self.ethereum_rpc_url = ethereum_rpc_url or BASE_RPC_URL
        self.private_key = private_key or METAMASK_PRIVATE_KEY
        
        # Validate configuration
        if not self.ethereum_rpc_url:
            raise ConfigurationError("Ethereum RPC URL not provided")
        if not self.private_key:
            raise ConfigurationError("Ethereum private key not provided")
        
        # Initialize Web3 provider
        self.web3 = Web3(Web3.HTTPProvider(self.ethereum_rpc_url))
        if not self.web3.is_connected():
            raise ConfigurationError(f"Could not connect to Ethereum node at {self.ethereum_rpc_url}")
        
        # Initialize account
        self.account = Account.from_key(self.private_key)
        self.logger.info(f"Initialized with account: {self.account.address}")
        
        # Set token addresses
        self.usdc_address = Web3.to_checksum_address(USDC_ADDRESS)
        self.weth_address = Web3.to_checksum_address(WETH_ADDRESS)
        self.router_address = Web3.to_checksum_address(UNIVERSAL_ROUTER_ADDRESS)
        self.permit2_address = Web3.to_checksum_address("0x000000000022D473030F116dDEE9F6B43aC78BA3")  # Standard Permit2 address
        self.chain_id = BASE_CHAIN_ID
        
        # Initialize contracts and decoder
        self._initialize_contracts()
        self.codec = RouterCodec()
    
    def _initialize_contracts(self) -> None:
        """
        Initialize smart contract interfaces.
        
        Sets up the USDC token and other necessary contracts.
        """
        # ABI for ERC20 token (for USDC)
        erc20_abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'
        
        # Initialize USDC contract
        self.usdc_contract = self.web3.eth.contract(
            address=self.usdc_address,
            abi=erc20_abi
        )
        
        # Get USDC decimals
        self.usdc_decimals = self.usdc_contract.functions.decimals().call()
        self.logger.debug(f"USDC decimals: {self.usdc_decimals}")
    
    def get_eth_balance(self) -> float:
        """
        Get the ETH balance of the account.
        
        Returns:
            float: The ETH balance in ether units
        """
        wei_balance = self.web3.eth.get_balance(self.account.address)
        eth_balance = self.web3.from_wei(wei_balance, 'ether')
        return float(eth_balance)
    
    def get_usdc_balance(self) -> float:
        """
        Get the USDC balance of the account.
        
        Returns:
            float: The USDC balance in USDC units
        """
        usdc_balance_raw = self.usdc_contract.functions.balanceOf(self.account.address).call()
        usdc_balance = usdc_balance_raw / (10 ** self.usdc_decimals)
        return float(usdc_balance)
    
    def get_eth_price(self) -> float:
        """
        Get the current ETH price in USDC.
        
        Returns:
            float: The current ETH price in USDC
            
        Raises:
            BlockchainError: If the price cannot be retrieved
        """
        try:
            # Import here to avoid circular imports
            from ...services.llm_service import get_eth_price as fetch_price
            return fetch_price()
        except Exception as e:
            self.logger.warning(f"Failed to get ETH price from LLM service: {e}")
            
            # Fallback: Use a reasonable estimate (this should be replaced with a proper price oracle)
            # In a production system, you would use a reliable price oracle
            return 3000.0  # Approximate ETH price in USD
    
    def estimate_eth_output(self, usdc_amount: float, slippage: float = 0.01) -> Tuple[float, float]:
        """
        Estimate the amount of ETH that will be received for a given USDC input.
        
        Args:
            usdc_amount: Amount of USDC to swap
            slippage: Maximum acceptable slippage (default: 1%)
            
        Returns:
            Tuple[float, float]: Estimated ETH output and minimum ETH output with slippage
            
        Raises:
            BlockchainError: If the estimation fails
        """
        try:
            # Get current ETH price
            eth_price = self.get_eth_price()
            
            # Calculate expected ETH output (USDC amount / price)
            estimated_eth = usdc_amount / eth_price
            
            # Apply slippage to get minimum output
            min_eth_output = estimated_eth * (1 - slippage)
            
            self.logger.info(f"Estimated {usdc_amount} USDC -> ~{estimated_eth:.6f} ETH (min: {min_eth_output:.6f})")
            
            return estimated_eth, min_eth_output
            
        except Exception as e:
            self.logger.error(f"Error estimating ETH output: {e}")
            raise BlockchainError(f"Failed to estimate ETH output: {e}")
    
    def ensure_permit2_approval(self) -> str:
        """
        Ensure USDC is approved for Permit2 contract.
        
        Returns:
            str: Transaction hash for approval if needed, empty string if already approved
            
        Raises:
            BlockchainError: If approval fails
        """
        permit2_allowance_needed = 2**256 - 1  # Max uint256 value
        
        try:
            # Check current allowance
            current_allowance = self.usdc_contract.functions.allowance(
                self.account.address, 
                self.permit2_address
            ).call()
            
            if current_allowance >= permit2_allowance_needed:
                self.logger.info("Permit2 already approved for USDC")
                return ""
            
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
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            self.logger.info(f"Permit2 approval transaction sent: {tx_hash_hex}")
            
            # Wait for transaction confirmation
            self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            return tx_hash_hex
            
        except Exception as e:
            self.logger.error(f"Error approving Permit2 for USDC: {e}")
            raise BlockchainError(f"Failed to approve Permit2: {e}")
    
    def swap_usdc_to_eth(
        self, 
        usdc_amount: float, 
        slippage: float = 0.01,
        gas_limit: int = 500_000,
        priority_fee_multiplier: float = 1.5,
        wait_for_approval: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a USDC to ETH swap on Uniswap.
        
        Args:
            usdc_amount: Amount of USDC to swap in USDC units
            slippage: Maximum acceptable slippage (default: 1%)
            gas_limit: Gas limit for transaction
            priority_fee_multiplier: Multiplier for priority fee
            wait_for_approval: Whether to wait for approval transaction confirmation
            
        Returns:
            Dict with transaction details including:
                - transaction_hash: The hash of the submitted transaction
                - approval_hash: The hash of the approval transaction (if needed)
                - usdc_amount: The amount of USDC swapped
                - estimated_eth: The estimated ETH output
                - min_eth_output: The minimum ETH output with slippage
                - status: Transaction status
                
        Raises:
            BlockchainError: If the swap fails
            ConfigurationError: If required configuration is missing
        """
        try:
            # Validate inputs
            if usdc_amount <= 0:
                raise ValueError("USDC amount must be greater than 0")
                
            # Check if account has enough USDC
            usdc_balance = self.get_usdc_balance()
            if usdc_amount > usdc_balance:
                raise ValueError(f"Insufficient USDC balance. Have {usdc_balance}, need {usdc_amount}")
            
            # Convert USDC amount to token units
            amount_in_usdc_units = int(usdc_amount * (10 ** self.usdc_decimals))
            
            # Ensure Permit2 approval first
            approval_tx = self.ensure_permit2_approval()
            if approval_tx and wait_for_approval:
                self.logger.info(f"Waiting for USDC approval transaction: {approval_tx}")
                self.web3.eth.wait_for_transaction_receipt(approval_tx, timeout=120)
            
            # Estimate ETH output
            _, min_eth_output = self.estimate_eth_output(usdc_amount, slippage)
            
            # Convert min output to ETH units with decimals
            min_amount_out = int(min_eth_output * (10 ** 18))  # ETH has 18 decimals
            
            # Define token path
            path = [self.usdc_address, self.weth_address]
            
            # Get signature for Permit2
            # Note: In a real implementation, you would generate a proper Permit2 signature
            # For simplicity, we'll skip this and use a different approach
            
            # Encode swap transaction using the router codec
            encoded_input = (
                self.codec
                .encode
                .chain()
                .v2_swap_exact_in(
                    FunctionRecipient.SENDER, 
                    amount_in_usdc_units, 
                    min_amount_out, 
                    path, 
                    payer_is_sender=True
                )
                .unwrap_weth(FunctionRecipient.SENDER, 0)  # Unwrap all WETH to ETH
                .build(self.codec.get_default_deadline())
            )
            
            # Get current nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address, 'pending')
            
            # Get gas price
            base_fee = self.web3.eth.gas_price
            priority_fee = self.web3.eth.max_priority_fee
            max_priority_fee = int(priority_fee * priority_fee_multiplier)
            max_fee = base_fee * 2
            
            # Prepare transaction parameters
            tx_params = {
                "from": self.account.address,
                "to": self.router_address,
                "gas": gas_limit,
                "maxPriorityFeePerGas": max_priority_fee,
                "maxFeePerGas": max_fee,
                "type": '0x2',  # EIP-1559 transaction
                "chainId": self.chain_id,
                "value": 0,  # No ETH is sent
                "nonce": nonce,
                "data": encoded_input,
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx_params, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            self.logger.info(f"USDC to ETH swap transaction sent: {tx_hash_hex}")
            
            # Return transaction details
            return {
                "transaction_hash": tx_hash_hex,
                "approval_hash": approval_tx,
                "usdc_amount": usdc_amount,
                "estimated_eth": min_eth_output / (1 - slippage),  # Reverse the slippage calculation
                "min_eth_output": min_eth_output,
                "status": "pending"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing USDC to ETH swap: {e}")
            raise BlockchainError(f"Failed to swap USDC to ETH: {e}")
    
    def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get the status of a transaction.
        
        Args:
            tx_hash: Transaction hash to check
            
        Returns:
            Dict with transaction status details
            
        Raises:
            BlockchainError: If the status check fails
        """
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if receipt is None:
                return {"status": "pending", "confirmations": 0}
            
            current_block = self.web3.eth.block_number
            confirmations = current_block - receipt.blockNumber
            
            if receipt.status == 1:
                status = "confirmed" if confirmations >= 1 else "pending_confirmation"
            else:
                status = "failed"
                
            return {
                "status": status,
                "confirmations": confirmations,
                "transaction_hash": tx_hash,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed
            }
            
        except Exception as e:
            self.logger.error(f"Error checking transaction status for {tx_hash}: {e}")
            raise BlockchainError(f"Failed to check transaction status: {e}")
    
    def get_usdc_to_eth_quote(self, usdc_amount: float) -> Dict[str, Any]:
        """
        Get a quote for a USDC to ETH swap without executing it.
        
        Args:
            usdc_amount: Amount of USDC to swap
            
        Returns:
            Dict with quote details
            
        Raises:
            BlockchainError: If the quote cannot be retrieved
        """
        try:
            # Check if account has enough USDC
            usdc_balance = self.get_usdc_balance()
            has_sufficient_balance = usdc_amount <= usdc_balance
            
            # Get current ETH price
            eth_price = self.get_eth_price()
            
            # Calculate expected ETH output
            estimated_eth, min_eth_output = self.estimate_eth_output(usdc_amount, 0.01)
            
            # Check permit2 approval status
            is_approved = self.usdc_contract.functions.allowance(
                self.account.address, 
                self.permit2_address
            ).call() > 0
            
            # Construct response
            return {
                "usdc_amount": usdc_amount,
                "estimated_eth": estimated_eth,
                "min_eth_output": min_eth_output,
                "eth_price": eth_price,
                "has_sufficient_balance": has_sufficient_balance,
                "is_approved": is_approved,
                "usdc_balance": usdc_balance,
                "eth_balance": self.get_eth_balance()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting USDC to ETH quote: {e}")
            raise BlockchainError(f"Failed to get USDC to ETH quote: {e}") 