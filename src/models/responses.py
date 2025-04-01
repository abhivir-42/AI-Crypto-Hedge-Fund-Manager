#!/usr/bin/env python3
"""
Response Models

This module defines the response models used by the agents in the system.
These models represent structured data exchanged between agents.
"""

from typing import List, Optional, Dict, Any
from uagents import Model


class CoinResponse(Model):
    """
    Response model with cryptocurrency market data.
    
    Attributes:
        name: Name of the cryptocurrency
        symbol: Symbol of the cryptocurrency (e.g., BTC, ETH)
        current_price: Current price in USD
        market_cap: Market capitalization in USD
        total_volume: Trading volume in USD
        price_change_24h: Price change in last 24 hours (percentage)
    """
    name: str
    symbol: str
    current_price: float
    market_cap: float
    total_volume: float
    price_change_24h: float


class CryptonewsResponse(Model):
    """
    Response model with cryptocurrency news updates.
    
    Attributes:
        cryptoupdates: String containing recent crypto news
    """
    cryptoupdates: str


class ASI1Response(Model):
    """
    Response model from ASI1 reasoning agent with trading decision.
    
    Attributes:
        decision: The trading decision (BUY/SELL/HOLD)
    """
    decision: str


class FearGreedData(Model):
    """
    Model representing Fear & Greed Index data for a single day.
    
    Attributes:
        value: Numeric value of the index (0-100)
        value_classification: Classification of the value (e.g., Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
        timestamp: ISO format timestamp
    """
    value: float
    value_classification: str
    timestamp: str


class FGIResponse(Model):
    """
    Response model with Fear & Greed Index data.
    
    Attributes:
        data: List of FearGreedData objects
        status: Status of the response (e.g., "success")
        timestamp: ISO format timestamp
    """
    data: List[FearGreedData]
    status: str
    timestamp: str


class SwaplandResponse(Model):
    """
    Model for swap responses.
    
    Attributes:
        status: The status of the swap operation
    """
    status: str


class NewsResponse(Model):
    """Response with cryptocurrency news articles."""
    articles: List[Dict[str, Any]]
    status: str = "ok"


class PaymentRequest(Model):
    """Payment request details sent by the reward agent."""
    wallet_address: str
    amount: int
    denom: str


class TransactionInfo(Model):
    """Transaction information sent to confirm a payment."""
    tx_hash: str


class PaymentReceived(Model):
    """Confirmation that a payment was received."""
    status: str


class TopupResponse(Model):
    """Response to a token top-up request."""
    status: str
    transaction_hash: Optional[str] = None
    balance: Optional[float] = None


class SwapResponse(Model):
    """Response to a swap request."""
    status: str  # "success", "error", "pending"
    message: Optional[str] = None
    transaction_hash: Optional[str] = None 