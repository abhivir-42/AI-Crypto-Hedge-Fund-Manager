# Improved ASI1 LLM Integration

This document provides an improved implementation of the ASI1 LLM integration with better error handling, type annotations, retry mechanisms, API response validation, environment variable management, and comprehensive logging.

## Improved LLM Swapfinder Module

```python
#!/usr/bin/env python3
"""
ASI1 LLM Integration Module

This module provides a robust interface for interacting with the ASI1 language 
model API, specifically designed for analyzing cryptocurrency market data and 
generating trading signals.

The module includes retry mechanisms, error handling, response validation,
and comprehensive logging to ensure reliable API interactions.
"""

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import backoff
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler(filename="asi1_llm_service.log", mode="a"),
    ],
)
logger = logging.getLogger("asi1_llm_service")


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


# Example usage
if __name__ == "__main__":
    try:
        # Create the ASI1 service
        asi1_service = ASI1Service()
        
        # Simple test query
        test_prompt = "What's the current sentiment in the crypto market?"
        response = asi1_service.query_llm(test_prompt)
        
        print("Response from ASI1 LLM:")
        print(response)
        
    except LLMError as e:
        logger.critical(f"LLM error: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        sys.exit(1)
```

## Improved ASI1 Agent Module

```python
#!/usr/bin/env python3
"""
ASI1 Reasoning Agent

This module implements an agent that provides AI-powered analysis of
cryptocurrency market data to generate trading signals (BUY/SELL/HOLD).
It uses the ASI1 language model to process complex market conditions
and make informed trading recommendations.
"""

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from dotenv import load_dotenv
from uagents import Agent, Context, Model

# Import the improved ASI1 service
from .llm_service import ASI1Service, LLMError, TradingSignal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler(filename="asi1_agent.log", mode="a"),
    ],
)
logger = logging.getLogger("asi1_agent")


class ASI1Request(Model):
    """
    Model for reasoning requests received by the agent.
    
    Attributes:
        query: The analysis query with market data
    """
    query: str


class ASI1Response(Model):
    """
    Model for reasoning responses sent by the agent.
    
    Attributes:
        decision: The trading decision (BUY/SELL/HOLD)
    """
    decision: str


@dataclass
class AgentConfig:
    """Configuration for the ASI1 agent."""
    name: str = "ASI1 Reasoning agent for crypto trading signals"
    port: int = 8018
    seed_env_var: str = "ASI1_AGENT_SEED"
    default_seed: str = "asi1_reasoning_agent_seed_phrase"
    endpoint: str = "http://127.0.0.1:8018/submit"


class ASI1ReasoningAgent:
    """
    Agent that provides AI-powered cryptocurrency trading signals.
    
    This agent uses the ASI1 language model to analyze market data
    and generate informed trading recommendations.
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the ASI1 reasoning agent.
        
        Args:
            config: Configuration for the agent
                  (default: AgentConfig with default values)
        """
        # Load environment variables
        load_dotenv()
        
        # Set configuration
        self.config = config or AgentConfig()
        
        # Get agent seed from environment or use default
        seed = os.getenv(self.config.seed_env_var, self.config.default_seed)
        
        # Initialize the agent
        self.agent = Agent(
            name=self.config.name,
            port=self.config.port,
            seed=seed,
            endpoint=[self.config.endpoint],
        )
        
        # Initialize the ASI1 service
        self.asi1_service = ASI1Service()
        
        # Register message handlers
        self.agent.on_event("startup")(self.on_startup)
        self.agent.on_message(model=ASI1Request)(self.handle_reasoning_request)
        
        logger.info("ASI1 reasoning agent initialized")
    
    async def on_startup(self, ctx: Context) -> None:
        """
        Handle agent startup event.
        
        Args:
            ctx: Agent context
        """
        logger.info(f"ASI1 Reasoning Agent started with address: {ctx.agent.address}")
        print(f"Hello! I'm {self.agent.name} and my address is {self.agent.address}.")
        logger.info("ASI1 Reasoning Agent startup complete")
    
    async def handle_reasoning_request(self, ctx: Context, sender: str, msg: ASI1Request) -> None:
        """
        Handle a reasoning request by analyzing market data and generating a trading signal.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: The reasoning request with market data
        """
        ctx.logger.info(f"Received request from {sender}: Analyzing crypto market data")
        
        try:
            # Query the ASI1 LLM with the provided prompt
            response = self.asi1_service.query_llm(msg.query)
            
            # Extract the trading signal from the response
            trading_signal = self.asi1_service.extract_trading_signal(response)
            
            # Log the result
            ctx.logger.info(f"Analysis complete. Trading signal: {trading_signal.value}")
            
            # Send the response back to the sender
            await ctx.send(sender, ASI1Response(decision=trading_signal.value))
            ctx.logger.info(f"Response sent to {sender}")
            
        except LLMError as e:
            # Handle LLM-related errors
            error_message = f"Error analyzing market data: {e}"
            ctx.logger.error(error_message)
            
            # Send error response
            await ctx.send(sender, ASI1Response(decision=f"ERROR: {str(e)}"))
            
        except Exception as e:
            # Handle unexpected errors
            error_message = f"Unexpected error: {e}"
            ctx.logger.error(error_message)
            
            # Send error response
            await ctx.send(sender, ASI1Response(decision=f"ERROR: {str(e)}"))
    
    def run(self) -> None:
        """Run the ASI1 reasoning agent."""
        try:
            logger.info("Starting ASI1 reasoning agent")
            self.agent.run()
        except KeyboardInterrupt:
            logger.info("ASI1 reasoning agent stopped by user")
        except Exception as e:
            logger.critical(f"Error running ASI1 reasoning agent: {e}")
            sys.exit(1)


# Application entry point
if __name__ == "__main__":
    try:
        # Create and run the ASI1 reasoning agent
        asi1_agent = ASI1ReasoningAgent()
        asi1_agent.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
```

## Key Improvements

The refactored ASI1 LLM integration includes several significant improvements:

1. **Enhanced Error Handling**:
   - Created a hierarchy of custom exception classes for different error types
   - Added detailed error handling for API connections, responses, and validation
   - Implemented proper error logging with meaningful messages
   - Added appropriate error recovery and fallback mechanisms

2. **Comprehensive Type Annotations**:
   - Added type hints for all functions, arguments, and return values
   - Used Pydantic models for request/response data validation
   - Implemented enums for standardized constants (like trading signals)
   - Created dataclasses for structured configuration

3. **Retry Mechanisms**:
   - Added automatic retries with exponential backoff for transient errors
   - Implemented specific handling for rate limiting
   - Added proper timeout handling for API requests
   - Included retry logging and statistics

4. **API Response Validation**:
   - Used Pydantic models to validate API responses
   - Added explicit validators for critical response fields
   - Implemented proper error handling for invalid responses
   - Included structured logging of validation failures

5. **Environment Variable Management**:
   - Used dotenv for loading environment variables
   - Added fallback default values for configuration
   - Implemented proper error handling for missing required variables
   - Created configuration classes for better organization

6. **Comprehensive Logging**:
   - Added structured logging with timestamps and log levels
   - Implemented both console and file logging
   - Added context-specific log messages
   - Included performance metrics in logging (request times)
   - Properly handled and logged errors at all levels

7. **Code Organization**:
   - Separated the LLM service from the agent implementation
   - Used classes to encapsulate related functionality
   - Created proper initialization and setup methods
   - Implemented a clean, modular design

8. **Additional Improvements**:
   - Added performance tracking for API requests
   - Implemented proper timeout handling
   - Added helper methods for common tasks (like extracting trading signals)
   - Included comprehensive documentation

These improvements make the ASI1 LLM integration more robust, maintainable, and reliable while providing better visibility into its operation through enhanced logging and error reporting. 