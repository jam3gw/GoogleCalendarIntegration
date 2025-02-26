#!/usr/bin/env python3
"""
Calendar Analysis with Anthropic Claude

This script retrieves Google Calendar events and uses Anthropic's Claude API
to provide summaries, analysis, and recommendations based on your schedule.
"""

import os
import json
import datetime
import argparse
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from calendar_api import GoogleCalendarAPI, get_last_seven_days_events

# Load environment variables from .env file
load_dotenv()

# Default number of days to analyze
DEFAULT_DAYS = 7

def get_calendar_events(days_back: int = DEFAULT_DAYS, include_details: bool = True) -> List[Dict[str, Any]]:
    """
    Retrieve calendar events from the specified number of days back.
    
    Args:
        days_back: Number of days to look back for events.
        include_details: Whether to include additional event details.
        
    Returns:
        List of formatted calendar events.
    """
    calendar_api = GoogleCalendarAPI()
    events = calendar_api.get_events(days_back=days_back)
    return calendar_api.format_events(events, include_details=include_details)

def categorize_events(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Attempt to categorize events into common types based on their titles and descriptions.
    This is a simple heuristic approach that can be improved with more sophisticated methods.
    
    Args:
        events: List of calendar events.
        
    Returns:
        Dictionary mapping category names to lists of events.
    """
    categories = {
        "work": [],
        "meeting": [],
        "personal": [],
        "travel": [],
        "social": [],
        "health": [],
        "other": []
    }
    
    # Simple keyword-based categorization
    keywords = {
        "work": ["work", "project", "deadline", "report", "task", "review", "client"],
        "meeting": ["meeting", "call", "conference", "sync", "discussion", "interview", "1:1", "1on1"],
        "travel": ["flight", "train", "trip", "travel", "commute", "drive", "airport"],
        "social": ["dinner", "lunch", "coffee", "drinks", "party", "celebration", "birthday", "wedding", "restaurant"],
        "health": ["doctor", "dentist", "gym", "workout", "exercise", "therapy", "medical", "appointment"],
    }
    
    for event in events:
        title = event.get("summary", "").lower()
        desc = event.get("description", "").lower()
        location = event.get("location", "").lower()
        combined_text = f"{title} {desc} {location}"
        
        # Try to match to a category
        matched = False
        for category, terms in keywords.items():
            if any(term in combined_text for term in terms):
                categories[category].append(event)
                matched = True
                break
        
        # If no match, check if it's likely personal or put in "other"
        if not matched:
            if any(attendee.split('@')[0] in title.lower() for attendee in event.get("attendees", [])):
                categories["personal"].append(event)
            else:
                categories["other"].append(event)
    
    return categories

def format_events_for_claude(events: List[Dict[str, Any]], days_back: int) -> str:
    """
    Format calendar events into a string suitable for sending to Claude.
    
    Args:
        events: List of calendar events.
        days_back: Number of days analyzed.
        
    Returns:
        Formatted string of events.
    """
    if not events:
        return "No events found in the specified time period."
    
    # Group events by day
    events_by_day = {}
    for event in events:
        # Get just the date part
        date_str = event['start'].split('T')[0] if 'T' in event['start'] else event['start']
        
        if date_str not in events_by_day:
            events_by_day[date_str] = []
        
        events_by_day[date_str].append(event)
    
    # Format events grouped by day
    formatted_text = f"Calendar Events for the Past {days_back} Days:\n\n"
    
    for date, day_events in sorted(events_by_day.items()):
        formatted_text += f"Date: {date} ({len(day_events)} events)\n"
        
        for event in day_events:
            # Format event time
            if event['is_all_day']:
                time_str = "All day"
            else:
                time_str = event['start'].split('T')[1][:5] if 'T' in event['start'] else 'All day'
            
            # Format event details
            formatted_text += f"- {time_str}: {event['summary']}\n"
            
            if 'location' in event and event['location']:
                formatted_text += f"  Location: {event['location']}\n"
            
            if 'description' in event and event['description']:
                # Truncate long descriptions
                desc = event['description']
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                formatted_text += f"  Description: {desc}\n"
            
            if 'attendees' in event and event['attendees']:
                attendees = event['attendees']
                attendee_str = ", ".join(attendees[:3])
                if len(attendees) > 3:
                    attendee_str += f" and {len(attendees) - 3} more"
                formatted_text += f"  Attendees: {attendee_str}\n"
            
            formatted_text += "\n"
    
    # Add categorized events
    categories = categorize_events(events)
    formatted_text += "\nEvent Categories:\n"
    for category, category_events in categories.items():
        if category_events:
            formatted_text += f"{category.capitalize()}: {len(category_events)} events\n"
    
    return formatted_text

def get_claude_analysis(events_text: str, api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Use Anthropic's Claude API to analyze calendar events.
    
    Args:
        events_text: Formatted string of calendar events.
        api_key: Anthropic API key. If None, will try to get from environment.
        
    Returns:
        Dictionary containing summary, analysis, and recommendations.
    """
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "No valid Anthropic API key provided. Either pass it as an argument or "
                "set it in the .env file or ANTHROPIC_API_KEY environment variable."
            )
    
    try:
        # Initialize the Anthropic client
        client = Anthropic(api_key=api_key)
        
        prompt = f"""
        I'm going to provide you with my calendar events from the past few days. Please analyze them and provide:

        1. A concise summary of my schedule
        2. An analysis of the frequency and balance of different types of events
        3. Recommendations for how I might better balance my time in the coming days

        Here are my calendar events:

        {events_text}

        Please format your response as JSON with the following structure:
        {{
            "summary": "A paragraph summarizing my schedule",
            "analysis": "A paragraph analyzing the frequency and balance of different types of events",
            "recommendations": "A paragraph with specific recommendations for better time management"
        }}
        
        Ensure your JSON is valid and does not contain any control characters, newlines within strings, or other invalid JSON syntax.
        """
        
        # Send the request to Claude
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Using a more recent model
            max_tokens=2000,
            temperature=0.2,
            system="You are a helpful assistant that analyzes calendar data and provides insightful time management advice. Always return valid JSON.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the JSON response
        content = response.content[0].text
        
        # Look for JSON structure
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            
            # Clean the JSON string to remove potential control characters
            # Replace common control characters with spaces
            for i in range(32):
                json_str = json_str.replace(chr(i), ' ')
            
            # Handle escaped characters properly
            json_str = json_str.replace('\\"', '"')
            json_str = json_str.replace('\\n', ' ')
            
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Problematic JSON: {json_str}")
                # Fall back to a structured response
                return {
                    "summary": "Error parsing Claude's response as JSON.",
                    "analysis": "The API returned a response that couldn't be parsed as JSON.",
                    "recommendations": f"Technical details: {str(e)}"
                }
        else:
            # If no JSON found, create a structured response from the text
            return {
                "summary": "Error parsing Claude's response as JSON.",
                "analysis": content,
                "recommendations": "Please check the API response format."
            }
    except Exception as e:
        return {
            "summary": f"Error: {str(e)}",
            "analysis": "Unable to analyze the calendar data.",
            "recommendations": "Please check your API key and try again."
        }

def display_analysis(analysis: Dict[str, str]):
    """
    Display the calendar analysis in a formatted way.
    
    Args:
        analysis: Dictionary containing summary, analysis, and recommendations.
    """
    print("\n" + "=" * 80)
    print("CALENDAR ANALYSIS".center(80))
    print("=" * 80 + "\n")
    
    print("📅 SUMMARY")
    print("-" * 80)
    print(analysis.get("summary", "No summary available."))
    print()
    
    print("📊 ANALYSIS")
    print("-" * 80)
    print(analysis.get("analysis", "No analysis available."))
    print()
    
    print("💡 RECOMMENDATIONS")
    print("-" * 80)
    print(analysis.get("recommendations", "No recommendations available."))
    print("\n" + "=" * 80 + "\n")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Analyze calendar events with Claude AI")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, 
                        help=f"Number of days to analyze (default: {DEFAULT_DAYS})")
    parser.add_argument("--api-key", type=str, default=None,
                        help="Anthropic API key (if not provided, will use ANTHROPIC_API_KEY from .env or environment)")
    args = parser.parse_args()
    
    try:
        # Get calendar events
        print(f"Retrieving calendar events from the past {args.days} days...")
        events = get_calendar_events(days_back=args.days, include_details=True)
        
        if not events:
            print("No events found in the specified time period.")
            return
        
        print(f"Found {len(events)} events.")
        
        # Format events for Claude
        events_text = format_events_for_claude(events, args.days)
        
        # Get analysis from Claude
        print("Analyzing events with Claude AI...")
        analysis = get_claude_analysis(events_text, api_key=args.api_key)
        
        # Display the analysis
        display_analysis(analysis)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 