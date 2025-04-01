# Running the Crypto Trading Agent System

This guide provides step-by-step instructions for setting up and running the crypto trading agent system. Follow these instructions to get the system up and running quickly.

## Prerequisites

Before starting, make sure you have:

1. **Python 3.9+** installed
2. **Poetry** package manager installed
3. Required API keys:
   - ASI1 API key
   - CoinGecko API key
   - Agentverse API key
4. Ethereum wallet with:
   - Private key for transactions
   - ETH for gas fees
   - USDC tokens (if using swap functionality)

## Setup Instructions

### 1. Install Dependencies

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd crypto-project

# Install dependencies using Poetry
poetry install
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```
# API Keys
ASI1_API_KEY=your_asi1_api_key
COINGECKO_API_KEY=your_coingecko_api_key
AGENTVERSE_API_KEY=your_agentverse_api_key

# Blockchain Configuration
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_infura_key
METAMASK_PRIVATE_KEY=your_wallet_private_key

# Agent Seeds (change these for security in production)
MAIN_AGENT_SEED=main_agent_secret_phrase
ASI1_AGENT_SEED=asi1_agent_secret_phrase
COIN_INFO_AGENT_SEED=coin_info_agent_secret_phrase
CRYPTO_NEWS_AGENT_SEED=crypto_news_agent_secret_phrase
FGI_AGENT_SEED=fgi_agent_secret_phrase
REWARD_AGENT_SEED=reward_agent_secret_phrase
TOPUP_AGENT_SEED=topup_agent_secret_phrase
ETH_USDC_AGENT_SEED=eth_usdc_agent_secret_phrase
USDC_ETH_AGENT_SEED=usdc_eth_agent_secret_phrase
SWAPFINDER_AGENT_SEED=swapfinder_agent_secret_phrase

# Configuration
LOG_LEVEL=INFO
```

## Running the System

You can run the entire agent system or individual agents depending on your needs.

### Option 1: Run All Agents

The easiest way to run all agents is using the provided script:

```bash
# Make sure the script is executable
chmod +x scripts/run_agents.sh

# Run all agents
./scripts/run_agents.sh
```

This script will start all agents in separate terminal windows (requires a terminal that supports tabs or splitting).

### Option 2: Run Individual Agents

If you prefer to run agents individually, use the following commands in separate terminal windows:

```bash
# Main Agent (orchestrator)
poetry run python -m src.crypto_project.agents.main_agent

# ASI1 Reasoning Agent
poetry run python -m src.crypto_project.agents.asi1_agent

# Coin Info Agent
poetry run python -m src.crypto_project.agents.coin_info

# Crypto News Agent
poetry run python -m src.crypto_project.agents.crypto_news

# Fear & Greed Index Agent
poetry run python -m src.crypto_project.agents.fear_greed_index

# Reward Agent
poetry run python -m src.crypto_project.agents.reward

# Top-up Agent
poetry run python -m src.crypto_project.agents.topup

# Swap Agents (only if needed)
poetry run python -m src.crypto_project.agents.swap.eth_usdc
poetry run python -m src.crypto_project.agents.swap.usdc_eth
poetry run python -m src.crypto_project.agents.swap.swapfinder
```

### Option 3: Run with Console Scripts

If you've installed the package, you can use console scripts defined in `pyproject.toml`:

```bash
# Main Agent
crypto-main

# ASI1 Agent
crypto-asi1

# Coin Info Agent
crypto-coin-info

# Other agents follow the same pattern
crypto-news
crypto-fgi
crypto-reward
crypto-topup
crypto-eth-usdc
crypto-usdc-eth
crypto-swapfinder
```

## Verifying the System is Running

To verify that agents are running correctly:

1. Check the terminal output for each agent. You should see:
   - `Agent started: 0x...` message with an address
   - No error messages

2. In the main agent logs, look for:
   - Messages about connecting to other agents
   - Successful data retrieval from each agent
   - Trading signal generation

## Agent Communication Flow

When running properly, agents follow this communication flow:

1. Main agent initiates a request to the Coin Info agent
2. After receiving coin data, main agent requests news from the Crypto News agent
3. After receiving news, main agent requests FGI data
4. With all data collected, main agent sends analysis request to ASI1 agent
5. Based on ASI1's response, main agent may initiate swap operations

## Monitoring and Logs

All agents write logs to their respective log files in the `logs/` directory:

```
logs/
├── main_agent.log
├── asi1_agent.log
├── coin_info_agent.log
├── crypto_news_agent.log
├── fgi_agent.log
├── reward_agent.log
├── topup_agent.log
└── swap/
    ├── eth_usdc_agent.log
    ├── usdc_eth_agent.log
    └── swapfinder_agent.log
```

Monitor these logs for detailed information about agent operations.

## Common Issues and Solutions

### Agents Can't Find Each Other

If agents can't communicate:

1. Verify all agents are running
2. Ensure ports aren't blocked by firewall
3. Check that agent addresses match in the logs

### API Rate Limiting

If you encounter API rate limiting:

1. Reduce polling frequency in settings
2. Consider upgrading to paid API tiers
3. Implement caching for API responses

### Swap Transaction Failures

If swap transactions fail:

1. Verify wallet has sufficient ETH for gas
2. Check token allowances are set
3. Verify RPC URL is working
4. Check gas price settings

## Advanced Configuration

For advanced users, you can modify agent behavior in `src/crypto_project/config/settings.py`.

Key settings include:

- `POLLING_INTERVAL`: Time between data checks
- `MAX_RETRIES`: Number of retry attempts for API calls
- `GAS_PRICE_STRATEGY`: Strategy for gas price determination
- `TRADING_THRESHOLDS`: Thresholds for trading decisions

## Conclusion

You should now have the crypto trading agent system up and running. The system will continuously monitor cryptocurrency market data and generate trading signals based on AI analysis. For more details on each agent's functionality, refer to the project documentation. 