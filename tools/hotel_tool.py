from typing import List
from models.models_hotels import HotelSearchResultOut, HotelItemOut
from normalizers.booking import normalize_booking_response
from utils.hotel import (
    get_coordinates_from_address,
    search_hotels,
    calculate_road_distance_between_coordinates,
)

__all__ = ["get_hotels_near_destination"]


def get_hotels_near_destination(
    address: str,
    checkin_date: str,
    checkout_date: str,
    country: str = "",
    locality: str = "",
    include_breakfast: bool = True,
    free_cancellation: bool = True,
    transport_mode: str = "walk",  # "walk" | "drive"
    top_k: int = 5,
) -> dict:
    """
    - Geocodifica (Google)
    - Pesquisa hotéis (RapidAPI) **com cache**
    - Normaliza
    - Calcula distância/tempo (Geoapify) **sem cache**
    - Ordena por tempo e preço
    - Devolve JSON (dict) pronto a renderizar
    """
    coords = get_coordinates_from_address(address, country, locality)
    if "error" in coords:
        return {"error": f"geocode_failed: {coords['error']}"}

    filters = []
    if include_breakfast:
        filters.append("mealplan::breakfast_included")
    if free_cancellation:
        filters.append("free_cancellation::1")
    filters_str = ",".join(filters) if filters else ""

    raw = search_hotels(coords, checkin_date, checkout_date, filters_str)
    if "error" in raw:
        return {"error": raw["error"]}

    normalized: HotelSearchResultOut = normalize_booking_response(raw)

    if not normalized.items:
        return normalized.model_dump()  # nothing to enrich, return empty list early

    # distâncias
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
            h.distance_meters = d.get("distance")
            h.travel_time_seconds = d.get("time")
            h.distance_units = units
            h.transport_mode = (
                "walk" if transport_mode not in ("walk", "drive") else transport_mode
            )

    # ordenar por tempo e preço
    def rank_key(x: HotelItemOut):
        t = x.travel_time_seconds if x.travel_time_seconds is not None else 10**12
        p = x.total_price_amount if x.total_price_amount is not None else 10**12
        return (t, p)

    normalized.items.sort(key=rank_key)
    if top_k:
        normalized.items = normalized.items[:top_k]

    return normalized.model_dump()
