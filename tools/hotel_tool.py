from utils.hotel import (
    enrich_hotels_with_distance,
    get_coordinates_from_address,
    search_hotels,
)


def get_ranked_hotels_near_client(
    address: str,
    checkin_date: str,
    checkout_date: str,
    country: str = "",
    locality: str = "",
    filters: str = "",
) -> list[dict]:
    """
    Searches for hotels near a given address and orders them by distance (in time) from the address.

    Args:
        address (str): The address to geocode (e.g., "Deloitte Bom Sucesso").
        checkin_date (str): The check-in date in YYYY-MM-DD format.
        checkout_date (str): The check-out date in YYYY-MM-DD format.
        country (str, optional): The two letter ISO 3166-1 COUNTRY code (e.g., "PT" for Portugal). Use only if certain of the country.
        locality (str, optional): The locality or city (e.g., "Porto"). Use only if certain of the locality.
        filters (str, Optional): Filters for the search. Values should be separated by commas. Available filters are:
            - mealplan::breakfast_included for breakfast included
            - free_cancellation::1 for free cancellation

    Returns:
        list[dict]: a list of hotel data dictionaries.

        Success example:
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
    coords = get_coordinates_from_address(address, country, locality)
    hotel_data = search_hotels(coords, checkin_date, checkout_date, filters)

    return enrich_hotels_with_distance(
        hotel_data, [coords["location"]["lng"], coords["location"]["lat"]]
    )


if __name__ == "__main__":
    enriched_hotel_data = get_ranked_hotels_near_client(
        address="Deloitte Bom Sucesso, Porto",
        checkin_date="2026-07-01",
        checkout_date="2026-07-05",
        country="PT",
        locality="Porto",
        filters="mealplan::breakfast_included,free_cancellation::1",
    )
    print(enriched_hotel_data)
