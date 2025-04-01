# Project Setup Guide

This document provides the necessary configuration files and directory structure for setting up the crypto trading agent project with Poetry for dependency management.

## 1. Poetry Configuration (pyproject.toml)

Below is the `pyproject.toml` file configuration for the project:
```toml
[tool.poetry]
name = "crypto-trading-agent"
version = "0.1.0"
description = "A multi-agent system for cryptocurrency trading signals and automated swaps"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
license = "MIT"
packages = [{include = "crypto_project", from = "src"}]

[tool.poetry.dependencies]
python = "^3.9"
# Agent system dependencies
fetchai = "0.1.24"
uagents = "0.6.0"
uagents-core = "0.1.1"
flask = "^2.3.2"
flask-cors = "^5.0.0"

# Data processing and visualization
dash = "^2.18.2"
dash-bootstrap-components = "^1.4.1"
pandas = "^2.2.3"
plotly = "^5.15.0"

# API integration
openai = "^1.55.3"
requests = "^2.31.0"
backoff = "^2.2.1"

# Blockchain/Web3 dependencies
web3 = "^6.4.0"
uniswap-universal-router-decoder = "^0.8.0"

# Configuration and environment
python-dotenv = "^1.0.1"
pydantic = "^2.4.2"

[tool.poetry.group.dev.dependencies]
# Testing
pytest = "^7.3.1"
pytest-cov = "^4.1.0"
pytest-mock = "^3.10.0"
pytest-asyncio = "^0.21.0"
requests-mock = "^1.11.0"

# Linting and formatting
black = "^23.3.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
mypy = "^1.3.0"
pylint = "^2.17.4"

# Documentation
sphinx = "^7.0.1"
sphinx-rtd-theme = "^1.2.1"

# Development tools
pre-commit = "^3.3.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ["py39"]
include = '\.pyi?$'

[tool.isort]
profile = "black"
line_length = 88
multi_line_output = 3

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
asyncio_mode = "auto"
```

## 2. Environment Variables (.env.example)

Below is an example `.env.example` file listing all required environment variables:

```
# API Keys
ASI1_API_KEY=your_asi1_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
AGENTVERSE_API_KEY=your_agentverse_api_key_here

# Blockchain Configuration
METAMASK_PRIVATE_KEY=your_private_key_here
BASE_RPC_URL=https://mainnet.base.org

# Agent Configuration
MAIN_AGENT_SEED=this_is_main_agent_to_run
ASI1_AGENT_SEED=asi1_reasoning_agent_seed_phrase
ETH_USDC_AGENT_SEED=eth_usdc_agent_seed_phrase
USDC_ETH_AGENT_SEED=usdc_eth_agent_seed_phrase

# Server Configuration
MAIN_AGENT_PORT=8017
ASI1_AGENT_PORT=8018
ETH_USDC_AGENT_PORT=5002
USDC_ETH_AGENT_PORT=5004
```

## 3. Project Directory Structure

```
crypto-trading-agent/
├── .github/                          # GitHub workflows for CI/CD
│   └── workflows/
│       ├── test.yml
│       └── lint.yml
├── .vscode/                          # VSCode configuration (optional)
│   └── settings.json
├── src/                              # Source code
│   └── crypto_project/               # Main package
│       ├── __init__.py
│       ├── config/                   # Configuration management
│       │   ├── __init__.py
│       │   └── settings.py           # Centralized settings (NEW)
│       ├── models/                   # Data models
│       │   ├── __init__.py
│       │   ├── requests.py           # From original model definitions in main.py
│       │   └── responses.py          # From original model definitions in main.py
│       ├── agents/                   # Agent implementations
│       │   ├── __init__.py
│       │   ├── base.py               # Base agent class (NEW)
│       │   ├── main_agent.py         # From cryptoreason/main.py
│       │   ├── coin_info.py          # From cryptoreason/coininfo_agent.py
│       │   ├── crypto_news.py        # From cryptoreason/cryptonews_agent.py
│       │   ├── fear_greed_index.py   # From cryptoreason/fgi_agent.py
│       │   ├── dashboard.py          # From cryptoreason/dashboard_agent.py
│       │   ├── reward.py             # From cryptoreason/reward_agent.py
│       │   ├── topup.py              # From cryptoreason/topup_agent.py
│       │   ├── asi1_agent.py         # From cryptoreason/asi/llm_agent.py
│       │   └── swap/                 # Swap agents
│       │       ├── __init__.py
│       │       ├── eth_to_usdc.py    # From cryptoreason/swapland/test_ethTOusdc.py
│       │       ├── usdc_to_eth.py    # From cryptoreason/swapland/test_usdcTOeth.py
│       │       └── swapfinder.py     # From cryptoreason/swapland/swapfinder_agent.py
│       ├── services/                 # Business logic services
│       │   ├── __init__.py
│       │   ├── llm_service.py        # From cryptoreason/swapland/llm_swapfinder.py
│       │   └── swap_service/         # Swap functionality
│       │       ├── __init__.py
│       │       ├── eth_usdc.py       # From cryptoreason/swapland/uni_base_ethusdc.py
│       │       └── usdc_eth.py       # From cryptoreason/swapland/uni_base_usdceth.py
│       ├── integration/              # External API integrations
│       │   ├── __init__.py
│       │   ├── asi1.py               # From ASI1 integration code
│       │   ├── coingecko.py          # From coin info fetching code
│       │   └── uniswap.py            # Uniswap integration utilities
│       └── utils/                    # Utility functions
│           ├── __init__.py
│           ├── logging.py            # Centralized logging (from main.py)
│           └── errors.py             # Error handling utilities (from main.py)
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Test fixtures and configuration
│   ├── unit/                         # Unit tests 
│   │   ├── __init__.py
│   │   ├── test_models/              # Tests for models
│   │   ├── test_agents/              # Tests for agents
│   │   ├── test_services/            # Tests for services
│   │   └── test_integration/         # Tests for integrations
│   └── integration/                  # Integration tests
│       ├── __init__.py
│       └── test_workflows.py         # End-to-end workflow tests
├── docs/                             # Documentation
│   ├── api.md                        # API documentation
│   ├── architecture.md               # Architecture documentation (NEW)
│   ├── agents.md                     # Agent documentation (NEW)
│   └── images/                       # Documentation images
│       └── architecture_diagram.png  # Based on Project_Flow_Diagram.png
├── scripts/                          # Utility scripts
│   ├── setup_dev.sh                  # Development setup script (NEW)
│   └── run_agents.sh                 # Script to run all agents (NEW)
├── .env.example                      # Example environment variables
├── .gitignore                        # Git ignore file
├── .pre-commit-config.yaml           # Pre-commit hooks configuration (NEW)
├── pyproject.toml                    # Poetry configuration (replacing requirements.txt)
├── README.md                         # Project README
└── LICENSE                           # License file (NEW)
```

## 4. Installation and Setup Instructions

### Prerequisites

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/crypto-trading-agent.git
   cd crypto-trading-agent
   ```

2. Install Poetry if you don't have it:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit the .env file to add your API keys and other configuration
   ```

4. Install dependencies:
   ```bash
   poetry install
   ```

5. Install pre-commit hooks (for development):
   ```bash
   poetry run pre-commit install
   ```

6. Run the tests:
   ```bash
   poetry run pytest
   ```

### Running the Application

Start the main agent:

```bash
poetry run python -m src.crypto_project.agents.main_agent
```

Or use the provided script to run all agents:

```bash
./scripts/run_agents.sh
```

## 5. Development Guidelines

- Use the provided linting tools (black, isort, flake8, mypy) to ensure code quality
- Write tests for all new functionality
- Follow the established project structure
- Use type annotations throughout the codebase
- Document all functions, classes, and modules with docstrings

## 6. Contribution Guidelines

1. Create a feature branch from `main`
2. Make your changes
3. Run linting and tests:
   ```bash
   poetry run black .
   poetry run isort .
   poetry run flake8
   poetry run mypy
   poetry run pytest
   ```
4. Push your changes and create a pull request
5. Wait for CI/CD checks to pass and request a review 
