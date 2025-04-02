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
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from uagents import Agent, Context

# Use relative imports
from ..models.requests import ASI1Request
from ..models.responses import ASI1Response

# Import the improved ASI1 service
from ..services.llm_service import ASI1Service, LLMError, TradingSignal

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for the ASI1 agent."""
    name: str = "ASI1 Reasoning agent for crypto trading signals"
    port: int = 9018
    seed_env_var: str = "ASI1_AGENT_SEED"
    default_seed: str = "asi1_reasoning_agent_seed_phrase"
    endpoint: str = "http://127.0.0.1:9018/submit"


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
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="asi1_agent.log", mode="a"),
            ],
        )
        
        # Create and run the ASI1 reasoning agent
        asi1_agent = ASI1ReasoningAgent()
        asi1_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 