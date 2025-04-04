#!/usr/bin/env python3
"""
Crypto Trading Signal Agent

This module implements the main agent for the Crypto Trading Agent System,
which orchestrates communication between specialized agents to provide
cryptocurrency trading signals (BUY/SELL/HOLD) based on market data,
news, and sentiment analysis.
"""

import atexit
import logging
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import os
from dotenv import load_dotenv
from uagents import Agent, Context

# Use relative imports
from ..models.requests import (
    CoinRequest, CryptonewsRequest, ASI1Request, FGIRequest
)
from ..models.responses import (
    CoinResponse, CryptonewsResponse, ASI1Response, FGIResponse, FearGreedData
)

# Configure logging
logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception class for agent-related errors."""
    pass


class AgentCommunicationError(AgentError):
    """Exception raised when communication between agents fails."""
    pass


class AgentConfigurationError(AgentError):
    """Exception raised when agent configuration is invalid."""
    pass


class BlockchainType(str, Enum):
    """Supported blockchain types for data requests."""
    ETHEREUM = "ethereum"
    BASE = "base"
    BITCOIN = "bitcoin"
    MATIC = "matic-network"


class InvestorType(str, Enum):
    """Investor types for personalized recommendations."""
    LONG_TERM = "long-term"
    SHORT_TERM = "short-term"
    SPECULATE = "speculate"


class RiskStrategy(str, Enum):
    """Risk strategies for personalized recommendations."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"


class TradingSignal(str, Enum):
    """Trading signals that can be generated by the system."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class AgentState:
    """Container for the agent's state during a trading analysis cycle."""
    network: BlockchainType = BlockchainType.BITCOIN
    coin_information: Optional[CoinResponse] = None
    cryptonews_info: Optional[CryptonewsResponse] = None
    fgi_data: Optional[FGIResponse] = None
    investor_type: Optional[InvestorType] = None
    risk_strategy: Optional[RiskStrategy] = None
    user_reason: Optional[str] = None


class MainCryptoAgent:
    """
    Main orchestration agent for the Crypto Trading System.
    
    This agent coordinates communication between specialized agents for market data,
    news, sentiment analysis, and trading signal generation.
    """
    
    def __init__(self):
        """Initialize the main agent."""
        # Load environment variables
        load_dotenv()
        
        # Agent addresses (loaded from environment variables with defaults)
        self.COIN_AGENT = os.getenv("COIN_AGENT_ADDRESS", "agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq")
        self.FGI_AGENT = os.getenv("FGI_AGENT_ADDRESS", "agent1q248t3vk8f60y3dqsr2nzu93h7tpz26dy62l4ejdtl9ces2sml8ask8zmdp")
        self.REASON_AGENT = os.getenv("REASON_AGENT_ADDRESS", "agent1qgrvpwve5f9emqes3vux9uwkstpjcl5ykmfe6sd8wh2fyhpwrptssttez3y")
        self.CRYPTONEWS_AGENT = os.getenv("CRYPTONEWS_AGENT_ADDRESS", "agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9")
        
        # Create the agent
        agent_seed = os.getenv("MAIN_AGENT_SEED", "this_is_main_agent_to_run")
        agent_name = os.getenv("MAIN_AGENT_NAME", "SentimentBased CryptoSellAlerts")
        agent_port = int(os.getenv("MAIN_AGENT_PORT", "8017"))
        
        self.agent = Agent(
            name=agent_name,
            port=agent_port,
            seed=agent_seed,
            endpoint=[f"http://127.0.0.1:{agent_port}/submit"],
        )
        
        # Initialize agent state
        self.state = AgentState()
        
        # Register event handlers
        self.agent.on_event("startup")(self.introduce_agent)
        self.agent.on_interval(period=24 * 60 * 60.0)(self.check_coin)
        self.agent.on_message(model=CoinResponse)(self.handle_coin_response)
        self.agent.on_message(model=CryptonewsResponse)(self.handle_cryptonews_response)
        self.agent.on_message(model=FGIResponse)(self.handle_fgi_response)
        self.agent.on_message(model=ASI1Response)(self.handle_asi1_response)
        
        # Register exit handler
        atexit.register(self.log_and_exit)
        
        # Set global exception handler
        sys.excepthook = self.handle_unexpected_exception
        
        logger.info("Main agent initialized")
    
    def log_and_exit(self) -> None:
        """Log when the script is terminated."""
        logger.warning("Script terminated unexpectedly")
    
    def handle_unexpected_exception(self, exc_type: type, exc_value: Exception, exc_traceback: any) -> None:
        """
        Global exception handler for uncaught exceptions.
        
        Args:
            exc_type: Type of the exception
            exc_value: Exception instance
            exc_traceback: Traceback object
        """
        logger.critical("Uncaught Exception:", exc_info=(exc_type, exc_value, exc_traceback))
    
    async def introduce_agent(self, ctx: Context) -> None:
        """
        Initialize the agent and log startup information.
        
        Args:
            ctx: Agent context
        """
        logger.info(f"Agent started: {ctx.agent.address}")
        print(f"Hello! I'm {self.agent.name} and my address is {self.agent.address}.")
        logger.info("Agent startup complete.")
    
    async def get_blockchain_input(self) -> BlockchainType:
        """
        Get and validate blockchain input from the user.
        
        Returns:
            BlockchainType: Selected blockchain
            
        Raises:
            SystemExit: If user input is invalid
        """
        print(f"Please, confirm the chain to request the data from")
        chain_input = input("Blockchain [ethereum/base/bitcoin/matic-network]? ").lower()
        
        try:
            # Validate the input is a supported blockchain
            if chain_input not in [e.value for e in BlockchainType]:
                print("Unsupported blockchain selected")
                sys.exit(1)
            return BlockchainType(chain_input)
        except ValueError:
            print("Aborted")
            sys.exit(1)
    
    async def get_investor_profile(self) -> InvestorType:
        """
        Get and validate investor profile input from the user.
        
        Returns:
            InvestorType: Selected investor profile
            
        Raises:
            SystemExit: If user input is invalid
        """
        print(f"Please, confirm if you long-term or short-term investor?")
        investor_input = input("Investor [long-term/short-term/speculate]: ").lower()
        
        try:
            if investor_input not in [e.value for e in InvestorType]:
                print("Unsupported investor type selected")
                sys.exit(1)
            return InvestorType(investor_input)
        except ValueError:
            print("Aborted")
            sys.exit(1)
    
    async def get_risk_strategy(self) -> RiskStrategy:
        """
        Get and validate risk strategy input from the user.
        
        Returns:
            RiskStrategy: Selected risk strategy
            
        Raises:
            SystemExit: If user input is invalid
        """
        print(f"Please, confirm your risk strategy for investments?")
        risk_input = input("Risk strategy [conservative/balanced/aggressive/speculative]: ").lower()
        
        try:
            if risk_input not in [e.value for e in RiskStrategy]:
                print("Unsupported risk strategy selected")
                sys.exit(1)
            return RiskStrategy(risk_input)
        except ValueError:
            print("Aborted")
            sys.exit(1)
    
    async def check_coin(self, ctx: Context) -> None:
        """
        Request market data for the monitored coin once a day.
        
        Args:
            ctx: Agent context
        """
        try:
            # Get blockchain selection from user
            blockchain = await self.get_blockchain_input()
            self.state.network = blockchain
            
            # Request coin information
            await ctx.send(self.COIN_AGENT, CoinRequest(blockchain=blockchain.value))
            logger.info(f"Sent CoinRequest for {blockchain.value}")
        except Exception as e:
            logger.error(f"Failed to send request: {e}")
            raise AgentCommunicationError(f"Failed to communicate with Coin Agent: {e}")
    
    async def handle_coin_response(self, ctx: Context, sender: str, msg: CoinResponse) -> None:
        """
        Handle coin market data and request crypto news.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Coin market data response
        """
        logger.info(f"Received CoinResponse from {sender}")
        
        # Update agent state with coin information
        self.state.coin_information = msg
        
        try:
            # Request crypto news
            await ctx.send(self.CRYPTONEWS_AGENT, CryptonewsRequest())
            logger.info("Sent CryptonewsRequest")
        except Exception as e:
            logger.error(f"Error sending CryptonewsRequest: {e}")
            raise AgentCommunicationError(f"Failed to communicate with Cryptonews Agent: {e}")
    
    async def handle_cryptonews_response(self, ctx: Context, sender: str, msg: CryptonewsResponse) -> None:
        """
        Handle cryptonews market data and request Fear & Greed Index.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Crypto news response
        """
        logger.info(f"Received CryptonewsResponse from {sender}")
        
        # Update agent state with crypto news
        self.state.cryptonews_info = msg
        
        try:
            # Request Fear & Greed Index data
            await ctx.send(self.FGI_AGENT, FGIRequest())
            logger.info("Sent FGIRequest")
        except Exception as e:
            logger.error(f"Error sending FGIRequest: {e}")
            raise AgentCommunicationError(f"Failed to communicate with FGI Agent: {e}")
    
    async def handle_fgi_response(self, ctx: Context, sender: str, msg: FGIResponse) -> None:
        """
        Analyze FGI data and determine whether to issue a SELL/BUY or HOLD alert.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Fear & Greed Index response
        """
        logger.info(f"Received FGIResponse from {sender}")
        
        # Update agent state with FGI data
        self.state.fgi_data = msg
        
        try:
            # Get user investor profile and risk strategy
            self.state.investor_type = await self.get_investor_profile()
            self.state.risk_strategy = await self.get_risk_strategy()
            
            # Get additional context from user
            self.state.user_reason = input("Any particular reason why you would like to perform Buy/Sell/Hold action? ").lower()
            
            # Construct the AI prompt
            prompt = self.construct_analysis_prompt(
                self.state.fgi_data,
                self.state.coin_information,
                self.state.investor_type,
                self.state.risk_strategy,
                self.state.cryptonews_info,
                self.state.network
            )
            
            # Send prompt to ASI1 reasoning agent
            await ctx.send(self.REASON_AGENT, ASI1Request(query=prompt))
            logger.info("Sent ASI1Request for trading signal")
        except Exception as e:
            logger.error(f"Error querying ASI1 model: {e}")
            raise AgentCommunicationError(f"Failed to communicate with ASI1 Reasoning Agent: {e}")
    
    def construct_analysis_prompt(
        self,
        fgi_data: FGIResponse, 
        coin_data: CoinResponse, 
        investor_type: InvestorType, 
        risk_strategy: RiskStrategy,
        crypto_news: CryptonewsResponse,
        network: BlockchainType
    ) -> str:
        """
        Construct a prompt for the ASI1 reasoning agent.
        
        Args:
            fgi_data: Fear & Greed Index data
            coin_data: Cryptocurrency market data
            investor_type: User's investor profile
            risk_strategy: User's risk strategy
            crypto_news: Crypto news data
            network: Selected blockchain network
            
        Returns:
            str: Formatted prompt for ASI1 analysis
        """
        return f'''    
        Consider the following factors:
        
        Fear Greed Index Analysis - {fgi_data}
        Coin Market Data - {coin_data}
        User's type of investing - {investor_type}
        User's risk strategy - {risk_strategy}
        
        Most recent crypto news - {crypto_news}
        
        You are a crypto expert, who is assisting the user to make the most meaningful decisions, to gain the most revenue. 
        Given the following information, respond with one word, either "SELL", "BUY" or "HOLD" native token from {network.value} network.
        '''
    
    async def handle_asi1_response(self, ctx: Context, sender: str, msg: ASI1Response) -> None:
        """
        Handle the response from the ASI1 reasoning agent and take appropriate action.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: ASI1 reasoning response with trading decision
        """
        logger.info(f"Received ASI1Response from {sender} with decision: {msg.decision}")
        
        # Process the decision
        if TradingSignal.SELL.value in msg.decision:
            logger.critical("SELL SIGNAL DETECTED!")
            print("SELL")
            # Future enhancement: start search and run of ETH to USDC swap agent
        elif TradingSignal.BUY.value in msg.decision:
            logger.critical("BUY SIGNAL DETECTED!")
            print("BUY")
            # Future enhancement: start search and run of USDC to ETH swap agent
        else:
            logger.info("HOLD decision received.")
            print("HOLD")
    
    def run(self) -> None:
        """Run the main agent."""
        try:
            logger.info("Starting the agent...")
            self.agent.run()
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
        except Exception as e:
            logger.critical(f"Error starting the agent: {e}")
            sys.exit(1)


# Application entry point
if __name__ == "__main__":
    try:
        # Configure root logger
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            handlers=[
                logging.StreamHandler(stream=sys.stdout),
                logging.FileHandler(filename="main_agent.log", mode="a"),
            ],
        )
        
        # Create and run the main agent
        main_agent = MainCryptoAgent()
        main_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 