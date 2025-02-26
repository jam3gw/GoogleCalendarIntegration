#!/usr/bin/env python3
"""
Google Calendar Events Retriever

This script authenticates with Google Calendar API and retrieves events
from the last 7 days for the authenticated user.
"""

import os
import datetime
import json
from dateutil.relativedelta import relativedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes required for Google Calendar API
# Using read-only scope for security
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """
    Authenticate with Google Calendar API.
    
    Returns:
        A Google Calendar API service object.
    """
    creds = None
    
    # Check if token.json exists (for previously saved credentials)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(
            json.loads(open('token.json').read()), SCOPES)
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client secrets from credentials.json
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json file not found. Please download it from "
                    "Google Cloud Console and save it in the current directory."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build and return the Google Calendar API service
    return build('calendar', 'v3', credentials=creds)

def get_last_seven_days_events(service):
    """
    Retrieve events from the last 7 days.
    
    Args:
        service: Authenticated Google Calendar API service object.
        
    Returns:
        List of calendar events from the last 7 days.
    """
    # Calculate time range (now to 7 days ago) using timezone-aware objects
    # Use UTC timezone for consistency
    try:
        # For Python 3.11+
        now = datetime.datetime.now(datetime.UTC)
    except AttributeError:
        # For older Python versions
        now = datetime.datetime.now(datetime.timezone.utc)
    
    seven_days_ago = now - datetime.timedelta(days=7)
    
    # Format times in RFC3339 format as required by Google Calendar API
    now_str = now.isoformat()  # isoformat() includes the timezone info
    seven_days_ago_str = seven_days_ago.isoformat()
    
    # Query for events
    events_result = service.events().list(
        calendarId='primary',  # 'primary' refers to the user's primary calendar
        timeMin=seven_days_ago_str,
        timeMax=now_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

def format_event(event):
    """
    Format a calendar event for display.
    
    Args:
        event: A Google Calendar event object.
        
    Returns:
        A formatted string representation of the event.
    """
    # Get event start time
    start = event['start'].get('dateTime', event['start'].get('date'))
    
    # Format start time based on whether it's a full-day event or not
    if 'T' in start:  # Has time component
        start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
        start_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    else:  # All-day event
        start_formatted = start
    
    # Return formatted event string
    return f"{start_formatted} - {event['summary']}"

def main():
    """Main function to run the script."""
    try:
        # Authenticate and get service
        service = authenticate_google_calendar()
        
        # Get events from the last 7 days
        events = get_last_seven_days_events(service)
        
        # Display events
        if not events:
            print("No events found in the last 7 days.")
        else:
            print(f"Events from the last 7 days ({len(events)} events):")
            print("-" * 50)
            for event in events:
                print(format_event(event))
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main() 