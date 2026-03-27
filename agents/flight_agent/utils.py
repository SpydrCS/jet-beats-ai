import json
from .models import FlightToolResponse


def format_flight_response(data: dict) -> FlightToolResponse:
    """
    Formats the flight search API response into a more readable structure.

    Args:
        data (dict): The raw JSON response from the flight search API.

    Returns:
        dict: A formatted dictionary containing flight segments and pricing information.

        Example success response: {"status": "success", "data": [...]}
        Example failure response: {"status": "error", "message": "..."}
    """
    FLIGHT_SEGMENTS_ATTRIBUTES = [
        "departureAirport",
        "arrivalAirport",
        "departureTime",
        "arrivalTime",
        "legs",
        "totalTime",
    ]
    FLIGHT_AIRPORT_ATTRIBUTES = ["code", "name", "cityName", "countryName"]
    FLIGHT_SEGMENTS_LEG_ATTRIBUTES = [
        "departureTime",
        "arrivalTime",
        "departureAirport",
        "arrivalAirport",
        "totalTime",
    ]
    print(data)

    try:
        formatted_flights = []
        for offer in data.get("data", {}).get("flightOffers", []):
            flight_info = {}
            for segment in offer.get("segments", []):
                segment_info = {
                    key: segment.get(key) for key in FLIGHT_SEGMENTS_ATTRIBUTES
                }
                segment_departure_airport_info = {
                    key: segment.get("departureAirport", {}).get(key)
                    for key in FLIGHT_AIRPORT_ATTRIBUTES
                }
                segment_arrival_airport_info = {
                    key: segment.get("arrivalAirport", {}).get(key)
                    for key in FLIGHT_AIRPORT_ATTRIBUTES
                }

                segment_legs = []
                for leg in segment.get("legs", []):
                    segment_leg_info = {
                        key: leg.get(key) for key in FLIGHT_SEGMENTS_LEG_ATTRIBUTES
                    }
                    segment_leg_departure_airport_info = {
                        key: leg.get("departureAirport", {}).get(key)
                        for key in FLIGHT_AIRPORT_ATTRIBUTES
                    }
                    segment_leg_arrival_airport_info = {
                        key: leg.get("arrivalAirport", {}).get(key)
                        for key in FLIGHT_AIRPORT_ATTRIBUTES
                    }
                    segment_legs.append(
                        {
                            **segment_leg_info,
                            "departureAirport": segment_leg_departure_airport_info,
                            "arrivalAirport": segment_leg_arrival_airport_info,
                            "flightNumber": leg.get("flightInfo", {}).get(
                                "flightNumber"
                            ),
                            "operatingCarrier": leg.get("flightInfo", {})
                            .get("carrierInfo", {})
                            .get("operatingCarrier"),
                        }
                    )

                flight_info.setdefault("segments", []).append(
                    {
                        **segment_info,
                        "departureAirport": segment_departure_airport_info,
                        "arrivalAirport": segment_arrival_airport_info,
                        "legs": segment_legs,
                    }
                )

            formatted_flights.append(
                {
                    **flight_info,
                    "totalPrice": {
                        "currencyCode": offer.get("priceBreakdown", {})
                        .get("total", {})
                        .get("currencyCode"),
                        "units": offer.get("priceBreakdown", {})
                        .get("total", {})
                        .get("units"),
                    },
                }
            )

        return FlightToolResponse(status="success", data=formatted_flights)
    except Exception as e:
        print("Error formatting flight response:", e)
        return FlightToolResponse(status="error", message=str(e))


if __name__ == "__main__":
    # Example usage
    origin = "OPO"
    destination = "LIS"
    date = "2026-01-08"

    with open(f"responses/oneway_{origin}_{destination}_{date}.json", "r") as f:
        print("Loading cached one-way flight data from file.")
        data = json.load(f)

    result = format_flight_response(data)
    print("Formatted flight response:")
    print(result)
