import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")


def search_oneway_flights(origin: str, destination: str, date: str) -> dict:
    """Searches for one-way flights from a specific origin to a destination on a given date.

    Uses the Booking.com Flights API via RapidAPI.

    Args:
        origin (str): The IATA code of the departure airport.
        destination (str): The IATA code of the arrival airport.
        date (str): The departure date in YYYY-MM-DD format.

    Returns:
        dict:
        - On success: the JSON response from the API containing flight search results.
        - On failure: a dictionary with an error message.

        Success example:
        {
            "data": {
                "flightOffers": {
                    "segments": [
                        {
                            "totalTime": 3600,
                            "legs": [
                                {
                                    "departureTime": "2025-11-08T10:00:00",
                                    "arrivalTime": "2025-11-08T11:00:00",
                                    "departureAirport": {
                                        "code": "OPO",
                                        "name": "Francisco Sá Carneiro Airport"
                                    },
                                    "arrivalAirport": {
                                        "code": "LIS",
                                        "name": "Lisbon Airport"
                                    },
                                    "cabinClass": "ECONOMY"
                                }
                            ]
                        }
                    ],
                    "priceBreakdown": {
                        "total": {
                            "currencyCode": "USD",
                            "units": 82,
                        }
                    }
                }
            }
        }

        Failure example:
        {
            "error": "Failed to retrieve one-way flight data. Status code: 400"
        }
    """
    # check if file with api response already exists in responses/oneway_{origin}_{destination}_{date}.json
    if os.path.exists(f"responses/oneway_{origin}_{destination}_{date}.json"):
        with open(f"responses/oneway_{origin}_{destination}_{date}.json", "r") as f:
            print("Loading cached one-way flight data from file.")
            return json.load(f)

    print("Cached one-way flight data not found. Making API request...")
    # TODO: API has pagination, so we are only getting the first page of results
    # TODO: Additional parameters for more refined search (e.g., number of passengers, cabin class)
    # TODO: Return more information (e.g., stops, luggage available)
    url = "https://booking-com18.p.rapidapi.com/flights/v2/search-oneway"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com",
    }
    query_string = {
        "departId": origin,
        "arrivalId": destination,
        "departDate": date,
    }
    response = requests.get(url, headers=headers, params=query_string)
    if response.status_code == 200:
        os.makedirs("responses", exist_ok=True)
        with open(f"responses/oneway_{origin}_{destination}_{date}.json", "w") as f:
            json.dump(response.json(), f, indent=4)
        return response.json()
    else:
        try:
            print("Error response:", response.json())
        except Exception:
            print("Error response is not in JSON format.")
        return {
            "error": f"Failed to retrieve one-way flight data. Status code: {response.status_code}",
        }


def search_roundtrip_flights(
    origin: str, destination: str, depart_date: str, return_date: str
) -> dict:
    """Searches for round-trip flights from a specific origin to a destination on given dates.

    Uses the Booking.com Flights API via RapidAPI.

    Args:
        origin (str): The IATA code of the departure airport.
        destination (str): The IATA code of the arrival airport.
        depart_date (str): The departure date in YYYY-MM-DD format.
        return_date (str): The return date in YYYY-MM-DD format.

    Returns:
        dict:
        - On success: the JSON response from the API containing flight search results.
        - On failure: a dictionary with an error message.

        Success example:
        {
            "data": {
                "flightOffers": {
                    "segments": [
                        {
                            "totalTime": 3600,
                            "legs": [
                                {
                                    "departureTime": "2025-11-08T10:00:00",
                                    "arrivalTime": "2025-11-08T11:00:00",
                                    "departureAirport": {
                                        "code": "OPO",
                                        "name": "Francisco Sá Carneiro Airport"
                                    },
                                    "arrivalAirport": {
                                        "code": "LIS",
                                        "name": "Lisbon Airport"
                                    },
                                    "cabinClass": "ECONOMY"
                                }
                            ]
                        },
                        {
                            "totalTime": 3600,
                            "legs": [
                                {
                                    "departureTime": "2025-11-11T20:00:00",
                                    "arrivalTime": "2025-11-11T21:00:00",
                                    "departureAirport": {
                                        "code": "LIS",
                                        "name": "Lisbon Airport"
                                    },
                                    "arrivalAirport": {
                                        "code": "OPO",
                                        "name": "Francisco Sá Carneiro Airport"
                                    },
                                    "cabinClass": "ECONOMY"
                                }
                            ]
                        }
                    ],
                    "priceBreakdown": {
                        "total": {
                            "currencyCode": "USD",
                            "units": 82,
                        }
                    }
                }
            }
        }

        Failure example:
        {
            "error": "Failed to retrieve round-trip flight data. Status code: 400"
        }
    """
    # TODO: API has pagination, so we are only getting the first page of results
    # TODO: Additional parameters for more refined search (e.g., number of passengers, cabin class)
    # TODO: Return more information (e.g., stops, luggage available)
    url = "https://booking-com18.p.rapidapi.com/flights/v2/search-roundtrip"
    headers = {
        "x-rapidapi-key": RAPID_API_KEY,
        "x-rapidapi-host": "booking-com18.p.rapidapi.com",
    }
    query_string = {
        "departId": origin,
        "arrivalId": destination,
        "departDate": depart_date,
        "returnDate": return_date,
    }
    response = requests.get(url, headers=headers, params=query_string)
    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"Failed to retrieve round-trip flight data. Status code: {response.status_code}"
        }


if __name__ == "__main__":
    # # Example usage
    oneway_result = search_oneway_flights("OPO", "LIS", "2026-01-08")
    print("One-way flight search result:")
    print(oneway_result)

    # roundtrip_result = search_roundtrip_flights(
    #     "OPO", "LIS", "2025-11-08", "2025-11-11"
    # )
    # print("Round-trip flight search result:")
    # print(roundtrip_result)
