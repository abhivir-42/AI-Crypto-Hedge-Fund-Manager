#!/bin/bash
# Script to run all agents in the crypto-trading-agent system

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
else
    echo "Error: .env file not found. Please create it from .env.example"
    exit 1
fi

# Check for required environment variables
if [ -z "$ASI1_API_KEY" ]; then
    echo "Error: ASI1_API_KEY not set in .env file"
    exit 1
fi

# Function to run an agent in the background
run_agent() {
    local agent_name=$1
    local agent_module=$2
    
    echo "Starting $agent_name..."
    poetry run python -m $agent_module &
    
    # Save the process ID
    agent_pids+=($!)
    
    # Wait a moment for the agent to initialize
    sleep 3
    
    echo "$agent_name started with PID ${agent_pids[-1]}"
    echo "------------------------------"
}

# Initialize array to store process IDs
declare -a agent_pids

# Start ASI1 reasoning agent (needs to be ready first)
run_agent "ASI1 Reasoning Agent" "src.crypto_project.agents.asi1_agent"

# Start other specialized agents
run_agent "Fear & Greed Index Agent" "src.crypto_project.agents.fear_greed_index"
run_agent "Coin Info Agent" "src.crypto_project.agents.coin_info"
run_agent "Crypto News Agent" "src.crypto_project.agents.crypto_news"

# Start Swap agents
run_agent "ETH to USDC Swap Agent" "src.crypto_project.agents.swap.eth_to_usdc"
run_agent "USDC to ETH Swap Agent" "src.crypto_project.agents.swap.usdc_to_eth"

# Start the main agent last
run_agent "Main Agent" "src.crypto_project.agents.main_agent"

# Optional: Start dashboard agent if needed
# run_agent "Dashboard Agent" "src.crypto_project.agents.dashboard"

echo "All agents started successfully!"
echo "Press Ctrl+C to stop all agents"

# Set up trap to kill all background processes on exit
cleanup() {
    echo "Stopping all agents..."
    for pid in "${agent_pids[@]}"; do
        if ps -p $pid > /dev/null; then
            kill $pid 2>/dev/null || true
        fi
    done
    echo "All agents stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for user to press Ctrl+C
while true; do
    sleep 1
done 