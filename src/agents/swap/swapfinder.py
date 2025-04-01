#!/usr/bin/env python3
"""
Swapfinder Agent

This module implements an agent that helps locate the best swap agent for a given
cryptocurrency transaction. It uses AI reasoning to find the most appropriate
swap agent based on the user's requirements.
"""

import logging
import os
import sys
import requests
from typing import Dict, Any, List, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from uagents import Context, Model

from ..base import BaseAgent
from ...models.requests import SwapRequest
from ...models.responses import SwapResponse
from ...services.asi1 import query_llm
from ...utils.errors import APIError, CommunicationError
from ...utils.logging import log_exception
from ...config.settings import AGENTVERSE_API_KEY


class SwapfinderAgent(BaseAgent):
    """
    Agent that helps find the best swap agent for a cryptocurrency transaction.
    
    This agent receives swap requests, uses AI reasoning to find the most appropriate
    swap agent, and forwards the request to that agent.
    """
    
    def __init__(self):
        """Initialize the Swapfinder agent."""
        super().__init__(
            name="SwapfinderAgent",
            port=5003,
            seed=os.getenv("SWAPFINDER_AGENT_SEED", "jedijidemphraifjowienowkewmm")
        )
        
        # Initialize Flask app for webhooks
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Set up routes
        self.app.route('/api/webhook', methods=['POST'])(self.webhook_handler)
        self.app.route('/request', methods=['POST'])(self.send_data_handler)
        
        # Store for agent response (used for communication between routes)
        self.agent_response = None
        
        # Register with Agentverse
        self.client_identity = Identity.from_seed(os.getenv(
            "SWAPFINDER_AGENT_SEED", "jedijidemphraifjowienowkewmm"
        ), 0)
        self.register_with_agentverse()
    
    def register_handlers(self) -> None:
        """Register message and event handlers."""
        self.register_message_handler(SwapRequest, self.handle_swap_request)
        self.register_message_handler(SwapResponse, self.handle_swap_response)
    
    def register_with_agentverse(self) -> None:
        """Register the agent with Agentverse."""
        try:
            from fetchai.registration import register_with_agentverse
            
            # Create a README for the agent
            readme = """
![tag:swapland](https://img.shields.io/badge/swapland-master)

<description>This Agent can find the best swap agent for your cryptocurrency transaction.</description>
<use_cases>
    <use_case>To find the right swap agent for your crypto swaps.</use_case>
</use_cases>
<payload_requirements>
<description>This agent requires blockchain, signal, and amount information.</description>
<payload>
    <requirement>
        <parameter>blockchain</parameter>
        <description>The blockchain to use (e.g., "base")</description>
    </requirement>
    <requirement>
        <parameter>signal</parameter>
        <description>The swap direction (buy or sell)</description>
    </requirement>
    <requirement>
        <parameter>amount</parameter>
        <description>The amount to swap</description>
    </requirement>
</payload>
</payload_requirements>
"""
            
            # Register the agent
            register_with_agentverse(
                identity=self.client_identity,
                url=f"http://127.0.0.1:{self.port}/api/webhook",
                agentverse_token=AGENTVERSE_API_KEY,
                agent_title="Swapland finder agent",
                readme=readme
            )
            
            self.logger.info("Agent registered with Agentverse successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to register with Agentverse: {e}")
    
    async def handle_swap_request(self, ctx: Context, sender: str, msg: SwapRequest) -> None:
        """
        Handle a swap request by finding the appropriate swap agent.
        
        Args:
            ctx: Agent context
            sender: Sender agent address
            msg: Swap request with blockchain, signal, and amount
        """
        self.logger.info(f"Received swap request from {sender}: {msg.blockchain}/{msg.signal} for {msg.amount}")
        
        try:
            # Search for appropriate swap agent
            agent_address = self.search_swap_agent(msg.blockchain, msg.signal, msg.amount)
            
            if not agent_address:
                await self.send_message(
                    ctx, 
                    sender, 
                    SwapResponse(
                        status="error",
                        message="No suitable swap agent found"
                    )
                )
                return
            
            # Forward the request to the chosen agent
            await self.send_message(ctx, agent_address, msg)
            self.logger.info(f"Forwarded swap request to agent: {agent_address}")
            
            # For now, we just inform the sender that the request was forwarded
            # In a real implementation, we would wait for the response from the swap agent
            await self.send_message(
                ctx, 
                sender, 
                SwapResponse(
                    status="pending",
                    message=f"Request forwarded to swap agent at {agent_address}"
                )
            )
            
        except Exception as e:
            log_exception(self.logger, e, "Error handling swap request")
            
            await self.send_message(
                ctx, 
                sender, 
                SwapResponse(
                    status="error",
                    message=f"Error finding swap agent: {str(e)}"
                )
            )
    
    async def handle_swap_response(self, ctx: Context, sender: str, msg: SwapResponse) -> None:
        """
        Handle a response from a swap agent.
        
        Args:
            ctx: Agent context
            sender: Sender agent address (the swap agent)
            msg: Swap response
        """
        self.logger.info(f"Received swap response from {sender}: {msg.status}")
        
        # In a real implementation, we would forward this response to the original requester
        # For now, we just log it
        self.agent_response = msg
    
    def search_swap_agent(self, blockchain: str, signal: str, amount: float) -> Optional[str]:
        """
        Search for an appropriate swap agent based on the request.
        
        Args:
            blockchain: The blockchain to use
            signal: The swap direction (buy or sell)
            amount: The amount to swap
            
        Returns:
            Optional[str]: The agent address if found, None otherwise
        """
        try:
            # Search for agents matching the criteria
            api_url = "https://agentverse.ai/v1/search/agents"
            query = f"{blockchain} {signal}"
            
            payload = {
                "search_text": "swapland",  # Base search text
                "sort": "relevancy",
                "direction": "asc",
                "offset": 0,
                "limit": 5,
            }
            
            # Make a POST request to the API
            response = requests.post(api_url, json=payload)
            
            if response.status_code != 200:
                self.logger.error(f"Agent search failed: {response.status_code}")
                return None
            
            data = response.json()
            agents = data.get("agents", [])
            
            if not agents:
                self.logger.info("No agents found")
                return None
            
            # Construct prompt for AI to analyze agents
            prompt = f"""
            These are all agents found through the search agent function using given information: "{query}" and {payload}. 
            Analyse all of the agents in the list and find the most suitable and output its agent address.
            Each agent has 3 parameters to consider: name, address and readme. Evaluate them all.
            
            Specific requirements:
            - Blockchain: {blockchain}
            - Signal (buy/sell): {signal}
            - Amount: {amount}
            
            Agents discovered:
            """
            
            for agent in agents:
                agent_info = f"""
                Agent Name: {agent.get("name")}
                Agent Address: {agent.get("address")}
                Readme: {agent.get("readme")}
                {"-" * 50}
                """
                prompt += agent_info
            
            # Query AI for decision
            self.logger.info("Requesting AI analysis of discovered agents")
            ai_response = query_llm(prompt)
            
            # Extract agent address from AI response
            # This is a simple implementation; could be enhanced with regex pattern matching
            for agent in agents:
                if agent.get("address") in ai_response:
                    self.logger.info(f"Selected agent: {agent.get('name')} ({agent.get('address')})")
                    return agent.get("address")
            
            # Fallback to hardcoded agents if AI doesn't give a clear answer
            if blockchain.lower() == "base":
                if signal.lower() == "sell":  # ETH to USDC
                    return "agent1qfrhxny23vz62v5tr20qnmnjujq8k5t0mxgwdxfap945922t9v4ugqtqkea"
                elif signal.lower() == "buy":  # USDC to ETH
                    return "agent1qgv9k947c5m04tmsqa9x2fnmuavjx9wz5pnclkr9cnafra7aym48g6qqajy"
            
            self.logger.info("No suitable agent found after AI analysis")
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching for swap agent: {e}")
            return None
    
    def webhook_handler(self):
        """Handle incoming webhook messages from Agentverse."""
        try:
            from fetchai.communication import parse_message_from_agent
            
            # Parse the incoming webhook message
            data = request.get_data().decode("utf-8")
            self.logger.info("Received webhook data")
            
            message = parse_message_from_agent(data)
            self.agent_response = message.payload
            
            self.logger.info(f"Processed webhook message: {self.agent_response}")
            
            return jsonify({"status": "success"})
            
        except Exception as e:
            self.logger.error(f"Error in webhook handler: {e}")
            return jsonify({"error": str(e)}), 500
    
    def send_data_handler(self):
        """Handle requests to send data to another agent."""
        try:
            from fetchai.communication import send_message_to_agent
            
            # Extract payload from request
            payload = {"status": "Successfully request sent to Swapland uAgent!"}
            
            # Target agent address
            uagent_address = "agent1qfrhxny23vz62v5tr20qnmnjujq8k5t0mxgwdxfap945922t9v4ugqtqkea"
            
            # Build model digest
            model_digest = Model.build_schema_digest(SwapResponse)
            
            # Send the message
            send_message_to_agent(
                self.client_identity,
                uagent_address,
                payload,
                model_digest=model_digest
            )
            
            return jsonify({"status": "request_sent", "payload": payload})
            
        except Exception as e:
            self.logger.error(f"Error sending data to agent: {e}")
            return jsonify({"error": str(e)}), 500
    
    def run(self) -> None:
        """Run the agent with Flask server."""
        try:
            self.logger.info(f"Starting agent: {self.name}")
            
            # Run the Flask app (this blocks)
            self.app.run(host="0.0.0.0", port=self.port)
            
        except KeyboardInterrupt:
            self.logger.info(f"Agent {self.name} stopped by user")
        except Exception as e:
            self.logger.critical(f"Error running agent: {e}")
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
                logging.FileHandler(filename="swapfinder_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        swapfinder_agent = SwapfinderAgent()
        swapfinder_agent.run()
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
                logging.FileHandler(filename="swapfinder_agent.log", mode="a"),
            ],
        )
        
        # Create and run the agent
        swapfinder_agent = SwapfinderAgent()
        swapfinder_agent.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 