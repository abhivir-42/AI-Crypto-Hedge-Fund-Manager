#!/usr/bin/env python3

import requests
import json
import logging
import sys
import uuid
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_news_agent():
    """Test the crypto news agent by sending a direct HTTP request"""
    
    # Endpoint of the news agent
    url = "http://localhost:9016/submit"
    
    # Address of the running news agent
    news_agent_address = "agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9"
    
    # Generate a random sender address for testing
    sender = f"agent1q{uuid.uuid4().hex[:40]}"
    
    # Create the message payload - following the uAgents envelope format
    envelope = {
        "type": "CryptonewsRequest",
        "version": "0.1.0",
        "sender": sender,
        "target": news_agent_address,
        "message": {
            "limit": 3
        }
    }
    
    logger.info(f"Testing Crypto News Agent at {news_agent_address}")
    logger.info(f"Sending request to {url}")
    
    try:
        # Send the request
        response = requests.post(url, json=envelope)
        
        # Check response
        if response.status_code == 202:
            logger.info(f"✅ Request accepted (status: {response.status_code})")
            logger.info(f"Response: {response.text}")
            return True
        else:
            logger.error(f"❌ Request failed with status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {str(e)}")
        return False

def test_coin_info_agent():
    """Test the coin info agent by sending a direct HTTP request"""
    
    # Endpoint of the coin info agent
    url = "http://localhost:9009/submit"
    
    # Address of the running coin info agent
    coin_info_address = "agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq"
    
    # Generate a random sender address
    sender = f"agent1q{uuid.uuid4().hex[:40]}"
    
    # Create the message payload
    envelope = {
        "type": "CoinRequest",
        "version": "0.1.0",
        "sender": sender,
        "target": coin_info_address,
        "message": {
            "blockchain": "ethereum"
        }
    }
    
    logger.info(f"Testing Coin Info Agent at {coin_info_address}")
    logger.info(f"Sending request to {url}")
    
    try:
        # Send the request
        response = requests.post(url, json=envelope)
        
        # Check response
        if response.status_code == 202:
            logger.info(f"✅ Request accepted (status: {response.status_code})")
            logger.info(f"Response: {response.text}")
            return True
        else:
            logger.error(f"❌ Request failed with status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {str(e)}")
        return False

def test_fgi_agent():
    """Test the fear & greed index agent by sending a direct HTTP request"""
    
    # Endpoint of the FGI agent
    url = "http://localhost:9010/submit"
    
    # Address of the running FGI agent
    fgi_address = "agent1q248t3vk8f60y3dqsr2nzu93h7tpz26dy62l4ejdtl9ces2sml8ask8zmdp"
    
    # Generate a random sender address
    sender = f"agent1q{uuid.uuid4().hex[:40]}"
    
    # Create the message payload
    envelope = {
        "type": "FGIRequest",
        "version": "0.1.0",
        "sender": sender,
        "target": fgi_address,
        "message": {
            "limit": 1
        }
    }
    
    logger.info(f"Testing Fear & Greed Index Agent at {fgi_address}")
    logger.info(f"Sending request to {url}")
    
    try:
        # Send the request
        response = requests.post(url, json=envelope)
        
        # Check response
        if response.status_code == 202:
            logger.info(f"✅ Request accepted (status: {response.status_code})")
            logger.info(f"Response: {response.text}")
            return True
        else:
            logger.error(f"❌ Request failed with status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting agent tests...")
    
    # Test each agent
    news_result = test_news_agent()
    time.sleep(1)  # Add a small delay between requests
    
    coin_result = test_coin_info_agent()
    time.sleep(1)  # Add a small delay between requests
    
    fgi_result = test_fgi_agent()
    
    # Report results
    logger.info("\n--- TEST RESULTS ---")
    logger.info(f"News Agent: {'✅ PASSED' if news_result else '❌ FAILED'}")
    logger.info(f"Coin Info Agent: {'✅ PASSED' if coin_result else '❌ FAILED'}")
    logger.info(f"Fear & Greed Index Agent: {'✅ PASSED' if fgi_result else '❌ FAILED'}")
    
    # Final result
    if news_result and coin_result and fgi_result:
        logger.info("✅ All tests PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ Some tests FAILED!")
        sys.exit(1) 