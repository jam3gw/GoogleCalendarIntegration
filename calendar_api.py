#!/usr/bin/env python3
"""
Google Calendar API Module

This module provides functions to interact with Google Calendar API,
including authentication and retrieving events within a specified date range.
"""

import os
import datetime
import json
from typing import List, Dict, Any, Optional, Union
from dateutil.parser import parse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarAPI:
    """Class to interact with Google Calendar API."""
    
    def __init__(self, credentials_path: str = 'credentials.json', 
                 token_path: str = 'token.json'):
        """
        Initialize the GoogleCalendarAPI class.
        
        Args:
            credentials_path: Path to the credentials.json file.
            token_path: Path to save/load the token.json file.
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Google Calendar API.
        
        Returns:
            A Google Calendar API service object.
        """
        creds = None
        
        # Check if token.json exists (for previously saved credentials)
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(open(self.token_path).read()), SCOPES)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Load client secrets from credentials.json
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"{self.credentials_path} file not found. Please download it from "
                        "Google Cloud Console and save it in the current directory."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for future runs
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build and return the Google Calendar API service
        return build('calendar', 'v3', credentials=creds)
    
    def get_events(self, 
                  days_back: int = 7, 
                  calendar_id: str = 'primary',
                  max_results: int = 100,
                  include_recurring: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve events from a specified number of days back until now.
        
        Args:
            days_back: Number of days to look back for events.
            calendar_id: ID of the calendar to fetch events from.
            max_results: Maximum number of events to return.
            include_recurring: Whether to include recurring events.
            
        Returns:
            List of calendar events.
        """
        # Calculate time range using timezone-aware objects
        try:
            # For Python 3.11+
            now = datetime.datetime.now(datetime.UTC)
        except AttributeError:
            # For older Python versions
            now = datetime.datetime.now(datetime.timezone.utc)
            
        start_date = now - datetime.timedelta(days=days_back)
        
        # Format times in RFC3339 format
        now_str = now.isoformat()  # isoformat() includes the timezone info
        start_date_str = start_date.isoformat()
        
        # Query for events
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_date_str,
            timeMax=now_str,
            maxResults=max_results,
            singleEvents=include_recurring,  # True expands recurring events
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    
    def format_events(self, events: List[Dict[str, Any]], 
                     include_details: bool = False) -> List[Dict[str, Any]]:
        """
        Format calendar events into a more usable structure.
        
        Args:
            events: List of Google Calendar event objects.
            include_details: Whether to include additional event details.
            
        Returns:
            List of formatted event dictionaries.
        """
        formatted_events = []
        
        for event in events:
            # Get basic event info
            event_id = event.get('id', '')
            summary = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            
            # Get start and end times
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Determine if it's an all-day event
            is_all_day = 'date' in event['start'] and 'dateTime' not in event['start']
            
            # Format start and end times
            if is_all_day:
                start_obj = datetime.datetime.strptime(start, '%Y-%m-%d').date()
                end_obj = datetime.datetime.strptime(end, '%Y-%m-%d').date()
                # Adjust end date (Google Calendar sets end date as day after)
                end_obj = end_obj - datetime.timedelta(days=1)
            else:
                start_obj = parse(start)
                end_obj = parse(end)
            
            # Create formatted event dictionary
            formatted_event = {
                'id': event_id,
                'summary': summary,
                'start': start_obj.isoformat(),
                'end': end_obj.isoformat(),
                'is_all_day': is_all_day,
            }
            
            # Add additional details if requested
            if include_details:
                formatted_event.update({
                    'description': description,
                    'location': location,
                    'creator': event.get('creator', {}).get('email', ''),
                    'organizer': event.get('organizer', {}).get('email', ''),
                    'attendees': [a.get('email') for a in event.get('attendees', [])],
                    'status': event.get('status', ''),
                    'link': event.get('htmlLink', '')
                })
            
            formatted_events.append(formatted_event)
        
        return formatted_events

def get_last_seven_days_events(credentials_path: str = 'credentials.json',
                              include_details: bool = False) -> List[Dict[str, Any]]:
    """
    Convenience function to get events from the last 7 days.
    
    Args:
        credentials_path: Path to the credentials.json file.
        include_details: Whether to include additional event details.
        
    Returns:
        List of formatted calendar events from the last 7 days.
    """
    calendar_api = GoogleCalendarAPI(credentials_path=credentials_path)
    events = calendar_api.get_events(days_back=7)
    return calendar_api.format_events(events, include_details=include_details)

if __name__ == '__main__':
    # Example usage
    try:
        events = get_last_seven_days_events(include_details=True)
        
        if not events:
            print("No events found in the last 7 days.")
        else:
            print(f"Events from the last 7 days ({len(events)} events):")
            print("-" * 50)
            for event in events:
                if event['is_all_day']:
                    print(f"{event['start']} (All day) - {event['summary']}")
                else:
                    start_time = parse(event['start']).strftime('%Y-%m-%d %H:%M')
                    print(f"{start_time} - {event['summary']}")
                
                if 'location' in event and event['location']:
                    print(f"  Location: {event['location']}")
                
                if 'attendees' in event and event['attendees']:
                    print(f"  Attendees: {', '.join(event['attendees'][:3])}" + 
                          (f" and {len(event['attendees']) - 3} more" if len(event['attendees']) > 3 else ""))
                
                print()
    
    except Exception as e:
        print(f"An error occurred: {e}") 