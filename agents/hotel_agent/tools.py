from typing import List
from .models import (
    HotelSearchResultOut,
    HotelItemOut,
    HotelToolResponse,
)
from .utils import (
    normalize_booking_response,
    get_coordinates_from_address,
    search_hotels,
    calculate_road_distance_between_coordinates,
)

__all__ = ["get_hotels_near_destination"]


from typing import Optional

def get_hotels_near_destination(
    final_destination: str,
    departure_date: str,
    return_date: str,
    country_code: str = "",
    locality: str = "",
    hotel_rating_preference: Optional[str] = None,
    hotel_extras_preference: Optional[list] = None,
    include_breakfast: bool = True,
    free_cancellation: bool = True,
    transport_mode: str = "walk",  # "walk" | "drive"
    top_k: int = 5,
) -> HotelToolResponse:
    """Search, normalize, enrich and rank hotels near a destination.

    This tool orchestrates three providers:
      1) Google Geocoding (address -> point + viewport)
      2) Booking.com (RapidAPI) hotel search (cached on disk)
      3) Geoapify Route Matrix (distance/time enrichment; no cache)

    Args:
        address (str): Destination address or POI (e.g., "Microsoft Parque das Nações, Lisboa").
        checkin_date (str): Check-in date in YYYY-MM-DD format.
        checkout_date (str): Check-out date in YYYY-MM-DD format.
        country (str, optional): ISO-3166-1 alpha-2 country code (e.g., "PT").
        locality (str, optional): City/locality hint (e.g., "Lisboa").
        include_breakfast (bool): If True, include breakfast filter.
        free_cancellation (bool): If True, include free cancellation filter.
        transport_mode (str): "walk" or "drive" used for distance matrix.
        top_k (int): Max number of hotels returned after ranking.

    Returns:
        HotelToolResponse: Pydantic model with status, items and total_results.

        Success example:
            {
              "status": "success",
              "items": [
                {
                  "name": "HF Fenix Porto",
                  "latitude": 41.1547,
                  "longitude": -8.63045,
                  "address": "Rua Exemplo 123",
                  "stars": 4.0,
                  "review_score": 8.8,
                  "review_count": 2298,
                  "total_price_amount": 542.3,
                  "total_price_currency": "EUR",
                  "distance_meters": 1200,
                  "travel_time_seconds": 900,
                  "distance_units": "meters",
                  "transport_mode": "walk",
                  "provider": "booking_com",
                  "provider_hotel_id": "123456",
                  "deep_link": null
                },
                ...
              ],
              "total_results": 42
            }

        Failure example:
            {
              "status": "error",
              "message": "geocode_failed: Geocoding API error: ZERO_RESULTS",
              "items": [],
              "total_results": 0
            }

    Notes:
      - Hotel search is cached under `responses/` by bounding box and dates.
      - Distance matrix is not cached; time/distance fields may be None for unreachable targets.
      - Ranking prioritizes lowest travel time, then lowest total price.
    """
    print("Hotel tool called with:", {
        "final_destination": final_destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "country_code": country_code,
        "locality": locality,
        "hotel_rating_preference": hotel_rating_preference,
        "hotel_extras_preference": hotel_extras_preference,
        "include_breakfast": include_breakfast,
        "free_cancellation": free_cancellation,
        "transport_mode": transport_mode,
        "top_k": top_k
    })
    
    coords = get_coordinates_from_address(final_destination, country_code, locality)
    print(f"Geocoding result: {coords}")
    if "error" in coords:
        return HotelToolResponse(
            status="error",
            message=f"geocode_failed: {coords['error']}",
            total_results=0,
        )

    filters: List[str] = []
    if include_breakfast:
        filters.append("mealplan::breakfast_included")
    if free_cancellation:
        filters.append("free_cancellation::1")
    filters_str = ",".join(filters) if filters else ""

    raw = search_hotels(coords, departure_date, return_date, filters_str)
    if "error" in raw:
        return HotelToolResponse(status="error", message=raw["error"], total_results=0)

    print(f"Raw hotel search returned {len(raw.get('data', {}).get('results', []))} raw results")
    
    normalized: HotelSearchResultOut = normalize_booking_response(raw)
    print(f"After normalization: {len(normalized.items)} items, total_results: {normalized.total_results}")
    
    if not normalized.items:
        print("No items after normalization - returning empty result")
        return HotelToolResponse(
            status="success", items=[], total_results=normalized.total_results
        )

    # Distances enrichment
    client_xy = [coords["location"]["lng"], coords["location"]["lat"]]
    targets: List[List[float]] = [[h.longitude, h.latitude] for h in normalized.items]
    dist_resp = calculate_road_distance_between_coordinates(
        client_xy, targets, mode=transport_mode
    )
    distances = (dist_resp or {}).get("data") or []
    units = (dist_resp or {}).get("distance_units") or "meters"
    dist_by_idx = {d.get("target_index"): d for d in distances}

    for i, h in enumerate(normalized.items):
        d = dist_by_idx.get(i)
        if d:
            h.distance_meters = d.get("distance") or d.get("distance_meters")
            h.travel_time_seconds = d.get("time") or d.get("travel_time_seconds")
            h.distance_units = units
            h.transport_mode = (
                "walk" if transport_mode not in ("walk", "drive") else transport_mode
            )

    # Order by travel time then price
    def rank_key(x: HotelItemOut):
        t = x.travel_time_seconds if x.travel_time_seconds is not None else 10**12
        p = x.total_price_amount if x.total_price_amount is not None else 10**12
        return (t, p)

    normalized.items.sort(key=rank_key)
    if top_k:
        normalized.items = normalized.items[:top_k]

    return HotelToolResponse(
        status="success", items=normalized.items, total_results=normalized.total_results
    )


hotel_tools: list = [get_hotels_near_destination]
