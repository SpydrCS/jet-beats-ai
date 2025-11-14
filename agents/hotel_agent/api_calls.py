"""
API Calls Module for Hotel Agent

This module centralizes all external API calls for the hotel agent:
- Google Maps Geocoding API (for address to coordinates conversion)
- RapidAPI Booking.com Hotels API (for hotel search with caching)
- Geoapify Route Matrix API (for distance and travel time calculations)

All API configurations are centralized in API_CONFIG dictionary.
Functions maintain backward compatibility with the original utils.py interface.
"""

import requests
import os
import json
import re
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# API Configuration
API_CONFIG = {
    "google_maps": {
        "api_key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "base_url": "https://maps.googleapis.com/maps/api/geocode/json",
        "timeout": 30,
    },
    "rapid_api": {
        "api_key": os.getenv("RAPID_API_KEY"),
        "host": "booking-com18.p.rapidapi.com",
        "base_url": "https://booking-com18.p.rapidapi.com/stays/search-by-geo",
        "timeout": 60,
    },
    "geoapify": {
        "api_key": os.getenv("GEOAPIFY_API_KEY"),
        "base_url": "https://api.geoapify.com/v1/routematrix",
        "timeout": 30,
    }
}


def sanitize_filename_component(val):
    r"""
    Cleans a string for safe use in filenames (Windows compatible).
    - Replaces spaces with underscores
    - Removes invalid filename characters (: / \\ ? * < > | ")
    Returns '_' if input is None or empty after cleaning.
    """
    if val is None:
        return "_"
    val = str(val)
    val = val.replace(" ", "_")
    val = re.sub(r"[:/\\?*<>|\"]", "", val)
    return val or "_"


def short_coordinate(val):
    """
    Converts a string/float to its integer part as a string.
    Used to shorten latitude/longitude for cache filenames.
    Falls back to sanitize if conversion fails.
    """
    try:
        return str(int(float(val)))
    except Exception:
        return sanitize_filename_component(val)


def call_google_maps_geocoding(address: str, country: str = "", locality: str = "") -> dict:
    """
    Calls Google Maps Geocoding API to get coordinates from an address.
    
    Args:
        address (str): The address to geocode
        country (str): The two letter ISO 3166-1 country code (e.g., "PT")
        locality (str): The locality or city (e.g., "Porto")
        
    Returns:
        dict: Success response with location and viewport, or error dict
    """
    config = API_CONFIG["google_maps"]
    
    components = []
    if country:
        components.append(f"country:{country}")
    if locality:
        components.append(f"locality:{locality}")
        
    params = {
        "address": address,
        "key": config["api_key"],
    }
    
    if components:
        params["components"] = "|".join(components)
    
    try:
        response = requests.get(
            config["base_url"], 
            params=params, 
            timeout=config["timeout"]
        )
        
        if response.status_code != 200:
            return {
                "error": f"Failed to retrieve coordinates. Status code: {response.status_code}"
            }
        
        response_json = response.json()
        if response_json["status"] != "OK":
            return {"error": "Geocoding API error: " + response_json["status"]}
        
        geometry = response_json.get("results")[0].get("geometry", {})
        return {
            "location": geometry.get("location"),
            "viewport": geometry.get("viewport"),
        }
        
    except Exception as e:
        return {"error": f"Geocoding API request failed: {e}"}


def call_rapid_api_hotels(location: dict, checkin_date: str, checkout_date: str, filters: str = "") -> dict:
    """
    Calls RapidAPI Booking.com hotels search with caching.
    
    Args:
        location (dict): Location with viewport containing northeast and southwest bounds
        checkin_date (str): Check-in date in YYYY-MM-DD format
        checkout_date (str): Check-out date in YYYY-MM-DD format
        filters (str): Comma-separated filters
        
    Returns:
        dict: Hotel search results or error dict
    """
    config = API_CONFIG["rapid_api"]
    
    # Generate cache filename - using main responses directory
    ne = location.get("viewport", {}).get("northeast", {})
    sw = location.get("viewport", {}).get("southwest", {})
    cache_filename = (
        f"../responses/hotels_"
        f"lat-{short_coordinate(ne.get('lat'))}_lng-{short_coordinate(ne.get('lng'))}_"
        f"lat-{short_coordinate(sw.get('lat'))}_lng-{short_coordinate(sw.get('lng'))}_"
        f"{sanitize_filename_component(checkin_date)}_{sanitize_filename_component(checkout_date)}_"
        f"{sanitize_filename_component(filters) if filters else 'nofilters'}.json"
    )
    
    # Check cache first
    if os.path.exists(cache_filename):
        try:
            with open(cache_filename, "r", encoding="utf-8") as f:
                print("Loading cached hotel search data from file.")
                return json.load(f)
        except Exception as e:
            print(f"Error reading cache file: {e}")
    
    print("Cached hotel search data not found. Making API request...")
    
    headers = {
        "x-rapidapi-key": config["api_key"],
        "x-rapidapi-host": config["host"],
    }
    
    params = {
        "neLat": ne.get("lat"),
        "neLng": ne.get("lng"),
        "swLat": sw.get("lat"),
        "swLng": sw.get("lng"),
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
    }
    
    if filters:
        params["categoriesFilters"] = filters
    
    print(f"API request params: {params}")
    print(f"API request filters: {filters}")
    
    try:
        response = requests.get(
            config["base_url"],
            headers=headers,
            params=params,
            timeout=config["timeout"]
        )
        
        print(f"API response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API response text: {response.text}")
            return {
                "error": f"Failed to retrieve hotel data. Status code: {response.status_code}"
            }
        
        response_data = response.json()
        results_count = len(response_data.get("data", {}).get("results", []))
        print(f"API returned {results_count} results")
        
        # Cache the response - using main responses directory
        try:
            os.makedirs("../responses", exist_ok=True)
            with open(cache_filename, "w", encoding="utf-8") as f:
                json.dump(response_data, f, indent=4)
        except Exception as e:
            print(f"Error caching response: {e}")
            
        return response_data
        
    except Exception as e:
        return {"error": f"Hotel search API request failed: {e}"}


def call_geoapify_route_matrix(source_coords: List[float], target_coords: List[List[float]], mode: str = "walk") -> dict:
    """
    Calls Geoapify Route Matrix API to calculate distances and travel times.
    
    Args:
        source_coords (List[float]): Source coordinates [longitude, latitude]
        target_coords (List[List[float]]): Target coordinates [[lon, lat], ...]
        mode (str): Travel mode - "walk" or "drive"
        
    Returns:
        dict: Distance matrix results or error dict
    """
    config = API_CONFIG["geoapify"]
    
    if not target_coords:
        return {"data": [], "distance_units": "meters"}
    
    # Validate mode
    if mode not in ("walk", "drive"):
        mode = "walk"
    
    headers = {"Content-Type": "application/json"}
    params = {"apiKey": config["api_key"]}
    
    data = {
        "mode": mode,
        "sources": [{"location": source_coords}],  # [lon, lat]
        "targets": [{"location": coord} for coord in target_coords],  # [[lon, lat], ...]
    }
    
    try:
        response = requests.post(
            config["base_url"],
            headers=headers,
            params=params,
            json=data,
            timeout=config["timeout"]
        )
        
        if response.status_code != 200:
            return {
                "error": f"Failed to retrieve distance data. Status code: {response.status_code}"
            }
        
        response_json = response.json()
        return {
            "data": (response_json.get("sources_to_targets") or [])[0],
            "distance_units": response_json.get("distance_units") or "meters",
        }
        
    except Exception as e:
        return {"error": f"Distance API request failed: {e}"}


# Convenience functions that maintain the original function signatures
def get_coordinates_from_address(address: str, country: str = "", locality: str = "") -> dict:
    """Legacy wrapper for Google Maps geocoding."""
    return call_google_maps_geocoding(address, country, locality)


def search_hotels(location: dict, checkin_date: str, checkout_date: str, filters: str = "") -> dict:
    """Legacy wrapper for RapidAPI hotel search."""
    return call_rapid_api_hotels(location, checkin_date, checkout_date, filters)


def calculate_road_distance_between_coordinates(source_coords: List[float], target_coords: List[List[float]], mode: str = "walk") -> dict:
    """Legacy wrapper for Geoapify route matrix."""
    return call_geoapify_route_matrix(source_coords, target_coords, mode)