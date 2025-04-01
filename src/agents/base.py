"""
Base Agent

This module provides a base agent class that encapsulates common functionality
for all agents in the system.
"""

import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable

from dotenv import load_dotenv
from uagents import Agent, Context, Model

# Use relative imports
from ..utils.logging import configure_logging, log_exception
from ..utils.errors import CommunicationError, ConfigurationError


class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    
    This class encapsulates common functionality such as initialization,
    logging, error handling, and environment variable loading.
    """
    
    def __init__(
        self,
        name: str,
        port: int,
        seed: str,
        endpoint: Optional[str] = None,
        log_level: int = logging.INFO
    ):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
            port: The port to run the agent on
            seed: The seed phrase for agent identity
            endpoint: The endpoint URL (default: constructed from port)
            log_level: The logging level (default: INFO)
        """
        # Load environment variables
        load_dotenv()
        
        # Set up logging
        self.logger = configure_logging(
            logger_name=f"agent.{name.lower().replace(' ', '_')}",
            log_level=log_level
        )
        
        # Set agent properties
        self.name = name
        self.port = port
        self.seed = seed
        
        # Set endpoint if provided, otherwise construct it
        if endpoint is None:
            self.endpoint = [f"http://127.0.0.1:{port}/submit"]
        else:
            self.endpoint = [endpoint]
        
        # Initialize the agent
        try:
            self.agent = Agent(
                name=self.name,
                port=self.port,
                seed=self.seed,
                endpoint=self.endpoint,
            )
            
            # Register default event handlers
            self.agent.on_event("startup")(self.on_startup)
            self.agent.on_event("shutdown")(self.on_shutdown)
            
            # Register custom event handlers
            self.register_handlers()
            
            self.logger.info(f"Agent {self.name} initialized successfully")
        
        except Exception as e:
            self.logger.critical(f"Failed to initialize agent: {e}")
            raise ConfigurationError(f"Failed to initialize {self.name} agent: {e}")
    
    async def on_startup(self, ctx: Context) -> None:
        """
        Handler for agent startup event.
        
        Args:
            ctx: Agent context
        """
        self.logger.info(f"Agent started: {ctx.agent.address}")
        print(f"Hello! I'm {self.name} and my address is {ctx.agent.address}.")
    
    async def on_shutdown(self, ctx: Context) -> None:
        """
        Handler for agent shutdown event.
        
        Args:
            ctx: Agent context
        """
        self.logger.info(f"Agent shutting down: {ctx.agent.address}")
    
    @abstractmethod
    def register_handlers(self) -> None:
        """
        Register message and event handlers.
        
        This method should be implemented by subclasses to register
        their specific message and event handlers.
        """
        pass
    
    def register_message_handler(self, model_class: Any, handler: Callable) -> None:
        """
        Register a message handler for a specific model.
        
        Args:
            model_class: The model class to handle
            handler: The handler function
        """
        self.agent.on_message(model=model_class)(handler)
        self.logger.debug(f"Registered message handler for {model_class.__name__}")
    
    async def send_message(self, ctx: Context, recipient: str, message: Model) -> None:
        """
        Send a message to another agent with error handling.
        
        Args:
            ctx: Agent context
            recipient: Recipient agent address
            message: The message to send
            
        Raises:
            CommunicationError: If sending the message fails
        """
        try:
            await ctx.send(recipient, message)
            self.logger.debug(f"Sent {message.__class__.__name__} to {recipient}")
        except Exception as e:
            error_msg = f"Failed to send {message.__class__.__name__} to {recipient}"
            log_exception(self.logger, e, error_msg)
            raise CommunicationError(error_msg, {"recipient": recipient})
    
    def run(self) -> None:
        """
        Run the agent.
        
        This method starts the agent and handles any exceptions that occur.
        """
        try:
            self.logger.info(f"Starting agent: {self.name}")
            self.agent.run()
        except KeyboardInterrupt:
            self.logger.info(f"Agent {self.name} stopped by user")
        except Exception as e:
            self.logger.critical(f"Error running agent: {e}")
            sys.exit(1) 