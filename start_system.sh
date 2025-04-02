#!/bin/bash
# Start script for AI Crypto Hedge Fund Manager
# This script starts all the required agent microservices

# Set current directory as the project root
cd "$(dirname "$0")"

# Function to check if a port is in use
check_port() {
  lsof -i ":$1" > /dev/null 2>&1
  return $?
}

# Function to kill a process on a specific port
kill_process_on_port() {
  echo "Killing process on port $1..."
  kill $(lsof -i ":$1" | grep LISTEN | awk '{print $2}') 2>/dev/null || true
}

echo "Starting AI Crypto Hedge Fund Manager..."

# Check and clear ports if needed
if check_port 9010; then
  echo "Port 9010 is already in use. Clearing..."
  kill_process_on_port 9010
fi

if check_port 9018; then
  echo "Port 9018 is already in use. Clearing..."
  kill_process_on_port 9018
fi

if check_port 8017; then
  echo "Port 8017 is already in use. Clearing..."
  kill_process_on_port 8017
fi

# Start the FGI agent
echo "Starting Fear & Greed Index Agent..."
python -m src.agents.fear_greed_index &
FGI_PID=$!
echo "FGI Agent started with PID: $FGI_PID"

# Wait for FGI agent to initialize and check if it's still running
sleep 2
if ! ps -p $FGI_PID > /dev/null; then
  echo "FGI Agent failed to start. Check logs for details."
  exit 1
fi

# Start the ASI1 agent
echo "Starting ASI1 Reasoning Agent..."
python -m src.agents.asi1_agent &
ASI1_PID=$!
echo "ASI1 Agent started with PID: $ASI1_PID"

# Wait for ASI1 agent to initialize and check if it's still running
sleep 2
if ! ps -p $ASI1_PID > /dev/null; then
  echo "ASI1 Agent failed to start. Check logs for details."
  # Cleanup
  kill $FGI_PID 2>/dev/null || true
  exit 1
fi

# Start the main agent
echo "Starting Main Agent..."
python -m src.agents.main_agent

# When main agent exits, clean up by killing other agents
echo "Main Agent exited. Cleaning up..."
kill $FGI_PID $ASI1_PID 2>/dev/null || true

echo "All agents have been terminated." 