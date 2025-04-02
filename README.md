# AI-Crypto-Hedge-Fund-Manager

## System Configuration

The AI Crypto Hedge Fund Manager consists of several agent microservices that communicate with each other:

1. **Main Agent**: Coordinates all other agents and provides the user interface
   - Port: 8017
   - Address: agent1qfrhxny23vz62v5tr20qnmnjujq8k5t0mxgwdxfap945922t9v4ugqtqkea

2. **Coin Info Agent**: Provides cryptocurrency price and market data
   - Default Address: agent1qw6cxgq4l8hmnjctm43q97vajrytuwjc2e2n4ncdfpqk6ggxcfmxuwdc9rq

3. **Crypto News Agent**: Provides cryptocurrency news and sentiment
   - Default Address: agent1q0ear5f66ljucqhjyehu6mw7ug2c498hwlsfndzv5wmkqvmahz7ggmg6tq9

4. **Fear & Greed Index (FGI) Agent**: Provides market sentiment data
   - Port: 9010
   - Address: agent1q248t3vk8f60y3dqsr2nzu93h7tpz26dy62l4ejdtl9ces2sml8ask8zmdp

5. **ASI1 Reasoning Agent**: Analyzes all data to generate trading signals
   - Port: 9018
   - Address: agent1qgrvpwve5f9emqes3vux9uwkstpjcl5ykmfe6sd8wh2fyhpwrptssttez3y

## Running the System

To run the system:

### Option 1: Using the start script (recommended)

```bash
# Make the script executable if needed
chmod +x start_system.sh

# Run the system
./start_system.sh
```

This script will:
1. Automatically check for and clear any ports in use
2. Start all required agents in the correct order
3. Clean up all processes when the main agent is closed

### Option 2: Starting agents manually

```bash
# Start the FGI agent
python -m src.agents.fear_greed_index &
   
# Start the ASI1 agent
python -m src.agents.asi1_agent &
   
# Start the main agent
python -m src.agents.main_agent
```

2. Interact with the main agent by answering its prompts:
   - Select a blockchain (ethereum/base/bitcoin/matic-network)
   - Specify your investor profile (long-term/short-term/speculate)
   - Choose a risk strategy (conservative/balanced/aggressive/speculative)
   - Provide any additional context for your investment decision

The system will process this information and provide a trading signal (BUY/SELL/HOLD) based on current market data, news sentiment, and AI analysis.

## Testing

You can test the complete system using the included test script:

```bash
python test_main_agent.py
```

This script simulates user input to the main agent and verifies that all agent communications are working correctly.