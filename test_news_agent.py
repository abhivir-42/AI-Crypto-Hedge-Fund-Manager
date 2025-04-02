#!/usr/bin/env python3

import os
import sys
import requests
import logging
import json
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_news_agent():
    """
    Test the crypto news agent by sending a direct HTTP request to its endpoint
    """
    # Endpoint of the news agent
    url = "http://localhost:9016/submit"
    
    # Address of the crypto news agent (from previous output)
    news_agent_address = "agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9"
    
    # Create the request payload
    payload = {
        "destination": news_agent_address,
        "message": {
            "limit": 3
        },
        "protocol": "CryptonewsRequest",
        "sender": "agent1qfq8f6s7je3mmxs3xqzyqc9gv4a3apqlkxzs93md7vvnnnsd32xzytxm07f"
    }
    
    logging.info(f"Sending request to {url}")
    
    try:
        # Send the request
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        # Log the response
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response headers: {response.headers}")
        logging.info(f"Response body: {response.text}")
        
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending request: {e}")
        return False

if __name__ == "__main__":
    logging.info("Starting test for Crypto News Agent")
    result = test_news_agent()
    
    if result:
        logging.info("Test completed successfully")
    else:
        logging.error("Test failed")
        sys.exit(1) 