# Test Suite for Crypto Project

This directory contains test files for the various components of the Crypto Project. The tests are designed to validate the functionality of agents and services in the project.

## Test Structure

The test suite is organized into the following directories:

- `swap/`: Tests for swap functionality
  - `test_eth_to_usdc.py`: Tests for ETH to USDC swap agent
  - `test_usdc_to_eth.py`: Tests for USDC to ETH swap agent
  - `test_swapfinder.py`: Tests for the Swapfinder agent that uses AI to determine the best swap path

Additional test directories will be added as more components are implemented.

## Running the Tests

Each test file contains a standalone test client that can be run independently. The test clients use Flask to set up a web server that can send requests to the agents and receive responses.

### Prerequisites

Before running the tests, make sure you have:

1. Set up your environment variables in a `.env` file (see the project's main README for required variables)
2. Started the agent(s) you want to test
3. Installed the required dependencies (Flask, flask-cors, fetchai, etc.)

### Running a Specific Test

To run a specific test, navigate to the project root directory and run:

```bash
python -m crypto_project.tests.swap.test_eth_to_usdc
```

This will start a Flask server on a specific port (each test uses a different port to avoid conflicts).

### Using the Test Client

Once the test server is running, you can interact with it using the command-line interface or by sending HTTP requests:

#### Command-Line Interface

The test servers provide a simple CLI with the following commands:
- `send`: Send a test request to the agent
- `response`: Get the last response received from the agent
- `exit`: Exit the test client

#### HTTP API

You can also send HTTP requests to the test server:

- `POST /send_request`: Send a request to the agent
  ```json
  {
    "blockchain": "base",
    "signal": "buy",
    "amount": 100
  }
  ```

- `GET /last_response`: Get the last response received from the agent

### Example

Running the ETH to USDC test:

```bash
python -m crypto_project.tests.swap.test_eth_to_usdc
```

Then in the CLI:
```
> send
Enter ETH amount: 0.1
Response: {"status": "request_sent", "request": {"blockchain": "base", "signal": "sell", "amount": 0.1}}
> response
Last response: {"response": {"status": "success", "data": {"ethAmount": 0.1, "usdcAmount": 185.32, "txHash": "0x123..."}}}
```

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create a new test file in the appropriate subdirectory
2. Use a unique port for the Flask server to avoid conflicts
3. Follow the existing test pattern for consistency
4. Make sure to include appropriate logging for easier debugging 