#!/usr/bin/env python3
"""
Request Models

This module defines the request models used by the agents in the system.
These models represent structured data exchanged between agents.
"""

from typing import Optional, List
from uagents import Model


class CoinRequest(Model):
    """Request for cryptocurrency information."""
    blockchain: str


class CryptonewsRequest(Model):
    """
    Request model for cryptocurrency news.
    
    Attributes:
        limit: Maximum number of news items to retrieve
    """
    limit: Optional[int] = 1


class ASI1Request(Model):
    """
    Request model for ASI1 reasoning agent.
    
    Attributes:
        query: The analysis query with market data
    """
    query: str


class FGIRequest(Model):
    """Request for Fear and Greed Index information."""
    limit: Optional[int] = 1
    ready: str = "ready"


class SwaplandRequest(Model):
    """
    Model for swap requests.
    
    Attributes:
        blockchain: The blockchain to perform the swap on
        signal: The trading signal (BUY/SELL/HOLD)
        amount: The amount to swap
    """
    blockchain: str
    signal: str
    amount: float


class NewsRequest(Model):
    """Request for cryptocurrency news."""
    coin: Optional[str] = None
    ready: str = "ready"


class PaymentInquiry(Model):
    """Payment inquiry message to start a payment process."""
    ready: str = "ready"


class RewardRequest(Model):
    """Request for reward information."""
    ready: str = "ready"


class TopupRequest(Model):
    """Request for token top-up."""
    wallet_address: str
    amount: Optional[int] = None


class SwapRequest(Model):
    """Request for cryptocurrency swap."""
    blockchain: str
    signal: str  # "buy" or "sell"
    amount: float 