"""
ASI1 LLM Integration Service

This module provides a robust interface for interacting with the ASI1 language 
model API, specifically designed for analyzing cryptocurrency market data and 
generating trading signals.
"""

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import backoff
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, validator

# Configure logging
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception class for LLM-related errors."""
    pass


class APIKeyError(LLMError):
    """Exception raised when there's an issue with the API key."""
    pass


class APIConnectionError(LLMError):
    """Exception raised when connection to the API fails."""
    pass


class APIResponseError(LLMError):
    """Exception raised when the API response is invalid or unexpected."""
    pass


class RateLimitError(LLMError):
    """Exception raised when the API rate limit is exceeded."""
    pass


class ValidationFailedError(LLMError):
    """Exception raised when response validation fails."""
    pass


class Message(BaseModel):
    """Model for a message in the conversation."""
    role: str
    content: str


class LLMResponse(BaseModel):
    """Model for validating LLM API responses."""
    choices: List[Dict[str, Any]]
    
    @validator('choices')
    def validate_choices(cls, choices):
        """Validate that the choices field contains at least one item with the expected structure."""
        if not choices or len(choices) == 0:
            raise ValueError("No choices in response")
        
        if "message" not in choices[0]:
            raise ValueError("No message in first choice")
            
        if "content" not in choices[0]["message"]:
            raise ValueError("No content in message")
            
        return choices


class TradingSignal(Enum):
    """Enum representing possible trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    UNKNOWN = "UNKNOWN"


@dataclass
class ASI1Config:
    """Configuration for the ASI1 LLM service."""
    api_url: str = "https://api.asi1.ai/v1/chat/completions"
    model: str = "asi1-mini"
    api_key_env_var: str = "ASI1_API_KEY"
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout: float = 30.0
    conversation_id: Optional[str] = None


class ASI1Service:
    """
    Service for interacting with the ASI1 language model API.
    
    This class provides functionality to query the ASI1 LLM API
    with robust error handling, retry mechanisms, and response validation.
    """
    
    def __init__(self, config: Optional[ASI1Config] = None):
        """
        Initialize the ASI1 LLM service.
        
        Args:
            config: Configuration for the service
                   (default: ASI1Config with default values)
        """
        # Load environment variables
        load_dotenv()
        
        # Set configuration
        self.config = config or ASI1Config()
        
        # Get API key from environment
        self.api_key = os.getenv(self.config.api_key_env_var)
        if not self.api_key:
            logger.critical(f"API key not found in environment variable: {self.config.api_key_env_var}")
            raise APIKeyError(f"Missing API key. Set the {self.config.api_key_env_var} environment variable.")
        
        # Set headers for API requests
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info("ASI1 LLM service initialized")
    
    @backoff.on_exception(
        backoff.expo,
        (APIConnectionError, RateLimitError),
        max_tries=lambda self: self.config.max_retries,
        on_backoff=lambda details: logger.warning(
            f"Retrying API call (attempt {details['tries']}/{self.config.max_retries})"
        )
    )
    def query_llm(self, query: str) -> str:
        """
        Query the ASI1 LLM with a prompt and get the response.
        
        This method includes automatic retries with exponential backoff
        for connection errors and rate limit errors.
        
        Args:
            query: The prompt to send to the language model
            
        Returns:
            str: The response from the language model
            
        Raises:
            APIKeyError: If the API key is invalid
            APIConnectionError: If connection to the API fails
            APIResponseError: If the API response is invalid
            RateLimitError: If the API rate limit is exceeded
            ValidationFailedError: If response validation fails
        """
        logger.info(f"Querying ASI1 LLM with prompt (length: {len(query)} chars)")
        
        # Prepare the request data
        data = {
            "messages": [{"role": "user", "content": query}],
            "conversationId": self.config.conversation_id,
            "model": self.config.model
        }
        
        try:
            # Send the request to the API
            logger.debug(f"Sending request to {self.config.api_url}")
            start_time = time.time()
            
            response = requests.post(
                self.config.api_url,
                headers=self.headers,
                json=data,
                timeout=self.config.timeout
            )
            
            request_time = time.time() - start_time
            logger.debug(f"Request completed in {request_time:.2f} seconds")
            
            # Check for common HTTP errors
            if response.status_code == 401:
                logger.error("API key unauthorized")
                raise APIKeyError("Invalid API key")
            
            elif response.status_code == 429:
                logger.warning("API rate limit exceeded")
                raise RateLimitError("API rate limit exceeded, retrying with backoff")
            
            elif response.status_code != 200:
                logger.error(f"API returned error status code: {response.status_code}")
                raise APIResponseError(f"API returned error: {response.status_code} - {response.text}")
            
            # Parse the response
            output = response.json()
            
            # Validate the response structure
            try:
                validated_response = LLMResponse(**output)
                content = validated_response.choices[0]["message"]["content"]
                logger.info(f"Received valid response (length: {len(content)} chars)")
                return content
            
            except ValidationError as e:
                logger.error(f"Response validation failed: {e}")
                raise ValidationFailedError(f"API response validation failed: {e}")
            
            except (KeyError, IndexError) as e:
                logger.error(f"Unexpected response structure: {e}")
                raise APIResponseError(f"Unexpected response structure: {e}")
        
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after {self.config.timeout} seconds")
            raise APIConnectionError(f"Request timed out after {self.config.timeout} seconds")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise APIConnectionError(f"Failed to connect to ASI1 API: {e}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise APIConnectionError(f"Request failed: {e}")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {e}")
            raise APIResponseError(f"Invalid JSON response: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise LLMError(f"Unexpected error: {e}")
    
    def extract_trading_signal(self, response: str) -> TradingSignal:
        """
        Extract a trading signal (BUY/SELL/HOLD) from the LLM response.
        
        Args:
            response: The response from the language model
            
        Returns:
            TradingSignal: The extracted trading signal
        """
        response_upper = response.upper()
        
        if "BUY" in response_upper:
            logger.info("Extracted BUY signal from response")
            return TradingSignal.BUY
        
        elif "SELL" in response_upper:
            logger.info("Extracted SELL signal from response")
            return TradingSignal.SELL
        
        elif "HOLD" in response_upper:
            logger.info("Extracted HOLD signal from response")
            return TradingSignal.HOLD
        
        else:
            logger.warning(f"Could not extract clear trading signal from response: {response}")
            return TradingSignal.UNKNOWN
    
    def analyze_market_data(
        self,
        coin_data: Dict[str, Any],
        fgi_data: Dict[str, Any],
        news_data: Dict[str, Any],
        investor_type: str,
        risk_strategy: str,
        blockchain: str
    ) -> TradingSignal:
        """
        Analyze market data and generate a trading signal.
        
        This high-level method combines market data into a prompt,
        sends it to the LLM, and extracts a trading signal from the response.
        
        Args:
            coin_data: Coin market data
            fgi_data: Fear & Greed Index data
            news_data: Cryptocurrency news data
            investor_type: Type of investor (e.g., "long-term", "short-term")
            risk_strategy: Risk strategy (e.g., "conservative", "aggressive")
            blockchain: The blockchain network
            
        Returns:
            TradingSignal: The recommended trading action
        """
        # Construct the prompt
        prompt = f"""    
        Consider the following factors:
        
        Fear Greed Index Analysis - {fgi_data}
        Coin Market Data - {coin_data}
        User's type of investing - {investor_type}
        User's risk strategy - {risk_strategy}
        
        Most recent crypto news - {news_data}
        
        You are a crypto expert, who is assisting the user to make the most meaningful decisions, to gain the most revenue. 
        Given the following information, respond with one word, either "SELL", "BUY" or "HOLD" native token from {blockchain} network.
        """
        
        # Query the LLM and extract the trading signal
        response = self.query_llm(prompt)
        return self.extract_trading_signal(response) 