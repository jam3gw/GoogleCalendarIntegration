#!/usr/bin/env python3
"""
AWS Lambda Handler for Google Calendar Analysis

This module provides a Lambda handler function that retrieves Google Calendar events
and performs analysis, returning the results as JSON.
"""

import os
import json
import base64
import datetime
from typing import Dict, Any, List

# Import required modules
from lambda_calendar_api import LambdaGoogleCalendarAPI
from calendar_analysis_local import analyze_events, categorize_events

# Default number of days to analyze
DEFAULT_DAYS = 7

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function for Google Calendar analysis.
    
    Args:
        event: The Lambda event data
        context: The Lambda context
        
    Returns:
        Dictionary containing the analysis results and status code
    """
    try:
        # Parse request parameters
        days_back = int(event.get('queryStringParameters', {}).get('days', DEFAULT_DAYS))
        
        # Check if credentials are provided in the environment
        if not os.environ.get('GOOGLE_CREDENTIALS_JSON'):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Google credentials not configured in environment variables'
                })
            }
        
        # Decode and save credentials from environment variable
        credentials_json = base64.b64decode(os.environ.get('GOOGLE_CREDENTIALS_JSON')).decode('utf-8')
        token_json = os.environ.get('GOOGLE_TOKEN_JSON')
        
        # Create temporary credential files
        with open('/tmp/credentials.json', 'w') as f:
            f.write(credentials_json)
        
        if token_json:
            with open('/tmp/token.json', 'w') as f:
                f.write(base64.b64decode(token_json).decode('utf-8'))
        
        # Initialize the Google Calendar API with temporary files
        calendar_api = LambdaGoogleCalendarAPI(
            credentials_path='/tmp/credentials.json',
            token_path='/tmp/token.json',
            parameter_store_token_name=os.environ.get('TOKEN_PARAMETER_NAME')
        )
        
        # Get calendar events
        events = calendar_api.get_events(days_back=days_back)
        formatted_events = calendar_api.format_events(events, include_details=True)
        
        # Save the updated token for future use
        if os.path.exists('/tmp/token.json'):
            with open('/tmp/token.json', 'r') as f:
                updated_token = f.read()
                # In a real implementation, you would store this token securely
                # For example, in AWS Parameter Store or Secrets Manager
        
        # Analyze events
        analysis_results = analyze_events(formatted_events, days_back)
        
        # Return the results
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'events_count': len(formatted_events),
                'days_analyzed': days_back,
                'analysis': analysis_results
            })
        }
        
    except Exception as e:
        # Log the error (CloudWatch will capture this)
        print(f"Error: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'An error occurred: {str(e)}'
            })
        }

# For local testing
if __name__ == "__main__":
    # Simulate a Lambda event
    test_event = {
        'queryStringParameters': {
            'days': '7'
        }
    }
    
    # Call the handler
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2)) 