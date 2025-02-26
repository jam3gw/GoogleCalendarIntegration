#!/usr/bin/env python3
"""
Example script demonstrating how to use the Google Calendar API module.
"""

import json
from calendar_api import GoogleCalendarAPI, get_last_seven_days_events

def example_1_basic_usage():
    """Basic usage example - get events from last 7 days."""
    print("\n=== Example 1: Basic Usage ===")
    events = get_last_seven_days_events()
    
    if not events:
        print("No events found in the last 7 days.")
    else:
        print(f"Found {len(events)} events in the last 7 days:")
        for event in events:
            print(f"- {event['summary']} ({event['start']})")

def example_2_detailed_events():
    """Get detailed event information."""
    print("\n=== Example 2: Detailed Events ===")
    events = get_last_seven_days_events(include_details=True)
    
    if not events:
        print("No events found.")
    else:
        print(f"Found {len(events)} events with details:")
        # Print the first event with all details
        if events:
            print("First event details:")
            print(json.dumps(events[0], indent=2))

def example_3_custom_date_range():
    """Get events from a custom date range."""
    print("\n=== Example 3: Custom Date Range ===")
    # Create API instance
    calendar_api = GoogleCalendarAPI()
    
    # Get events from the last 30 days
    events = calendar_api.get_events(days_back=30)
    formatted_events = calendar_api.format_events(events)
    
    print(f"Found {len(formatted_events)} events in the last 30 days")
    
    # Group events by day
    events_by_day = {}
    for event in formatted_events:
        # Get just the date part
        date_str = event['start'].split('T')[0] if 'T' in event['start'] else event['start']
        
        if date_str not in events_by_day:
            events_by_day[date_str] = []
        
        events_by_day[date_str].append(event)
    
    # Print events grouped by day
    for date, day_events in sorted(events_by_day.items()):
        print(f"\n{date} ({len(day_events)} events):")
        for event in day_events:
            if event['is_all_day']:
                print(f"  All day: {event['summary']}")
            else:
                time_str = event['start'].split('T')[1][:5] if 'T' in event['start'] else 'All day'
                print(f"  {time_str}: {event['summary']}")

def main():
    """Run all examples."""
    try:
        example_1_basic_usage()
        example_2_detailed_events()
        example_3_custom_date_range()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 