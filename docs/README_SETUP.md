# Setting Up the Crypto Project

This document provides instructions for setting up and running the Crypto Project agents.

## Installation

To install the package in development mode:

```bash
# Navigate to the project directory
cd migrate

# Install in development mode
pip install -e .
```

This will install the package with all its dependencies and make the console scripts available.

## Configuration

Create a `.env` file in the project root with the required API keys and configuration:

```
# API Keys
ASI1_API_KEY=your_asi1_api_key
COINGECKO_API_KEY=your_coingecko_api_key
AGENTVERSE_API_KEY=your_agentverse_api_key
NEWS_API_KEY=your_news_api_key

# Blockchain Configuration
METAMASK_PRIVATE_KEY=your_metamask_private_key
BASE_RPC_URL=https://mainnet.base.org

# Agent Seeds - for development you can use these defaults
MAIN_AGENT_SEED=this_is_main_agent_to_run
ASI1_AGENT_SEED=asi1_reasoning_agent_seed_phrase
COIN_INFO_AGENT_SEED=coin_info_agent1_secret_phrase
FGI_AGENT_SEED=fear_greed_index_agent_seed
CRYPTO_NEWS_AGENT_SEED=crypto_news_agent_seed
REWARD_AGENT_SEED=reward_secret_phrase_agent_oekwpfokw
TOPUP_AGENT_SEED=topup_secret_phrase_agent_oekwpfokw
```

You can copy and modify the `.env.example` file provided in the `files` directory.

## Running Agents

You can run the agents using the provided console scripts:

```bash
# Run the Coin Info Agent
crypto-coin-info

# Run the Fear & Greed Index Agent
crypto-fgi

# Run the Crypto News Agent
crypto-news

# Run the Reward Agent
crypto-reward

# Run the Topup Agent
crypto-topup
```

Or you can run the agents directly with Python:

```bash
python -m crypto_project.agents.coin_info
```

## Running Tests

To run the tests:

```bash
# Install pytest if you haven't already
pip install pytest pytest-asyncio

# Run the tests
pytest
``` 