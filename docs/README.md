# Crypto Trading Agent System

## Project Overview

The Crypto Trading Agent System is an intelligent multi-agent platform that helps users make informed cryptocurrency trading decisions. The system analyzes market data, news, sentiment, and technical indicators to generate buy, sell, or hold signals for various cryptocurrencies.

By leveraging a network of specialized agents and AI integration, the system provides data-driven trading recommendations tailored to user risk profiles and investment strategies.

### Key Features

- **Real-time market data analysis** from CoinGecko API
- **Fear & Greed Index monitoring** for market sentiment
- **Crypto news aggregation** and sentiment analysis
- **Personalized recommendations** based on user risk profile
- **AI-powered decision making** via ASI1 integration
- **Trading dashboard** for visualization and monitoring
- **Automated swap functionality** for executing trades

## System Architecture

The system uses a multi-agent architecture where specialized agents communicate and collaborate to provide trading signals.

```
                                  ┌─────────────────┐
                                  │                 │
                                  │  Main Agent     │
                                  │                 │
                                  └─────┬───────────┘
                                        │
                 ┌──────────────────────┼───────────────────────┐
                 │                      │                       │
        ┌────────▼─────────┐   ┌────────▼─────────┐    ┌────────▼─────────┐
        │                  │   │                  │    │                  │
        │  Coin Info Agent │   │  Crypto News    │    │  Fear & Greed    │
        │                  │   │  Agent          │    │  Index Agent     │
        └──────────────────┘   └──────────────────┘    └──────────────────┘
                                                               │
                                                        ┌──────▼──────┐
                                                        │             │
                                                        │  ASI1 LLM   │
                                                        │  Reasoning  │
                                                        │  Agent      │
                                                        │             │
                                                        └─────────────┘
                                                               │
                                                      ┌────────▼───────┐
                                                      │                │
                                                      │  Action Signal │
                                                      │  (BUY/SELL/    │
                                                      │   HOLD)        │
                                                      │                │
                                                      └────────────────┘
```

### Agent Responsibilities

- **Main Agent**: Orchestrates the entire workflow and user interaction
- **Coin Info Agent**: Retrieves cryptocurrency market data from APIs
- **Crypto News Agent**: Gathers and analyzes latest crypto news
- **Fear & Greed Index Agent**: Monitors market sentiment
- **ASI1 Reasoning Agent**: Processes data and generates trading signals based on AI reasoning
- **Dashboard Agent**: Visualizes data and signals for user monitoring
- **Swap Agent**: Executes trades based on signals (when enabled)

## Setup Instructions

### Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/crypto-trading-agent.git
   cd crypto-trading-agent
   ```

2. Install Poetry if you don't have it:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Add your API keys:
   ```
   ASI1_API_KEY=your_asi1_api_key
   COINGECKO_API_KEY=your_coingecko_api_key
   # Additional API keys as needed
   ```

### Running the System

Start the main agent:

```bash
poetry run python -m src.crypto_project.main
```

Start individual agents (if running separately):

```bash
# Coin Info Agent
poetry run python -m src.crypto_project.agents.coin_info

# Fear & Greed Index Agent
poetry run python -m src.crypto_project.agents.fear_greed_index

# ASI1 Reasoning Agent
poetry run python -m src.crypto_project.agents.asi1
```

## Usage Examples

### Basic Usage

1. Start the main agent:
   ```bash
   poetry run python -m src.crypto_project.main
   ```

2. Follow the prompt to select the blockchain:
   ```
   Blockchain [ethereum/base/bitcoin/matic-network]? bitcoin
   ```

3. Specify your investor profile:
   ```
   Investor [long-term/short-term/speculate]: long-term
   ```

4. Specify your risk strategy:
   ```
   Risk strategy [conservative/balanced/aggressive/speculative]: balanced
   ```

5. Provide any additional context for decision-making:
   ```
   Any particular reason why you would like to perform Buy/Sell/Hold action? market seems volatile
   ```

6. Receive the recommended action:
   ```
   Analysis complete. Recommendation: HOLD
   ```

### Running the Dashboard

Start the dashboard for visual monitoring:

```bash
poetry run python -m src.crypto_project.agents.dashboard
```

Access the dashboard at: `http://localhost:8050`

## Development Guidelines

### Project Structure

```
crypto_project/
├── src/
│   └── crypto_project/
│       ├── agents/       # Individual agent implementations
│       ├── models/       # Data models for requests/responses
│       ├── integration/  # External API integrations
│       ├── services/     # Business logic services
│       └── utils/        # Utility functions and helpers
├── tests/               # Test suite
└── docs/                # Documentation
```

### Adding a New Agent

1. Create a new agent file in `src/crypto_project/agents/`
2. Implement the agent using the base agent class
3. Define request/response models in `src/crypto_project/models/`
4. Register the agent in the main application

Example:

```python
from uagents import Agent, Context
from src.crypto_project.agents.base import BaseAgent
from src.crypto_project.models.requests import MyAgentRequest
from src.crypto_project.models.responses import MyAgentResponse

class MyNewAgent(BaseAgent):
    def __init__(self, name, port, seed):
        super().__init__(name, port, seed)
        
    async def process_request(self, ctx, msg):
        # Process the request
        result = self.get_data()
        return MyAgentResponse(data=result)

# Initialize and run the agent
if __name__ == "__main__":
    agent = MyNewAgent(
        name="MyNewAgent",
        port=8020,
        seed="my_new_agent_seed"
    )
    agent.run()
```

### Code Style

- Use [Black](https://black.readthedocs.io/) for code formatting
- Follow PEP 8 style guidelines
- Add type hints to function signatures
- Write comprehensive docstrings in Google style

### Testing

Run tests with pytest:

```bash
poetry run pytest
```

## API Documentation

### Agent Communication Protocol

Agents communicate using a standard request-response pattern with defined message models.

#### Coin Info Agent

**Request**:
```python
class CoinRequest(Model):
    blockchain: str  # Blockchain to fetch data for (e.g., "bitcoin", "ethereum")
```

**Response**:
```python
class CoinResponse(Model):
    name: str
    symbol: str
    current_price: float
    market_cap: float
    total_volume: float
    price_change_24h: float
```

#### Fear & Greed Index Agent

**Request**:
```python
class FGIRequest(Model):
    limit: Optional[int] = 1  # Number of days to fetch
```

**Response**:
```python
class FGIResponse(Model):
    data: list[FearGreedData]
    status: str
    timestamp: str
```

#### Crypto News Agent

**Request**:
```python
class CryptonewsRequest(Model):
    limit: Optional[int] = 1  # Number of news items to fetch
```

**Response**:
```python
class CryptonewsResponse(Model):
    cryptoupdates: str  # Latest crypto news
```

#### ASI1 Reasoning Agent

**Request**:
```python
class ASI1Request(Model):
    query: str  # The analysis query with all the data
```

**Response**:
```python
class ASI1Response(Model):
    decision: str  # BUY, SELL, or HOLD recommendation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [uAgents](https://fetch.ai/uagents) - For the multi-agent framework
- [CoinGecko API](https://www.coingecko.com/en/api) - For cryptocurrency market data
- [ASI1](https://asi1.ai/) - For AI reasoning capabilities

# CryptoReason Migration Project

This project contains the migration of the CryptoReason codebase to a new, more maintainable architecture.

## Project Structure

```
migrate/
├── files/                  # The migrated codebase
│   ├── agents/             # Agent implementations
│   │   ├── base.py         # Base agent class
│   │   ├── coin_info.py    # Coin information agent
│   │   ├── crypto_news.py  # Crypto news agent
│   │   ├── fear_greed_index.py  # Fear & Greed Index agent
│   │   ├── reward.py       # Reward payment agent
│   │   ├── topup.py        # Token top-up agent
│   │   ├── swap/           # Swap agents
│   │   │   ├── eth_usdc.py # ETH to USDC swap agent
│   │   │   ├── usdc_eth.py # USDC to ETH swap agent
│   │   │   └── swapfinder.py # Swap finder agent
│   ├── models/             # Data models
│   │   ├── requests.py     # Request model definitions
│   │   ├── responses.py    # Response model definitions
│   ├── services/           # Services for external integrations
│   │   ├── asi1.py         # ASI1 AI service
│   ├── utils/              # Utility functions
│   │   ├── errors.py       # Error handling
│   │   ├── logging.py      # Logging utilities
├── understanding_new.md    # Documentation of the new architecture
```

## Migration Progress

### Implemented Components

- **Architecture**: Established a new architecture with a `BaseAgent` class to standardize agent implementation
- **Agent Implementations**:
  - Coin Info Agent: Fetches cryptocurrency market data
  - Fear & Greed Index Agent: Provides market sentiment data
  - Crypto News Agent: Retrieves cryptocurrency news
  - Reward Agent: Handles token rewards and payments
  - Topup Agent: Manages token top-up operations
  - Swap Agents:
    - ETH to USDC: Swaps Ethereum to USDC on Uniswap
    - USDC to ETH: Swaps USDC to Ethereum on Uniswap
    - Swapfinder: Uses AI to find the best swap agent for a given transaction
- **Core Utilities**:
  - Error handling framework
  - Standardized logging
  - Common data models
- **Services**:
  - ASI1 AI integration for sentiment analysis and agent selection

### Remaining Work

- **Testing**: Create comprehensive tests for all agent implementations
- **Documentation**: Add detailed API documentation and usage examples
- **Configuration**: Create a centralized configuration system
- **Deployment**: Set up deployment scripts and containerization
- **Integration**: Ensure all agents work together correctly in the new system

## How to Use

To run an agent, navigate to the agent's directory and run it as a Python module. For example:

```bash
python -m crypto_project.agents.coin_info
```

Alternatively, use the provided console scripts:

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

# Run the Swap Agents
crypto-eth-usdc
crypto-usdc-eth
crypto-swapfinder
```

## Architecture Design

The new architecture follows these key principles:

1. **Standardization**: All agents inherit from a common `BaseAgent` class
2. **Modularity**: Clear separation of concerns between components
3. **Error Handling**: Comprehensive error handling with custom exceptions
4. **Logging**: Consistent logging across all components
5. **Configuration**: Environment-based configuration with sensible defaults

For more details on the architecture, see the [understanding_new.md](understanding_new.md) document.

# Crypto Project Migration

This repository contains the migration of the crypto project to a new architecture with standardized patterns.

## Project Structure

The project is structured as follows:

```
migrate/
├── files/
│   ├── agents/            # Agent implementations
│   │   ├── base.py        # Base agent class
│   │   ├── fear_greed_index.py
│   │   ├── crypto_news.py
│   │   ├── topup.py
│   │   ├── reward.py
│   │   └── swap/          # Swap-related agents
│   │       ├── eth_usdc.py
│   │       ├── usdc_eth.py
│   │       └── swapfinder.py
│   ├── models/            # Data models
│   │   ├── requests.py
│   │   └── responses.py
│   ├── services/          # Shared services
│   │   ├── logging.py
│   │   └── asi1.py        # AI service integration
│   └── tests/             # Test implementations
│       ├── swap/
│       │   ├── test_eth_to_usdc.py
│       │   ├── test_usdc_to_eth.py
│       │   └── test_swapfinder.py
│       └── README.md      # Test documentation
├── setup.py               # Package setup file
└── README.md              # This file
```

## Migration Progress

The migration is progressing with a focus on modular design and standardized patterns.

### Implemented Components

1. **Base Agent Framework**
   - `BaseAgent` class with common functionality
   - Standardized logging and error handling
   - Message registration system

2. **Data Agents**
   - Fear & Greed Index Agent
   - Crypto News Agent

3. **Operational Agents**
   - Top-up Agent
   - Reward Agent

4. **Swap Agents**
   - ETH to USDC swap agent
   - USDC to ETH swap agent
   - Swapfinder agent that uses AI to identify the best swap option

5. **Testing Framework**
   - Test clients for swap functionality
   - Documentation for running tests

### Remaining Work

1. **Additional Agents**
   - Any missing agents from the original codebase
   
2. **Integration Tests**
   - End-to-end testing of agent interactions
   
3. **Documentation**
   - Additional usage examples
   - API documentation

## Usage

### Running Agents

Each agent can be run using its respective console script:

```bash
# Run the Fear & Greed Index agent
crypto-fgi

# Run the Crypto News agent
crypto-news

# Run the Top-up agent
crypto-topup

# Run the Reward agent
crypto-reward

# Run Swap agents
crypto-eth-usdc
crypto-usdc-eth
crypto-swapfinder
```

### Running Tests

Tests for each component can be run using the Python module path:

```bash
# Run the ETH to USDC swap test
python -m crypto_project.tests.swap.test_eth_to_usdc

# Run the USDC to ETH swap test
python -m crypto_project.tests.swap.test_usdc_to_eth

# Run the Swapfinder test
python -m crypto_project.tests.swap.test_swapfinder
```

Refer to the [test documentation](files/tests/README.md) for more details on running and using the tests.

## Architecture Design

The architecture follows these key principles:

1. **Standardization**: All agents follow a consistent pattern defined by the `BaseAgent` class.

2. **Modularity**: Each agent encapsulates specific functionality and can work independently.

3. **Error Handling**: Comprehensive error handling and logging throughout.

4. **Logging**: Consistent logging pattern for easier debugging and monitoring.

5. **Configuration**: Environment-based configuration for flexibility.

## Contributing

When adding new functionality:

1. Follow the established patterns for consistency
2. Create appropriate test cases in the tests directory
3. Update documentation as needed 