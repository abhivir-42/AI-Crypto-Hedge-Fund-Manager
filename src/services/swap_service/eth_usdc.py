#!/usr/bin/env python3
"""
ETH to USDC Swap Service

This module provides functionality for swapping ETH to USDC on Uniswap
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


class ETHUSDCSwapService:
    """
    Service for handling ETH to USDC swap operations on Uniswap.
    """
    
    def __init__(self, ethereum_rpc_url: str = None, private_key: str = None):
        """
        Initialize the ETH to USDC swap service.
        
        Args:
            ethereum_rpc_url: Optional RPC URL override
            private_key: Optional private key override
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Initialize logger
        self.logger = logging.getLogger("service.swap.eth_usdc")
        
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
    
    def estimate_usdc_output(self, eth_amount: float, slippage: float = 0.01) -> Tuple[float, float]:
        """
        Estimate the amount of USDC that will be received for a given ETH input.
        
        Args:
            eth_amount: Amount of ETH to swap
            slippage: Maximum acceptable slippage (default: 1%)
            
        Returns:
            Tuple[float, float]: Estimated USDC output and minimum USDC output with slippage
            
        Raises:
            BlockchainError: If the estimation fails
        """
        try:
            # Get current ETH price
            eth_price = self.get_eth_price()
            
            # Calculate expected USDC output (ETH amount * price)
            estimated_usdc = eth_amount * eth_price
            
            # Apply slippage to get minimum output
            min_usdc_output = estimated_usdc * (1 - slippage)
            
            self.logger.info(f"Estimated {eth_amount} ETH -> ~{estimated_usdc:.2f} USDC (min: {min_usdc_output:.2f})")
            
            return estimated_usdc, min_usdc_output
            
        except Exception as e:
            self.logger.error(f"Error estimating USDC output: {e}")
            raise BlockchainError(f"Failed to estimate USDC output: {e}")
    
    def swap_eth_to_usdc(
        self, 
        eth_amount: float, 
        slippage: float = 0.01,
        gas_limit: int = 500_000,
        priority_fee_multiplier: float = 1.5
    ) -> Dict[str, Any]:
        """
        Execute an ETH to USDC swap on Uniswap.
        
        Args:
            eth_amount: Amount of ETH to swap in ether units
            slippage: Maximum acceptable slippage (default: 1%)
            gas_limit: Gas limit for transaction
            priority_fee_multiplier: Multiplier for priority fee
            
        Returns:
            Dict with transaction details including:
                - transaction_hash: The hash of the submitted transaction
                - eth_amount: The amount of ETH swapped
                - estimated_usdc: The estimated USDC output
                - min_usdc_output: The minimum USDC output with slippage
                - status: Transaction status
                
        Raises:
            BlockchainError: If the swap fails
            ConfigurationError: If required configuration is missing
        """
        try:
            # Validate inputs
            if eth_amount <= 0:
                raise ValueError("ETH amount must be greater than 0")
                
            # Check if account has enough ETH
            eth_balance = self.get_eth_balance()
            if eth_amount > eth_balance:
                raise ValueError(f"Insufficient ETH balance. Have {eth_balance}, need {eth_amount}")
            
            # Convert ETH amount to wei
            amount_in_wei = self.web3.to_wei(eth_amount, 'ether')
            
            # Estimate USDC output
            _, min_usdc_output = self.estimate_usdc_output(eth_amount, slippage)
            
            # Convert min output to USDC units with decimals
            min_amount_out = int(min_usdc_output * (10 ** self.usdc_decimals))
            
            # Define token path
            path = [self.weth_address, self.usdc_address]
            
            # Encode swap transaction using the router codec
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
            
            # Get current nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
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
                "value": amount_in_wei,
                "nonce": nonce,
                "data": encoded_input,
            }
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx_params, self.account.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = self.web3.to_hex(tx_hash)
            
            self.logger.info(f"ETH to USDC swap transaction sent: {tx_hash_hex}")
            
            # Return transaction details
            return {
                "transaction_hash": tx_hash_hex,
                "eth_amount": eth_amount,
                "estimated_usdc": min_usdc_output / (1 - slippage),  # Reverse the slippage calculation
                "min_usdc_output": min_usdc_output,
                "status": "pending"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing ETH to USDC swap: {e}")
            raise BlockchainError(f"Failed to swap ETH to USDC: {e}")
    
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