import json
import requests
from dotenv import load_dotenv
import os
from .flight import format_flight_response
from .models import FlightToolResponse

load_dotenv()
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

# TODO: add option for multiple airports, and multiple dates


def search_oneway_flights(
    origin: str, destination: str, date: str
) -> FlightToolResponse:
    """
    Searches for one-way flights from a specific origin to a destination on a given date.
    Uses the Booking.com Flights API via RapidAPI.

    Args:
        origin (str): The IATA code of the departure airport (e.g., "OPO").
        destination (str): The IATA code of the arrival airport (e.g., "LIS").
        date (str): The departure date in YYYY-MM-DD format (e.g., "2026-01-20").

    Returns:
        dict[str, Any]: JSON-like dictionary containing flight information in the following format:

        Success response example:
        {
            "status": "success",
            "data": [
                {
                    "segments": [
                        {
                            "departureAirport": {
                                "code": "OPO",
                                "name": "Francisco Sa Carneiro Airport",
                                "cityName": "Porto",
                                "countryName": "Portugal"
                            },
                            "arrivalAirport": {
                                "code": "LIS",
                                "name": "Humberto Delgado Airport",
                                "cityName": "Lisbon",
                                "countryName": "Portugal"
                            },
                            "departureTime": "2026-01-08T11:15:00",
                            "arrivalTime": "2026-01-08T12:15:00",
                            "legs": [
                                {
                                    "departureTime": "2026-01-08T11:15:00",
                                    "arrivalTime": "2026-01-08T12:15:00",
                                    "departureAirport": {
                                        "code": "OPO",
                                        "name": "Francisco Sa Carneiro Airport",
                                        "cityName": "Porto",
                                        "countryName": "Portugal"
                                    },
                                    "arrivalAirport": {
                                        "code": "LIS",
                                        "name": "Humberto Delgado Airport",
                                        "cityName": "Lisbon",
                                        "countryName": "Portugal"
                                    },
                                    "totalTime": 3600,
                                    "flightNumber": 1925,
                                    "operatingCarrier": "TP"
                                }
                            ],
                            "totalTime": 3600
                        }
                    ],
                    "totalPrice": {
                        "currencyCode": "USD",
                        "units": 49
                    }
                },
                ...
            ]
        }

        Failure formatting response example:
        {
            "status": "error",
            "message": "Failed to retrieve one-way flight data. Status code: 400"
        }

        Failure API response example:
        {
            "error": "Failed to retrieve one-way flight data. Status code: 400",
        }

    Notes:
    - Expects valid IATA codes and an ISO-formatted date.
    """
    # check if file with api response already exists in responses/oneway_{origin}_{destination}_{date}.json
    file_path = f"../responses/oneway_{origin}_{destination}_{date}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            print("Loading cached one-way flight data from file.")
            return json.load(f)

    print("Cached one-way flight data not found. Making API request...")
    # TODO: API has pagination, so we are only getting the first page of results
    # TODO: Additional parameters for more refined search (e.g., number of passengers, cabin class)
    # TODO: Return more information (e.g., stops, luggage available, available extra products)
    # TODO: Return aggregated information (e.g., cheapest flight, fastest flight, min price per airline, etc.)
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
        os.makedirs("../responses", exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(response.json(), f, indent=4)
        return format_flight_response(response.json())
    else:
        try:
            message = "Error response:", response.json()
        except Exception:
            message = "Error response is not in JSON format."
        return FlightToolResponse(
            status="error",
            message=f"Failed to retrieve one-way flight data. Status code: {response.status_code}. {message}",
        )


def search_roundtrip_flights(
    origin: str, destination: str, depart_date: str, return_date: str
) -> FlightToolResponse:
    """
    Searches for round-trip flights between two airports for specified departure and return dates.
    Uses the Booking.com Flights API via RapidAPI.

    Args:
        origin (str): The IATA code of the departure airport (e.g., "OPO").
        destination (str): The IATA code of the arrival airport (e.g., "LIS").
        depart_date (str): The departure date in YYYY-MM-DD format (e.g., "2026-01-20").
        return_date (str): The return date in YYYY-MM-DD format (e.g., "2026-01-27").

    Returns:
        dict[str, Any]: JSON-like dictionary containing flight information in the following format:

        Success response example:
        {
            "status": "success",
            "data": [
                {
                    "segments": [
                        {
                            "departureAirport": {
                                "code": "OPO",
                                "name": "Francisco Sa Carneiro Airport",
                                "cityName": "Porto",
                                "countryName": "Portugal"
                            },
                            "arrivalAirport": {
                                "code": "LIS",
                                "name": "Humberto Delgado Airport",
                                "cityName": "Lisbon",
                                "countryName": "Portugal"
                            },
                            "departureTime": "2026-01-08T11:15:00",
                            "arrivalTime": "2026-01-08T12:15:00",
                            "legs": [
                                {
                                    "departureTime": "2026-01-08T11:15:00",
                                    "arrivalTime": "2026-01-08T12:15:00",
                                    "departureAirport": {
                                        "code": "OPO",
                                        "name": "Francisco Sa Carneiro Airport",
                                        "cityName": "Porto",
                                        "countryName": "Portugal"
                                    },
                                    "arrivalAirport": {
                                        "code": "LIS",
                                        "name": "Humberto Delgado Airport",
                                        "cityName": "Lisbon",
                                        "countryName": "Portugal"
                                    },
                                    "totalTime": 3600,
                                    "flightNumber": 1925,
                                    "operatingCarrier": "TP"
                                }
                            ],
                            "totalTime": 3600
                        }
                    ],
                    "totalPrice": {
                        "currencyCode": "USD",
                        "units": 49
                    }
                },
                ...
            ]
        }

        Failure formatting response example:
        {
            "status": "error",
            "message": "Failed to retrieve one-way flight data. Status code: 400"
        }

        Failure API response example:
        {
            "error": "Failed to retrieve one-way flight data. Status code: 400",
        }

    Notes:
    - Expects valid IATA codes and an ISO-formatted date.
    """
    # check if file with api response already exists in responses/roundtrip_{origin}_{destination}_{depart_date}_{return_date}.json
    file_path = f"../responses/roundtrip_{origin}_{destination}_{depart_date}_{return_date}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            print("Loading cached round-trip flight data from file.")
            return json.load(f)

    print("Cached round-trip flight data not found. Making API request...")
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
        os.makedirs("../responses", exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(response.json(), f, indent=4)
        return format_flight_response(response.json())
    else:
        try:
            message = "Error response:", response.json()
        except Exception:
            message = "Error response is not in JSON format."
        return FlightToolResponse(
            status="error",
            message=f"Failed to retrieve round-trip flight data. Status code: {response.status_code}. {message}",
        )


flight_tools: list = [search_oneway_flights, search_roundtrip_flights]

if __name__ == "__main__":
    # # Example usage
    # oneway_result = search_oneway_flights("OPO", "LIS", "2026-01-08")
    # print("One-way flight search result:")
    # print(oneway_result)

    roundtrip_result = search_roundtrip_flights(
        "OPO", "LIS", "2026-01-08", "2026-01-10"
    )
    print("Round-trip flight search result:")
    print(roundtrip_result)
