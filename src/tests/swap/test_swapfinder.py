#!/usr/bin/env python3
"""
Test for Swapfinder Agent

This module provides a test client for the Swapfinder agent functionality.
It sets up a Flask server to receive and handle swap requests and responses.
The Swapfinder agent uses AI reasoning to determine the best swap agent for a transaction.
"""

import logging
import os
import sys
from threading import Thread

from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
from uagents import Model
from dotenv import load_dotenv

# Import models from project
from ...models.requests import SwapRequest
from ...models.responses import SwapResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
flask_app = Flask(__name__)
CORS(flask_app)

# Client identity for Agentverse
client_identity = None

# Store for agent response
agent_response = None

# Load environment variables
load_dotenv()


def init_client():
    """Initialize and register the client agent with Agentverse."""
    global client_identity
    try:
        # Create identity from seed
        client_identity = Identity.from_seed("swapfinder_test_seed_phrase", 0)
        logger.info(f"Test client started with address: {client_identity.address}")
        
        # Create README for agent registration
        readme = """
![tag:swapland](https://img.shields.io/badge/swapfinder-1)

<description>Test client for the Swapfinder agent that finds the best swap option.</description>
<use_cases>
    <use_case>Tests the swapfinder agent that determines the best swap path.</use_case>
</use_cases>
<payload_requirements>
<description>Expects a swap request containing blockchain, signal, and amount.</description>
    <payload>
          <requirement>
              <parameter>blockchain</parameter>
              <description>The blockchain to use for the swap (e.g., "base").</description>
          </requirement>
          <requirement>
              <parameter>signal</parameter>
              <description>The signal to determine swap direction (e.g., "buy" or "sell").</description>
          </requirement>
          <requirement>
              <parameter>amount</parameter>
              <description>Amount to swap.</description>
          </requirement>
    </payload>
</payload_requirements>
"""
        
        # Register with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5004/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Test Client for Swapfinder Agent",
            readme=readme
        )
        
        logger.info("Test client registration complete")
        
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise


@flask_app.route('/send_request', methods=['POST'])
def send_request():
    """
    Send a test swap request to the Swapfinder agent.
    
    Expected JSON payload:
    {
        "blockchain": "base",
        "signal": "buy" or "sell",
        "amount": 100.0
    }
    """
    global agent_response
    agent_response = None
    
    try:
        # Get request data
        data = request.json
        
        # Create swap request
        swap_request = SwapRequest(
            blockchain=data.get("blockchain", "base"),
            signal=data.get("signal", "buy"),
            amount=float(data.get("amount", 100))
        )
        
        # Target agent address - the Swapfinder agent
        target_agent = "agent1q2kxet8hcvyzk34xvd7n8ue24p9hdygqlz98p32p0s6dqths0yazwpqe9fg"
        
        # Create model digest
        model_digest = Model.build_schema_digest(SwapRequest)
        
        # Send message to agent
        send_message_to_agent(
            client_identity,
            target_agent,
            swap_request.dict(),
            model_digest=model_digest
        )
        
        logger.info(f"Sent swap request to {target_agent}: {swap_request}")
        
        return jsonify({
            "status": "request_sent",
            "request": swap_request.dict()
        })
        
    except Exception as e:
        logger.error(f"Error sending swap request: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@flask_app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook messages from the Swapfinder agent."""
    global agent_response
    
    try:
        # Parse incoming message
        data = request.get_data().decode("utf-8")
        logger.info("Received response from Swapfinder agent")
        
        # Parse agent message
        message = parse_message_from_agent(data)
        agent_response = message.payload
        
        logger.info(f"Processed response: {agent_response}")
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500


@flask_app.route('/last_response', methods=['GET'])
def get_last_response():
    """Get the last response received from the Swapfinder agent."""
    global agent_response
    
    return jsonify({
        "response": agent_response
    })


def run_test_server():
    """Run the test server."""
    # Initialize client
    init_client()
    
    # Start Flask server in a separate thread
    Thread(
        target=lambda: flask_app.run(
            host="0.0.0.0",
            port=5004,
            debug=False,
            use_reloader=False
        )
    ).start()
    
    logger.info("Test server running on http://localhost:5004")
    logger.info("Send POST requests to /send_request to test the Swapfinder agent")
    logger.info("GET /last_response to get the last response received from the agent")


if __name__ == "__main__":
    try:
        run_test_server()
        
        # Keep the main thread running
        while True:
            cmd = input("> ")
            if cmd.lower() == "exit":
                break
            elif cmd.lower() == "send":
                signal = input("Enter signal (buy/sell): ").lower()
                amount = input("Enter amount: ")
                try:
                    # Make a manual request
                    import requests
                    response = requests.post(
                        "http://localhost:5004/send_request",
                        json={
                            "blockchain": "base",
                            "signal": signal,
                            "amount": float(amount)
                        }
                    )
                    print(f"Response: {response.json()}")
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd.lower() == "response":
                try:
                    import requests
                    response = requests.get("http://localhost:5004/last_response")
                    print(f"Last response: {response.json()}")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Unknown command. Available commands: exit, send, response")
                
    except KeyboardInterrupt:
        logger.info("Test server stopped by user")
    except Exception as e:
        logger.error(f"Error running test server: {e}")
        sys.exit(1) 