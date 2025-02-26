#!/usr/bin/env python3
"""
Test script for Anthropic API connection.
"""

import os
import sys
from anthropic import Anthropic

def test_anthropic_connection():
    """Test the connection to Anthropic's API."""
    # Check if API key is set
    api_key = "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"
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it with: export ANTHROPIC_API_KEY=your_api_key_here")
        return False
    
    try:
        # Initialize the client
        client = Anthropic(api_key=api_key)
        
        # Send a simple test message
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, Claude! Please respond with a simple 'Hello, I'm working!' message."}
            ]
        )
        
        # Print the response
        print("Anthropic API Test Result:")
        print("-" * 50)
        print(response.content[0].text)
        print("-" * 50)
        print("API connection successful!")
        return True
        
    except Exception as e:
        print(f"Error connecting to Anthropic API: {e}")
        return False

if __name__ == "__main__":
    success = test_anthropic_connection()
    if not success:
        sys.exit(1) 