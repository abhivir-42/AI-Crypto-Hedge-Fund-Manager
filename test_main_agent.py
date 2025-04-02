#!/usr/bin/env python3

"""
Test script for the main agent that connects to all other agents.
"""

import time
import threading
import sys
import os
import logging
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_agent_with_input(agent_command, inputs, timeout=60):
    """Run an agent with a list of inputs and check the output for success."""
    process = subprocess.Popen(
        agent_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,  # Make sure stdin is created
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    
    thread_stop = threading.Event()
    success = False
    output_success = {
        "coin_request": False,
        "coin_response": False,
        "news_request": False,
        "news_response": False,
        "fgi_request": False,
        "fgi_response": False,
        "asi1_request": False,
        "asi1_response": False,
    }
    
    def read_output(pipe, is_error=False):
        nonlocal success, output_success
        prefix = "STDERR: " if is_error else "STDOUT: "
        for line in pipe:
            print(prefix + line.strip())
            
            # Check for successful outputs
            if is_error:  # Only check stderr for these messages
                if "Sent CoinRequest" in line:
                    output_success["coin_request"] = True
                    logger.info("✅ CoinRequest sent")
                elif "Received CoinResponse" in line:
                    output_success["coin_response"] = True
                    logger.info("✅ CoinResponse received")
                elif "Sent CryptonewsRequest" in line:
                    output_success["news_request"] = True
                    logger.info("✅ CryptonewsRequest sent")
                elif "Received CryptonewsResponse" in line:
                    output_success["news_response"] = True
                    logger.info("✅ CryptonewsResponse received")
                elif "Sent FGIRequest" in line:
                    output_success["fgi_request"] = True
                    logger.info("✅ FGIRequest sent")
                elif "Received FGIResponse" in line:
                    output_success["fgi_response"] = True
                    logger.info("✅ FGIResponse received")
                elif "Sent ASI1Request" in line:
                    output_success["asi1_request"] = True
                    logger.info("✅ ASI1Request sent")
                elif "Received ASI1Response" in line and "decision:" in line:
                    output_success["asi1_response"] = True
                    logger.info("✅ ASI1Response received")
                    # If we received all responses, the test is successful
                    if all(output_success.values()):
                        logger.info("🎉 All agent communications successful!")
                        success = True
                        thread_stop.set()
                elif "HOLD decision received" in line:
                    logger.info("✅ HOLD decision detected")
                    success = True
                elif "BUY SIGNAL DETECTED!" in line:
                    logger.info("✅ BUY signal detected")
                    success = True
                elif "SELL SIGNAL DETECTED!" in line:
                    logger.info("✅ SELL signal detected")
                    success = True
    
    # Start threads to read output
    stdout_thread = threading.Thread(target=read_output, args=(process.stdout,))
    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, True))
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()
    
    # Send inputs with delays
    for user_input in inputs:
        if thread_stop.is_set() or process.poll() is not None:
            break
        time.sleep(2)  # Wait a bit before sending each input
        logger.info(f"Sending input: {user_input}")
        try:
            process.stdin.write(user_input + "\n")
            process.stdin.flush()
        except BrokenPipeError:
            logger.error("Broken pipe - process may have terminated")
            break
        except Exception as e:
            logger.error(f"Error sending input: {e}")
            break
    
    # Wait for the timeout or until thread_stop is set
    start_time = time.time()
    while time.time() - start_time < timeout and not thread_stop.is_set():
        if process.poll() is not None:  # Process has terminated
            break
        time.sleep(0.1)
    
    # Check success based on collected responses
    if output_success["asi1_response"]:
        success = True
    
    # Clean up
    if process.poll() is None:  # Process still running
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    
    # Log the test result
    if success:
        logger.info("✅ Main agent test PASSED")
    else:
        logger.error("❌ Main agent test FAILED")
    
    return success

if __name__ == "__main__":
    logger.info("Starting main agent test...")
    
    # Define the command to run the main agent
    command = "python -m src.agents.main_agent"
    
    # Define the inputs to send to the agent
    inputs = [
        "ethereum",    # Blockchain selection
        "long-term",   # Investor profile
        "balanced",    # Risk strategy
        "I want to hedge against inflation"  # Additional context
    ]
    
    logger.info(f"Running command: {command}")
    logger.info(f"With inputs: {inputs}")
    
    # Run the agent and check for success
    success = run_agent_with_input(command, inputs, timeout=60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 