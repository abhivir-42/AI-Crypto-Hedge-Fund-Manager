"""
Centralized Settings

This module provides centralized access to configuration settings from
environment variables, with appropriate type conversions and default values.
"""

import os
from typing import Dict, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
ASI1_API_KEY: str = os.getenv("ASI1_API_KEY", "")
COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
AGENTVERSE_API_KEY: str = os.getenv("AGENTVERSE_API_KEY", "")

# Blockchain Configuration
METAMASK_PRIVATE_KEY: str = os.getenv("METAMASK_PRIVATE_KEY", "")
BASE_RPC_URL: str = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")

# Agent Seeds
MAIN_AGENT_SEED: str = os.getenv("MAIN_AGENT_SEED", "this_is_main_agent_to_run")
ASI1_AGENT_SEED: str = os.getenv("ASI1_AGENT_SEED", "asi1_reasoning_agent_seed_phrase")
ETH_USDC_AGENT_SEED: str = os.getenv("ETH_USDC_AGENT_SEED", "eth_usdc_agent_seed_phrase")
USDC_ETH_AGENT_SEED: str = os.getenv("USDC_ETH_AGENT_SEED", "usdc_eth_agent_seed_phrase")

# Agent Names
MAIN_AGENT_NAME: str = os.getenv("MAIN_AGENT_NAME", "SentimentBased CryptoSellAlerts")

# Agent Addresses
COIN_AGENT_ADDRESS: str = os.getenv(
    "COIN_AGENT_ADDRESS", 
    "agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq"
)
FGI_AGENT_ADDRESS: str = os.getenv(
    "FGI_AGENT_ADDRESS", 
    "agent1qgzh245lxeaapd32mxlwgdf2607fkt075hymp06rceknjnc2ylznwdv8up7"
)
REASON_AGENT_ADDRESS: str = os.getenv(
    "REASON_AGENT_ADDRESS", 
    "agent1qwlg48h8sstknk7enc2q44227ahq6dr5mjg0p7z62ca6tfueze38kyrtyl2"
)
CRYPTONEWS_AGENT_ADDRESS: str = os.getenv(
    "CRYPTONEWS_AGENT_ADDRESS", 
    "agent1q2cq0q3cnhccudx6cym8smvpquafsd99lrwexppuecfrnv90xlrs5lsxw6k"
)

# Port Configuration
MAIN_AGENT_PORT: int = int(os.getenv("MAIN_AGENT_PORT", "8017"))
ASI1_AGENT_PORT: int = int(os.getenv("ASI1_AGENT_PORT", "8018"))
ETH_USDC_AGENT_PORT: int = int(os.getenv("ETH_USDC_AGENT_PORT", "5002"))
USDC_ETH_AGENT_PORT: int = int(os.getenv("USDC_ETH_AGENT_PORT", "5004"))

# API Endpoints
ASI1_API_URL: str = "https://api.asi1.ai/v1/chat/completions"

# Contract Addresses
USDC_ADDRESS: str = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # Base network
WETH_ADDRESS: str = "0x4200000000000000000000000000000000000006"  # Base network
UNIVERSAL_ROUTER_ADDRESS: str = "0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD"  # Base network

# Blockchain Chain IDs
BASE_CHAIN_ID: int = 8453

# Default Agent Configuration
DEFAULT_AGENT_CONFIG: Dict[str, str] = {
    "main": {
        "name": MAIN_AGENT_NAME,
        "port": str(MAIN_AGENT_PORT),
        "seed": MAIN_AGENT_SEED,
        "endpoint": f"http://127.0.0.1:{MAIN_AGENT_PORT}/submit",
    },
    "asi1": {
        "name": "ASI1 Reasoning agent for crypto trading signals",
        "port": str(ASI1_AGENT_PORT),
        "seed": ASI1_AGENT_SEED,
        "endpoint": f"http://127.0.0.1:{ASI1_AGENT_PORT}/submit",
    },
    "eth_usdc": {
        "name": "Swapland ETH to USDC base agent",
        "port": str(ETH_USDC_AGENT_PORT),
        "seed": ETH_USDC_AGENT_SEED,
        "endpoint": f"http://127.0.0.1:{ETH_USDC_AGENT_PORT}/api/webhook",
    },
    "usdc_eth": {
        "name": "Swapland USDC to ETH base agent",
        "port": str(USDC_ETH_AGENT_PORT),
        "seed": USDC_ETH_AGENT_SEED,
        "endpoint": f"http://127.0.0.1:{USDC_ETH_AGENT_PORT}/api/webhook",
    },
}

# Check if required API keys are available
def validate_api_keys() -> None:
    """Validate that required API keys are set."""
    missing_keys = []
    
    if not ASI1_API_KEY:
        missing_keys.append("ASI1_API_KEY")
    
    if not AGENTVERSE_API_KEY:
        missing_keys.append("AGENTVERSE_API_KEY")
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")


# Other constants
DEFAULT_TIMEOUT: float = 30.0
MAX_RETRIES: int = 3 