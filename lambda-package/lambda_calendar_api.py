#!/usr/bin/env python3
"""
Google Calendar API Module for AWS Lambda

This module provides functions to interact with Google Calendar API,
adapted for use in AWS Lambda environments.
"""

import os
import datetime
import json
import boto3
from typing import List, Dict, Any, Optional, Union
from dateutil.parser import parse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class LambdaGoogleCalendarAPI:
    """Class to interact with Google Calendar API in a Lambda environment."""
    
    def __init__(self, credentials_path: str = '/tmp/credentials.json', 
                 token_path: str = '/tmp/token.json',
                 parameter_store_token_name: Optional[str] = None):
        """
        Initialize the LambdaGoogleCalendarAPI class.
        
        Args:
            credentials_path: Path to the credentials.json file.
            token_path: Path to save/load the token.json file.
            parameter_store_token_name: Name of the parameter in AWS Parameter Store
                                       where the token is stored (optional).
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.parameter_store_token_name = parameter_store_token_name
        self.service = self._authenticate()
    
    def _get_token_from_parameter_store(self) -> Optional[str]:
        """
        Retrieve token from AWS Parameter Store.
        
        Returns:
            Token JSON string or None if not found.
        """
        if not self.parameter_store_token_name:
            return None
            
        try:
            ssm = boto3.client('ssm')
            response = ssm.get_parameter(
                Name=self.parameter_store_token_name,
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Error retrieving token from Parameter Store: {e}")
            return None
    
    def _save_token_to_parameter_store(self, token_json: str) -> bool:
        """
        Save token to AWS Parameter Store.
        
        Args:
            token_json: Token JSON string to save.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.parameter_store_token_name:
            return False
            
        try:
            ssm = boto3.client('ssm')
            ssm.put_parameter(
                Name=self.parameter_store_token_name,
                Value=token_json,
                Type='SecureString',
                Overwrite=True
            )
            return True
        except Exception as e:
            print(f"Error saving token to Parameter Store: {e}")
            return False
    
    def _authenticate(self):
        """
        Authenticate with Google Calendar API.
        
        Returns:
            A Google Calendar API service object.
        """
        creds = None
        
        # First try to get token from Parameter Store if configured
        token_json = self._get_token_from_parameter_store()
        if token_json:
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(token_json), SCOPES)
            except Exception as e:
                print(f"Error loading token from Parameter Store: {e}")
        
        # If no token from Parameter Store, check local file
        if not creds and os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as token_file:
                    creds = Credentials.from_authorized_user_info(
                        json.loads(token_file.read()), SCOPES)
            except Exception as e:
                print(f"Error loading token from file: {e}")
        
        # If credentials don't exist or are invalid, refresh them
        if creds and not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                
                # Save the refreshed token
                token_json = creds.to_json()
                with open(self.token_path, 'w') as token_file:
                    token_file.write(token_json)
                
                # Also save to Parameter Store if configured
                self._save_token_to_parameter_store(token_json)
            else:
                # In Lambda, we can't run the local server flow
                # We need to have a valid token already
                raise ValueError(
                    "Token is expired and can't be refreshed in Lambda environment. "
                    "Please generate a new token using the local authentication flow."
                )
        
        # If no valid credentials, we can't proceed in Lambda
        if not creds:
            raise ValueError(
                "No valid credentials found. Please run the authentication flow locally first."
            )
        
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