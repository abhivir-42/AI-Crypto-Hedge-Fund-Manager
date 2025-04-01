# Understanding the New Code Structure

This document provides an analysis of the current implementation in the `migrate/files` folder, including the architectural design, patterns, and existing components.

## Overall Architecture

The new architecture follows a modular, object-oriented design with clear separation of concerns:

1. **Models**: Data structures for inter-agent communication
2. **Agents**: Individual agent implementations with specific responsibilities
3. **Services**: Business logic and external API integrations
4. **Config**: Centralized configuration management
5. **Utils**: Shared utilities for logging, error handling, etc.

## Design Patterns

### Base Agent Pattern
A `BaseAgent` class provides common functionality for all agents, including:
- Initialization and configuration
- Logging setup
- Error handling
- Message sending
- Event handling

All agent implementations extend this base class, ensuring consistent behavior.

### Service Pattern
Services encapsulate business logic and external integrations:
- The `ASI1Service` handles LLM API communication
- Core functionality is exposed through clean interfaces
- Error handling and retries are managed internally

### Dependency Injection
Configuration is passed to components via constructor parameters, making it easy to test and modify behavior.

### Centralized Configuration
The `settings.py` file provides centralized access to all configuration values from environment variables.

## Current Implementations

### Models
- **Requests**: Inter-agent request definitions (`CoinRequest`, `CryptonewsRequest`, etc.)
- **Responses**: Inter-agent response definitions (`CoinResponse`, `FGIResponse`, etc.)

### Agents
- **Main Agent**: Orchestrates the overall system flow
- **ASI1 Agent**: Handles reasoning and trading signal generation

### Services
- **LLM Service**: Communicates with the ASI1 API

### Utils
- **Errors**: Custom exception classes and error handling utilities
- **Logging**: Centralized logging configuration

## Agent Communication Flow

The current implementation supports this flow:
1. Main agent initiates a check for coin data
2. Main agent receives coin data and requests crypto news
3. Main agent receives crypto news and requests FGI data
4. Main agent receives FGI data and requests trading signal from ASI1
5. Main agent receives trading signal and decides action

## Missing Components

The following components are not yet implemented:
1. **Coin Info Agent**: Retrieves cryptocurrency market data
2. **Crypto News Agent**: Retrieves cryptocurrency news
3. **Fear & Greed Index Agent**: Retrieves market sentiment data
4. **Dashboard Agent**: Provides visualization
5. **Reward Agent**: Handles reward-related functionality
6. **Top-up Agent**: Handles top-up functionality
7. **Swap Agents**: Handle cryptocurrency swap operations
8. **Swap Services**: Provide swap-related business logic

## Next Steps

The missing components need to be implemented following the established patterns:
1. Each agent should extend the BaseAgent class
2. Each agent should handle specific models from the models directory
3. Services should be created for external integrations
4. All components should use the centralized error handling and logging 