# Step-by-Step Migration Guide

This document provides detailed steps to migrate the legacy cryptoreason project to the new structure using Poetry. Follow these steps in order to successfully set up your new environment and migrate all functionality.

## 1. Setup Poetry Environment

```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Initialize the poetry project
poetry init --name crypto-trading-agent --description "A multi-agent system for cryptocurrency trading signals and automated swaps"

# Copy the provided pyproject.toml configuration
cp migrate/files/pyproject.toml .

# Create the basic directory structure
mkdir -p src/crypto_project/{agents,config,models,services,integration,utils}
mkdir -p src/crypto_project/agents/swap
mkdir -p src/crypto_project/services/swap_service
mkdir -p docs/images
mkdir -p tests/{unit,integration}
mkdir -p tests/unit/{test_models,test_agents,test_services,test_integration}
mkdir -p scripts

# Create initial __init__.py files
touch src/crypto_project/__init__.py
touch src/crypto_project/{agents,config,models,services,integration,utils}/__init__.py
touch src/crypto_project/agents/swap/__init__.py
touch src/crypto_project/services/swap_service/__init__.py
touch tests/__init__.py
touch tests/{unit,integration}/__init__.py
touch tests/unit/{test_models,test_agents,test_services,test_integration}/__init__.py
```

## 2. Set Up Environment Variables

```bash
# Copy the example .env file
cp migrate/files/.env.example .env

# Edit the .env file to add your actual API keys and configuration
# You'll need to set:
# - ASI1_API_KEY
# - COINGECKO_API_KEY
# - AGENTVERSE_API_KEY
# - METAMASK_PRIVATE_KEY
# - Other agent seeds and configuration
```

## 3. Copy Original Agent Code to the New Structure

```bash
# Copy the improved agent implementations to the new structure

# Main agent
cp migrate/files/agents/main_agent.py src/crypto_project/agents/

# ASI1 LLM integration
cp migrate/files/agents/asi1_agent.py src/crypto_project/agents/
cp migrate/files/services/llm_service.py src/crypto_project/services/

# Specialized agents
cp migrate/files/agents/coin_info.py src/crypto_project/agents/
cp migrate/files/agents/crypto_news.py src/crypto_project/agents/
cp migrate/files/agents/fear_greed_index.py src/crypto_project/agents/
cp migrate/files/agents/dashboard.py src/crypto_project/agents/
cp migrate/files/agents/reward.py src/crypto_project/agents/
cp migrate/files/agents/topup.py src/crypto_project/agents/

# Swap agents
cp migrate/files/agents/swap/eth_to_usdc.py src/crypto_project/agents/swap/
cp migrate/files/agents/swap/usdc_to_eth.py src/crypto_project/agents/swap/
cp migrate/files/agents/swap/swapfinder.py src/crypto_project/agents/swap/

# Swap services
cp migrate/files/services/swap_service/eth_usdc.py src/crypto_project/services/swap_service/
cp migrate/files/services/swap_service/usdc_eth.py src/crypto_project/services/swap_service/

# Model definitions
cp migrate/files/models/requests.py src/crypto_project/models/
cp migrate/files/models/responses.py src/crypto_project/models/

# Configuration and utilities
cp migrate/files/config/settings.py src/crypto_project/config/
cp migrate/files/utils/logging.py src/crypto_project/utils/
cp migrate/files/utils/errors.py src/crypto_project/utils/

# Copy utility scripts
cp migrate/files/scripts/run_agents.sh scripts/
chmod +x scripts/run_agents.sh
```

## 4. Install Dependencies with Poetry

```bash
# Install all dependencies
poetry install

# [Optional] If you need additional packages not in pyproject.toml
poetry add package-name
```

## 5. Run Tests

```bash
# Run tests to verify functionality
poetry run pytest
```

## 6. Run the Application

```bash
# Run the main agent
poetry run python -m src.crypto_project.agents.main_agent

# Alternatively, use the provided script to run all agents
./scripts/run_agents.sh
```

## 7. Verify Functionality

Follow these steps to manually verify that all functionality is working correctly:

1. Run the main agent and check that it connects to other agents
2. Test the Fear & Greed Index data retrieval
3. Test cryptocurrency market data retrieval
4. Test news aggregation functionality
5. Verify that the ASI1 reasoning provides proper trading signals
6. Test the swap functionality if applicable to your use case

## Troubleshooting

### Common Issues and Solutions

**Issue: Agent cannot connect to Agentverse**
- Verify your AGENTVERSE_API_KEY is correct
- Check network connectivity
- Ensure agent addresses are correctly configured

**Issue: ASI1 API errors**
- Verify your ASI1_API_KEY is valid and active
- Check for rate limiting issues
- Ensure the ASI1 API endpoint is accessible

**Issue: Swap functionality not working**
- Verify your METAMASK_PRIVATE_KEY is correctly set
- Ensure you have sufficient funds for gas and transactions
- Check that RPC endpoints are accessible and responsive

**Issue: Dependencies conflicts**
- Run `poetry show --tree` to see dependency relationships
- Update conflicting dependencies in pyproject.toml
- Try removing poetry.lock and running `poetry install` again 