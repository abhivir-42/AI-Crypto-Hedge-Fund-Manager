#!/usr/bin/env python3
"""
ASI1 API Service

This module provides functions to interact with the ASI1 LLM API for AI reasoning.
"""

import os
import logging
import requests
from typing import Dict, Any, Optional

from ..utils.errors import APIError
from ..utils.logging import log_exception
from ..config.settings import ASI1_API_KEY


def query_llm(prompt: str) -> str:
    """
    Queries the ASI1-Mini LLM with a given prompt and returns the model's response.
    
    Args:
        prompt: The input question or statement for the language model
        
    Returns:
        str: The response from the LLM
        
    Raises:
        APIError: If the request to the LLM API fails
    """
    api_key = ASI1_API_KEY
    if not api_key:
        raise APIError("ASI1_API_KEY is not set in environment variables")
    
    url = "https://api.asi1.ai/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "conversationId": None,
        "model": "asi1-mini"
    }
    
    logger = logging.getLogger("service.asi1")
    
    try:
        logger.debug(f"Sending request to ASI1 API: {prompt[:100]}...")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        output = response.json()
        content = output["choices"][0]["message"]["content"]
        
        logger.debug(f"Received response from ASI1 API: {content[:100]}...")
        return content
        
    except requests.exceptions.RequestException as e:
        log_exception(logger, e, "ASI1 API request failed")
        raise APIError(f"Failed to query ASI1 LLM: {e}")
    
    except (KeyError, IndexError) as e:
        log_exception(logger, e, "Invalid response format from ASI1 API")
        raise APIError(f"Invalid response from ASI1 LLM: {e}")


def analyze_crypto_sentiment(news_data: Dict[str, Any], price_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes cryptocurrency sentiment using the ASI1 LLM.
    
    Args:
        news_data: Recent cryptocurrency news
        price_data: Recent price and market data
        
    Returns:
        Dict[str, Any]: Sentiment analysis results
        
    Raises:
        APIError: If the request to the LLM API fails
    """
    prompt = f"""
    Please analyze the following cryptocurrency data and provide a sentiment analysis:
    
    NEWS DATA:
    {news_data}
    
    PRICE DATA:
    {price_data}
    
    Based on this information, please:
    1. Determine if the overall sentiment is bullish or bearish
    2. Explain key factors influencing the market
    3. Recommend whether to buy, sell, or hold
    4. Provide a confidence level (low, medium, high)
    
    Format your response as JSON with the following structure:
    {{
        "sentiment": "bullish|bearish|neutral",
        "key_factors": ["factor1", "factor2"],
        "recommendation": "buy|sell|hold",
        "confidence": "low|medium|high",
        "explanation": "brief explanation"
    }}
    """
    
    response = query_llm(prompt)
    
    # In a production system, you'd properly parse this as JSON
    # For simplicity, we're returning the raw response for now
    return {
        "analysis": response
    } 