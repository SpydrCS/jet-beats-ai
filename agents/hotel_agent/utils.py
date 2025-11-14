from typing import Dict, Any, List
from .models import HotelItemOut, HotelSearchResultOut
from .api_calls import (
    get_coordinates_from_address,
    search_hotels,
    calculate_road_distance_between_coordinates
)


def normalize_booking_response(raw: Dict[str, Any]) -> HotelSearchResultOut:
    """
    Converte o payload da RapidAPI Booking num formato estável (HotelItemOut),
    sem calcular distâncias (isso é feito no tool).
    """
    results = (((raw or {}).get("data") or {}).get("results")) or []
    items: List[HotelItemOut] = []
    
    print(f"normalize_booking_response: Processing {len(results)} raw results")

    for i, r in enumerate(results):
        bp = r.get("basicPropertyData") or {}
        loc = bp.get("location") or {}
        reviews = bp.get("reviews") or {}
        stars = bp.get("starRating") or {}

        # preço total da estadia: preferir priceDisplayInfo.amountPerStay; fallback blocks[0].finalPrice
        price_info = (
            ((r.get("priceDisplayInfo") or {}).get("displayPrice") or {}).get(
                "amountPerStay"
            )
        ) or {}
        amount = price_info.get("amountUnformatted")
        currency = price_info.get("currency")
        if amount is None:
            blocks = r.get("blocks") or []
            if blocks:
                fp = (blocks[0] or {}).get("finalPrice") or {}
                amount = fp.get("amount")
                currency = fp.get("currency")

        # Check for valid coordinates before creating the hotel item
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        
        # Skip hotels without valid coordinates (None or 0.0, 0.0)
        if (lat is None or lng is None or (lat == 0.0 and lng == 0.0)):
            print(f"  Hotel {i+1}: {bp.get('name', 'Unnamed')} - SKIPPED (no valid coordinates: lat={lat}, lng={lng})")
            continue

        item = HotelItemOut(
            name=bp.get("name")
            or (r.get("displayName") or {}).get("text")
            or "Unnamed",
            latitude=lat,
            longitude=lng,
            address=loc.get("address"),
            stars=stars.get("value"),
            review_score=reviews.get("totalScore"),
            review_count=reviews.get("reviewsCount"),
            total_price_amount=amount,
            total_price_currency=(currency or "EUR").upper() if currency else None,
            provider_hotel_id=str(bp.get("id")) if bp.get("id") is not None else None,
            deep_link=None,
        )

        items.append(item)
        print(f"  Hotel {i+1}: {item.name} at ({item.latitude}, {item.longitude}) - ADDED")

    print(f"normalize_booking_response: Returning {len(items)} valid items out of {len(results)} raw results")
    return HotelSearchResultOut(items=items, total_results=len(results))


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

    HOTEL_CHECKIN_CHECKOUT_POLICY_ATTRIBUTES = [
        "checkinTimeFromInHours",
        "checkoutTimeFromInHours",
        "checkinTimeUntilInHours",
        "checkoutTimeUntilInHours",
    ]
    BASIC_PROPERTY_DATA_ATTRIBUTES = ["name", "starRating", "location", "reviews"]
    BASIC_PROPERTY_DATA_LOCATION_ATTRIBUTES = ["latitude", "longitude", "address"]
    BASIC_PROPERTY_DATA_REVIEWS_ATTRIBUTES = ["reviewsCount", "totalScore"]

    # 3️⃣ Merge distances back into hotel records
    enriched_hotels = []
    for i, hotel in enumerate(results):

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
