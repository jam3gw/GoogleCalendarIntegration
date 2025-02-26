#!/usr/bin/env python3
"""
Calendar Analysis (Local Version)

This script retrieves Google Calendar events and provides a local analysis
without requiring the Anthropic API.
"""

import os
import json
import datetime
import argparse
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
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

def analyze_events(events: List[Dict[str, Any]], days_back: int) -> Dict[str, str]:
    """
    Perform a local analysis of calendar events without using the Anthropic API.
    
    Args:
        events: List of calendar events.
        days_back: Number of days analyzed.
        
    Returns:
        Dictionary containing summary, analysis, and recommendations.
    """
    if not events:
        return {
            "summary": "No events found in the specified time period.",
            "analysis": "No data to analyze.",
            "recommendations": "No recommendations available."
        }
    
    # Categorize events
    categories = categorize_events(events)
    
    # Count events by category
    category_counts = {category: len(events_list) for category, events_list in categories.items() if events_list}
    
    # Count events by day
    events_by_day = {}
    for event in events:
        date_str = event['start'].split('T')[0] if 'T' in event['start'] else event['start']
        if date_str not in events_by_day:
            events_by_day[date_str] = []
        events_by_day[date_str].append(event)
    
    # Calculate busiest and lightest days
    day_counts = {day: len(day_events) for day, day_events in events_by_day.items()}
    busiest_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else ("None", 0)
    lightest_day = min(day_counts.items(), key=lambda x: x[1]) if day_counts else ("None", 0)
    
    # Calculate average events per day
    avg_events_per_day = len(events) / len(events_by_day) if events_by_day else 0
    
    # Generate summary
    summary = (
        f"Over the past {days_back} days, you had {len(events)} events "
        f"across {len(events_by_day)} days, averaging {avg_events_per_day:.1f} events per day. "
    )
    
    # Generate analysis
    analysis = (
        f"Your calendar shows the following distribution of events: "
    )
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            analysis += f"{category.capitalize()}: {count} events ({count/len(events)*100:.1f}%), "
    
    analysis += (
        f"Your busiest day was {busiest_day[0]} with {busiest_day[1]} events, "
        f"while your lightest day was {lightest_day[0]} with {lightest_day[1]} events. "
    )
    
    # Generate recommendations
    recommendations = "Based on your calendar data, here are some suggestions:\n"
    
    # Check for balance
    if len(category_counts) <= 2:
        recommendations += "- Your calendar appears to be focused on a limited number of categories. Consider diversifying your activities for better work-life balance.\n"
    
    # Check for overloaded days
    if busiest_day[1] > 5:
        recommendations += f"- Your busiest day ({busiest_day[0]}) had {busiest_day[1]} events. Consider spreading out commitments more evenly when possible.\n"
    
    # Check for specific category imbalances
    if category_counts.get("work", 0) + category_counts.get("meeting", 0) > len(events) * 0.7:
        recommendations += "- Work-related events dominate your calendar. Consider allocating more time for personal activities and self-care.\n"
    
    if category_counts.get("health", 0) == 0:
        recommendations += "- No health-related events were found. Consider scheduling time for exercise or wellness activities.\n"
    
    if not recommendations.endswith("\n"):
        recommendations += "- Your calendar appears to be well-balanced across different categories of activities."
    
    return {
        "summary": summary,
        "analysis": analysis,
        "recommendations": recommendations
    }

def display_analysis(analysis: Dict[str, str]):
    """
    Display the calendar analysis in a formatted way.
    
    Args:
        analysis: Dictionary containing summary, analysis, and recommendations.
    """
    print("\n" + "=" * 80)
    print("CALENDAR ANALYSIS (LOCAL)".center(80))
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
    parser = argparse.ArgumentParser(description="Analyze calendar events locally")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, 
                        help=f"Number of days to analyze (default: {DEFAULT_DAYS})")
    args = parser.parse_args()
    
    try:
        # Get calendar events
        print(f"Retrieving calendar events from the past {args.days} days...")
        events = get_calendar_events(days_back=args.days, include_details=True)
        
        if not events:
            print("No events found in the specified time period.")
            return
        
        print(f"Found {len(events)} events.")
        
        # Analyze events locally
        print("Analyzing events locally...")
        analysis = analyze_events(events, args.days)
        
        # Display the analysis
        display_analysis(analysis)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 