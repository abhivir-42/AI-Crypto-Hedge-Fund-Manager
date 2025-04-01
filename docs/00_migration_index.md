# Crypto Trading Agent System - Migration Index

This directory contains all the necessary files and documentation to migrate the crypto trading agent system from its current structure to an improved, maintainable architecture using modern Python best practices.

## Migration Documents

1. **[01_migration_plan.md](01_migration_plan.md)** - Overview of the migration plan with current and proposed structure
2. **[02_main_agent.md](02_main_agent.md)** - Improved implementation of main.py
3. **[03_swap_agents.md](03_swap_agents.md)** - Improved implementations for swap functionality
4. **[04_llm_integration.md](04_llm_integration.md)** - Improved ASI1 LLM integration
5. **[05_project_setup.md](05_project_setup.md)** - Project setup guide with configuration files and directory structure
6. **[06_migration_steps.md](06_migration_steps.md)** - Step-by-step guide for executing the migration
7. **[07_migration_summary.md](07_migration_summary.md)** - Summary of current migration state and accomplishments
8. **[Testing.md](Testing.md)** - Comprehensive guide for testing the system
9. **[RunningTheSystem.md](RunningTheSystem.md)** - Instructions for running the system
10. **[RemainingSteps.md](RemainingSteps.md)** - Remaining tasks needed for full migration
11. **[understanding_new.md](understanding_new.md)** - Explanation of the new code architecture

## Files Directory

The `files/` directory contains the actual source code files to be copied into the new project structure:

- `agents/` - Implementation of all agent classes
  - `main_agent.py` - Main orchestration agent
  - `asi1_agent.py` - ASI1 reasoning agent
  - `coin_info.py` - Coin information agent
  - `crypto_news.py` - Crypto news agent
  - `fear_greed_index.py` - Fear & Greed Index agent
  - `dashboard.py` - Dashboard agent
  - `reward.py` - Reward agent
  - `topup.py` - Top-up agent
  - `swap/` - Swap-related agents
    - `eth_usdc.py` - ETH to USDC swap agent
    - `usdc_eth.py` - USDC to ETH swap agent
    - `swapfinder.py` - Swap finder agent

- `services/` - Service implementations
  - `llm_service.py` - ASI1 LLM integration service
  - `asi1.py` - ASI1 API service
  - `swap_service/` - Swap-related services
    - `eth_usdc.py` - ETH to USDC swap service
    - `usdc_eth.py` - USDC to ETH swap service

- `models/` - Data models
  - `requests.py` - Request models
  - `responses.py` - Response models

- `config/` - Configuration management
  - `settings.py` - Centralized settings

- `utils/` - Utility functions
  - `logging.py` - Centralized logging
  - `errors.py` - Error handling utilities

- `scripts/` - Utility scripts
  - `run_agents.sh` - Script to run all agents

- `tests/` - Test implementations
  - `swap/` - Tests for swap functionality
  - `README.md` - Test documentation

- `.env.example` - Example environment variables file

## Current Migration Status

All agent and service implementations have been completed and are ready to use. The system now features:

- A consistent, modular architecture
- Improved error handling and logging
- Type hints and comprehensive docstrings
- Better configurability through environment variables
- Complete swap service implementations for blockchain interactions

The remaining tasks (detailed in [RemainingSteps.md](RemainingSteps.md)) include:
- Creating additional tests
- Obtaining API keys and configuring the environment
- Deploying and monitoring the system

## Getting Started

To begin the migration process, follow these steps:

1. Read [01_migration_plan.md](01_migration_plan.md) to understand the overall plan
2. Set up the new project structure as described in [05_project_setup.md](05_project_setup.md)
3. Follow the detailed migration steps in [06_migration_steps.md](06_migration_steps.md)
4. Review [Testing.md](Testing.md) for testing instructions
5. See [RunningTheSystem.md](RunningTheSystem.md) for instructions on running the system
6. Complete the remaining tasks listed in [RemainingSteps.md](RemainingSteps.md)

## Requirements

- Python 3.9 or higher
- Poetry for dependency management
- Git for version control
- API keys for external services (ASI1, CoinGecko, etc.)

## Additional Resources

- The original code for reference is in the `cryptoreason/` directory
- Understanding of the existing code structure is in `cryptoreason/understanding_old_code.md`
- The API documentation and architecture diagrams are in the `docs/` directory 