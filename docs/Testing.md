# Testing Guide for Crypto Trading Agent System

This document provides comprehensive information on how to test the crypto trading agent system after migration. Follow these guidelines to ensure all components work correctly in the new structure.

## Test Environment Setup

Before running tests, you need to set up the test environment:

1. **Create a Test Environment File**

   Create a `.env.test` file in the root of your project with the following content:

   ```
   # API Keys (use test keys if available)
   ASI1_API_KEY=your_asi1_test_api_key
   COINGECKO_API_KEY=your_coingecko_test_api_key
   AGENTVERSE_API_KEY=your_agentverse_test_api_key
   
   # Blockchain Configuration (use testnet settings)
   ETHEREUM_RPC_URL=https://goerli.infura.io/v3/your_infura_key
   METAMASK_PRIVATE_KEY=your_test_wallet_private_key
   
   # Agent Seeds (for test environment)
   MAIN_AGENT_SEED=main_agent_test_seed_phrase
   ASI1_AGENT_SEED=asi1_agent_test_seed_phrase
   COIN_INFO_AGENT_SEED=coin_info_test_seed_phrase
   CRYPTO_NEWS_AGENT_SEED=crypto_news_test_seed_phrase
   FGI_AGENT_SEED=fgi_test_seed_phrase
   REWARD_AGENT_SEED=reward_test_seed_phrase
   TOPUP_AGENT_SEED=topup_test_seed_phrase
   ETH_USDC_AGENT_SEED=eth_usdc_test_seed_phrase
   USDC_ETH_AGENT_SEED=usdc_eth_test_seed_phrase
   SWAPFINDER_AGENT_SEED=swapfinder_test_seed_phrase
   
   # Test Configuration
   LOG_LEVEL=DEBUG
   TEST_MODE=true
   ```

2. **Install Test Dependencies**

   ```bash
   poetry install --with dev
   ```

3. **Configure Test Networks**

   For blockchain-related tests (swap agents), ensure you have:
   - Goerli (Ethereum testnet) ETH in your test wallet
   - Test USDC on Goerli
   - Properly configured RPC endpoints

## Test Categories

### 1. Unit Tests

Unit tests verify individual components in isolation:

#### Agent Tests

```bash
# Run all agent tests
poetry run pytest tests/unit/test_agents/

# Run specific agent tests
poetry run pytest tests/unit/test_agents/test_coin_info.py
poetry run pytest tests/unit/test_agents/test_fear_greed_index.py
poetry run pytest tests/unit/test_agents/test_crypto_news.py
poetry run pytest tests/unit/test_agents/test_reward.py
poetry run pytest tests/unit/test_agents/test_topup.py
poetry run pytest tests/unit/test_agents/test_asi1.py
```

#### Service Tests

```bash
# Run all service tests
poetry run pytest tests/unit/test_services/

# Run specific service tests
poetry run pytest tests/unit/test_services/test_llm_service.py
poetry run pytest tests/unit/test_services/test_swap_service/
```

#### Model Tests

```bash
# Run model tests
poetry run pytest tests/unit/test_models/
```

### 2. Integration Tests

Integration tests verify that components work together:

```bash
# Run all integration tests
poetry run pytest tests/integration/

# Run specific integration workflow
poetry run pytest tests/integration/test_trading_workflow.py
poetry run pytest tests/integration/test_swap_workflow.py
```

### 3. Mock Tests

For tests requiring external services (ASI1, CoinGecko, blockchain), mock versions are available:

```bash
# Run with mocks
TEST_USE_MOCKS=true poetry run pytest
```

### 4. End-to-End Tests

These tests run the entire system:

```bash
# Start all agents in test mode
./scripts/run_agents_test.sh

# In another terminal, run the end-to-end tests
poetry run pytest tests/e2e/
```

## What to Test

1. **Agent Communication**
   - Each agent should successfully register with the framework
   - Messages should be properly sent and received between agents

2. **Data Retrieval**
   - Coin Info Agent should fetch cryptocurrency data
   - Fear & Greed Index Agent should retrieve market sentiment
   - Crypto News Agent should gather relevant news

3. **LLM Integration**
   - ASI1 Agent should process data and generate trading signals
   - Error handling should work for API failures

4. **Swap Functionality**
   - ETH to USDC conversions should work on test networks
   - USDC to ETH conversions should work on test networks
   - SwapFinder should correctly identify the best swap option

5. **End-to-End Workflow**
   - The full trading signal generation workflow should run without errors
   - System should handle different market conditions

## Expected Test Results

When all tests pass, you should see:

1. All unit tests pass with proper mocking
2. Integration tests demonstrate correct inter-agent communication
3. End-to-end tests show the complete workflow functioning

## Troubleshooting Test Failures

### Common Issues and Solutions

#### 1. Agent Communication Failures

**Symptoms**:
- Timeouts when agents try to communicate
- Missing message handlers

**Solutions**:
- Verify agent addresses are correctly configured
- Check port availability (no conflicts)
- Ensure message handlers are registered in the `register_handlers` method

#### 2. API Integration Failures

**Symptoms**:
- Failed requests to external APIs
- Timeout errors

**Solutions**:
- Check API key validity
- Verify network connectivity
- Look for rate limiting issues
- Use mock services for testing (set `TEST_USE_MOCKS=true`)

#### 3. Blockchain Interaction Failures

**Symptoms**:
- Failed transactions
- Gas estimation errors

**Solutions**:
- Ensure sufficient test ETH in wallet
- Verify RPC endpoint availability
- Check transaction parameters
- Use lower gas limits for testnet

#### 4. Data Model Issues

**Symptoms**:
- Type errors
- Missing fields in responses

**Solutions**:
- Check model definitions match expected API responses
- Verify field types are correct
- Add validation to handle missing or null fields

## Manual Testing Steps

For manual verification of the system:

1. **Start all agents**:
   ```bash
   ./scripts/run_agents.sh
   ```

2. **Verify agent startup**:
   - Check logs for successful initialization
   - Verify agents are registered with correct addresses

3. **Test market data retrieval**:
   - Send a test request to the Coin Info Agent
   - Verify the response contains expected fields

4. **Test news retrieval**:
   - Send a test request to the Crypto News Agent
   - Verify news data is properly formatted

5. **Test trading signal generation**:
   - Monitor the main agent logs
   - Verify it collects data from all agents
   - Check that ASI1 produces valid trading signals

6. **Test swap functionality** (if applicable):
   - Initiate a small test swap through the appropriate agent
   - Verify transaction success on the testnet explorer

## Continuous Testing

For ongoing development, integrate these tests into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: curl -sSL https://install.python-poetry.org | python3 -
      - name: Install dependencies
        run: poetry install --with dev
      - name: Run tests with mocks
        run: TEST_USE_MOCKS=true poetry run pytest
        env:
          # Add required test environment variables here
          TEST_MODE: true
```

## Conclusion

Following this testing guide will ensure that all components of the migrated crypto trading agent system work correctly. Start with unit tests to verify individual components, then progress to integration and end-to-end tests to validate the entire system. Use the troubleshooting guidance if you encounter issues during testing. 