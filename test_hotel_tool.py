#!/usr/bin/env python3
"""
Test script for the hotel tool function.
This script directly calls the get_hotels_near_destination function for debugging.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

from agents.hotel_agent.tools import get_hotels_near_destination

def test_hotel_tool():
    """Test the hotel tool with sample data."""
    
    # Test case 1: Berlin to Amsterdam office
    print("=" * 60)
    print("TEST CASE 1: Berlin to Amsterdam Office")
    print("=" * 60)
    
    result1 = get_hotels_near_destination(
        final_destination="Amsterdam, Netherlands",  # Use a broader location
        departure_date="2025-12-15",  # Use closer dates
        return_date="2025-12-20",
        country_code="NL",
        locality="Amsterdam",
        hotel_rating_preference="budget-friendly",
        hotel_extras_preference=["Wi-Fi", "breakfast included"],
        include_breakfast=False,  # Remove breakfast filter
        free_cancellation=False,  # Remove cancellation filter
        transport_mode="walk",
        top_k=5
    )
    
    print(f"Status: {result1.status}")
    print(f"Total results: {result1.total_results}")
    print(f"Number of items returned: {len(result1.items)}")
    if result1.message:
        print(f"Message: {result1.message}")
    
    if result1.items:
        print("\nFirst hotel result:")
        hotel = result1.items[0]
        print(f"  Name: {hotel.name}")
        print(f"  Address: {hotel.address}")
        print(f"  Price: {hotel.total_price_amount} {hotel.total_price_currency}")
        print(f"  Distance: {hotel.distance_meters} meters")
        print(f"  Travel time: {hotel.travel_time_seconds} seconds")
    
    print("\n" + "=" * 60)
    print("TEST CASE 2: Paris Office")
    print("=" * 60)
    
    # Test case 2: Paris office (more generic address)
    result2 = get_hotels_near_destination(
        final_destination="Paris office",
        departure_date="2025-11-20",
        return_date="2025-11-24",
        country_code="FR",
        locality="Paris",
        hotel_rating_preference="mid-range",
        hotel_extras_preference=["Wi-Fi", "breakfast included"],
        include_breakfast=True,
        free_cancellation=True,
        transport_mode="walk",
        top_k=3
    )
    
    print(f"Status: {result2.status}")
    print(f"Total results: {result2.total_results}")
    print(f"Number of items returned: {len(result2.items)}")
    if result2.message:
        print(f"Message: {result2.message}")
    
    if result2.items:
        print("\nFirst hotel result:")
        hotel = result2.items[0]
        print(f"  Name: {hotel.name}")
        print(f"  Address: {hotel.address}")
        print(f"  Price: {hotel.total_price_amount} {hotel.total_price_currency}")
        print(f"  Distance: {hotel.distance_meters} meters")
        print(f"  Travel time: {hotel.travel_time_seconds} seconds")

if __name__ == "__main__":
    try:
        test_hotel_tool()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()