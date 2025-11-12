import requests
import os
from dotenv import load_dotenv

load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")


def get_coordinates_from_address(address: str, country: str, locality: str) -> dict:
    """Fetches the coordinates (latitude and longitude) for a given address using the Google Maps API.

    Args:
        address (str): The address to geocode (e.g., "Deloitte Bom Sucesso").
        country (str): The two letter ISO 3166-1 COUNTRY code (e.g., "PT" for Portugal). Use only if certain of the country.
        locality (str): The locality or city (e.g., "Porto"). Use only if certain of the locality.

    Returns:
        dict: A dictionary containing 'location' and 'viewport' keys on success,
              or an 'error' key with a message on failure.
        Success example:
        {
            "location": {
                "latitude": 41.14961,
                "longitude": -8.61099
            },
            "viewport": {
                "northeast": {
                    "latitude": 41.14961,
                    "longitude": -8.61099
                },
                "southwest": {
                    "latitude": 41.14961,
                    "longitude": -8.61099
                }
            }
        }
        Failure example:
        {
            "error": "Failed to retrieve coordinates. Status code: 400"
        }
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    components = []
    if country:
        components.append(f"country:{country}")
    if locality:
        components.append(f"locality:{locality}")
    params = {
        "address": address,
        "components": "|".join(components),
        "key": GOOGLE_MAPS_API_KEY,
    }
    response = requests.get(url, params=params)

    if not response.status_code == 200:
        return {
            "error": f"Failed to retrieve coordinates. Status code: {response.status_code}"
        }

    response_json = response.json()
    if not response_json["status"] == "OK":
        return {"error": "Geocoding API error: " + response_json["status"]}

    geometry = response_json.get("results")[0].get("geometry", {})
    return {
        "location": geometry.get("location"),
        "viewport": geometry.get("viewport"),
    }


def search_hotels(
    location: dict,
    checkin_date: str,
    checkout_date: str,
    filters: str,
) -> dict:
    """Searches for hotels in a specific location (latitude/longitude) for given dates and number of guests.

    Uses the Booking.com Hotels API via RapidAPI.

    Args:
        location (dict): The location dictionary containing the 'viewport' attribute.
        checkin_date (str): The check-in date in YYYY-MM-DD format.
        checkout_date (str): The check-out date in YYYY-MM-DD format.
        filters (str): Filters for the search. Values should be separated by commas. Available filters are:
            - mealplan::breakfast_included for breakfast included
            - free_cancellation::1 for free cancellation

    Returns:
        dict:
        - On success: the JSON response from the API containing hotel search results.
        - On failure: a dictionary with an error message.

        Success example:
        {
            "data": {
                "results": [
                    {
                        "checkinCheckoutPolicy": {
                            "checkinTimeFromInHours": 15,
                            "checkinTimeUntilInHours": 0,
                            "checkoutTimeUntilInHours": 11,
                            "checkoutTimeFromInHours": 0
                        },
                        "basicPropertyData": {
                            "name": "Hotel Example"
                            "latitude": 41.14961,
                            "longitude": -8.61099,
                            "address": "123 Example St, Porto, Portugal",
                            "starRating": {
                                "value": 4,
                                "symbol": "STARS"
                            }
                            "reviews": {
                                "reviewsCount": 5728,
                                "totalScore": 7.3
                            }
                        },
                        "blocks": [
                            {
                                "finalPrice": {
                                    "amount": 150,
                                    "currency": "USD"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        Failure example:
        {
            "error": "Failed to retrieve hotel data. Status code: 400"
        }
    """
    # TODO: API has pagination, so we are only getting the first page of results
    # TODO: Additional parameters for more refined search (e.g., number of guests, min/max price)
    # TODO: Return more information (e.g., checkin/out times)
    url = "https://booking-com18.p.rapidapi.com/stays/search-by-geo"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com",
    }
    params = {
        "neLat": location.get("viewport", {}).get("northeast").get("lat"),
        "neLng": location.get("viewport", {}).get("northeast").get("lng"),
        "swLat": location.get("viewport", {}).get("southwest").get("lat"),
        "swLng": location.get("viewport", {}).get("southwest").get("lng"),
        "checkinDate": checkin_date,
        "checkoutDate": checkout_date,
    }
    if filters:
        params["categoriesFilters"] = filters

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to retrieve hotel data. Status code: {response.status_code}"
        }


def calculate_road_distance_between_coordinates(
    source_coords: list[float], target_coords: list[list[float]]
) -> dict:
    """Calculates the road distance and duration between two sets of coordinates using the Google Maps Distance Matrix API.

    Args:
        source_coords (list[float]): A list containing the latitude and longitude of the origin location [lat, lon].
        target_coords (list[list[float]]): A list of lists, each containing the latitude and longitude of a destination location [lat, lon].

    Returns:
        dict: A dictionary containing distance and duration information on success,
              or an 'error' key with a message on failure.
        Success example:
        {
            "data": [
                {
                    "distance": 26732,
                    "time": 1800,
                    "source_index": 0,
                    "destination_index": 0
                }
            ],
            "distance_units": "meters"
        }
        Failure example:
        {
            "error": "Failed to retrieve distance data. Status code: 400"
        }
    """
    url = "https://api.geoapify.com/v1/routematrix"
    headers = {"Content-Type": "application/json"}
    params = {"apiKey": GEOAPIFY_API_KEY}
    data = {
        "mode": "drive",  # TODO: add more options (?)
        "sources": [{"location": source_coords}],
        "targets": [{"location": coord} for coord in target_coords],
    }
    response = requests.post(url, headers=headers, params=params, json=data)

    if not response.status_code == 200:
        return {
            "error": f"Failed to retrieve distance data. Status code: {response.status_code}"
        }

    try:
        response_json = response.json()
        return {
            "data": response_json.get("sources_to_targets")[0],
            "distance_units": response_json.get("distance_units"),
        }
    except (IndexError, KeyError, TypeError) as e:
        return {"error": f"Error parsing address from response: {str(e)}"}


def enrich_hotels_with_distance(
    hotels_response: dict, client_coord: list[float]
) -> list[dict]:
    """
    Adds driving distance (m) and time (s) from the client location
    to each hotel result using the distance API.

    Args:
        hotels_response (dict): Raw hotel API response (as shown above)
        client_coord (list): [latitude, longitude] of client or meeting location

    Returns:
        list[dict]: List of cleaned hotel entries with distance/time fields added
        Example:
        [
            {
                "checkinCheckoutPolicy": {
                    "checkinTimeFromInHours": 15,
                    "checkoutTimeFromInHours": 0,
                    "checkinTimeUntilInHours": 0,
                    "checkoutTimeUntilInHours": 12
                },
                "basicPropertyData": {
                    "name": "HF Fenix Porto",
                    "starRating": {
                        "symbol": "STARS",
                        "value": 4.0
                    },
                    "location": {
                        "latitude": 41.1547491317966,
                        "longitude": -8.6304547637701,
                        "address": "Rua Gonçalo Sampaio, 282"
                    },
                    "reviews": {
                        "reviewsCount": 2298,
                        "totalScore": 8.8
                    }
                },
                "finalPrice": {
                    "currency": "EUR",
                    "amount": 542.3
                },
                "distance": 62,
                "time_seconds": 14,
                "distance_units": "meters"
            },
            ...
        ]
    """
    results = hotels_response.get("data", {}).get("results", [])
    if not results:
        return []

    # 1️⃣ Extract coordinates for all hotels
    hotel_coords = []
    for hotel in results:
        bp = hotel.get("basicPropertyData", {}).get("location", {})
        lat = bp.get("latitude")
        lon = bp.get("longitude")
        if lat is not None and lon is not None:
            hotel_coords.append([lon, lat])

    # 2️⃣ Call your distance API once for all hotels
    distance_data = calculate_road_distance_between_coordinates(
        source_coords=client_coord, target_coords=hotel_coords
    )

    distances = distance_data.get("data", [])
    units = distance_data.get("distance_units", "meters")

    # 3️⃣ Merge distances back into hotel records
    enriched_hotels = []
    for i, hotel in enumerate(results):
        HOTEL_CHECKIN_CHECKOUT_POLICY_ATTRIBUTES = [
            "checkinTimeFromInHours",
            "checkoutTimeFromInHours",
            "checkinTimeUntilInHours",
            "checkoutTimeUntilInHours",
        ]
        BASIC_PROPERTY_DATA_ATTRIBUTES = ["name", "starRating", "location", "reviews"]
        BASIC_PROPERTY_DATA_LOCATION_ATTRIBUTES = ["latitude", "longitude", "address"]
        BASIC_PROPERTY_DATA_REVIEWS_ATTRIBUTES = ["reviewsCount", "totalScore"]

        checkin_checkout_policy = {
            key: hotel.get("checkinCheckoutPolicy", {}).get(key)
            for key in HOTEL_CHECKIN_CHECKOUT_POLICY_ATTRIBUTES
        }
        basic_property_data = {
            key: hotel.get("basicPropertyData", {}).get(key)
            for key in BASIC_PROPERTY_DATA_ATTRIBUTES
        }
        basic_property_data_location = {
            key: basic_property_data.get("location", {}).get(key)
            for key in BASIC_PROPERTY_DATA_LOCATION_ATTRIBUTES
        }
        basic_property_data_reviews = {
            key: basic_property_data.get("reviews", {}).get(key)
            for key in BASIC_PROPERTY_DATA_REVIEWS_ATTRIBUTES
        }
        final_price = hotel.get("blocks", [{}])[0].get("finalPrice", {})

        hotel_info = {
            "checkinCheckoutPolicy": checkin_checkout_policy,
            "basicPropertyData": {
                **basic_property_data,
                "location": basic_property_data_location,
                "reviews": basic_property_data_reviews,
            },
            "finalPrice": final_price,
        }

        # Add distance info if available
        distance_entry = next((d for d in distances if d["target_index"] == i), None)

        if distance_entry:
            hotel_info["distance"] = distance_entry["distance"]
            hotel_info["distance_units"] = units
            hotel_info["time_seconds"] = distance_entry["time"]

        enriched_hotels.append(hotel_info)

    # 4️⃣ Sort by distance (optional)
    enriched_hotels.sort(key=lambda x: x.get("time_seconds", float("inf")))

    return enriched_hotels


if __name__ == "__main__":
    source = [-8.63016, 41.1550298]
    targets = [
        [-8.6304547637701, 41.1547491317966],
        [-8.63064520061016, 41.1545128465065],
    ]

    distance_info = calculate_road_distance_between_coordinates(source, targets)
    print(distance_info)
