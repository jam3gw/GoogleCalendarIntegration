#!/usr/bin/env python3
"""
Test script for Anthropic API connection using dotenv.
"""

import os
import sys
import json
from dotenv import load_dotenv
from anthropic import Anthropic, APIError, APIConnectionError, AuthenticationError

def validate_api_key(api_key):
    """Validate the format of the Anthropic API key."""
    if not api_key:
        return False, "API key is empty"
    
    if not api_key.startswith("sk-ant-"):
        return False, "API key should start with 'sk-ant-'"
    
    if len(api_key) < 30:  # Anthropic keys are typically longer
        return False, "API key appears too short"
    
    return True, "API key format appears valid"

def test_anthropic_connection():
    """Test the connection to Anthropic's API using the key from .env."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API key is set
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Error: ANTHROPIC_API_KEY is not properly set in the .env file.")
        print("Please edit the .env file and set your actual API key.")
        return False
    
    # Validate API key format
    is_valid, message = validate_api_key(api_key)
    if not is_valid:
        print(f"Warning: {message}")
        print(f"API key: {api_key[:5]}...{api_key[-5:]} (length: {len(api_key)})")
    else:
        print(f"API key format check: {message}")
        print(f"Using API key: {api_key[:5]}...{api_key[-5:]} (length: {len(api_key)})")
    
    try:
        # Initialize the client
        client = Anthropic(api_key=api_key)
        
        # Send a simple test message
        print("Sending test request to Anthropic API...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Hello, Claude! Please respond with a simple 'Hello, I'm working!' message."}
            ]
        )
        
        # Print the response
        print("\nAnthropic API Test Result:")
        print("-" * 50)
        print(response.content[0].text)
        print("-" * 50)
        print("API connection successful!")
        return True
        
    except AuthenticationError as e:
        print(f"\nAuthentication Error: {e}")
        print("This usually means your API key is invalid or has been revoked.")
        print("Please check your API key in the .env file and ensure it's correct.")
        print("You can get a new API key from: https://console.anthropic.com/")
        return False
    except APIConnectionError as e:
        print(f"\nAPI Connection Error: {e}")
        print("This usually indicates network issues or Anthropic's services might be down.")
        print("Please check your internet connection and try again later.")
        return False
    except APIError as e:
        print(f"\nAPI Error: {e}")
        print(f"Status code: {e.status_code}")
        print(f"Error type: {e.error_type}")
        print(f"Error message: {e.message}")
        return False
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("Anthropic API Connection Test")
    print("=" * 50)
    success = test_anthropic_connection()
    print("\nTest result:", "SUCCESS" if success else "FAILED")
    if not success:
        sys.exit(1) 