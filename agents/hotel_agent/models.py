"""Hotel domain models.

This module contains the normalized hotel item model returned from the Booking
API and simple container response schemas used by the hotel tool.

Responsibility split:
    - Network calls & provider JSON parsing live outside (normalizers + tools).
    - These classes are pure data contracts (no side effects).

Extend carefully: prefer adding optional fields rather than renaming existing
ones to keep backward compatibility with agents depending on the schema.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


# Updated to match context agent/flight agent field names
class HotelAgentInput(BaseModel):
    final_destination: str = Field(
        description="Address/POI, e.g., 'Microsoft Parque das Nações, Lisboa'."
    )
    country_code: Optional[str] = Field(
        default=None, description="ISO-3166-1 alpha-2, e.g., 'PT'."
    )
    locality: Optional[str] = Field(
        default=None, description="City/locality, e.g., 'Lisboa'."
    )
    departure_date: str = Field(description="YYYY-MM-DD")
    return_date: str = Field(description="YYYY-MM-DD")
    hotel_rating_preference: Optional[str] = Field(
        default=None, description="Hotel rating preference, e.g., 'budget-friendly'."
    )
    hotel_extras_preference: Optional[list[str]] = Field(
        default=None,
        description="List of hotel extras, e.g., ['Wi-Fi', 'breakfast included'].",
    )
    include_breakfast: bool = Field(default=True)
    free_cancellation: bool = Field(default=True)
    transport_mode: Literal["walk", "drive"] = Field(default="walk")
    top_k: int = Field(default=5, ge=1, le=20)


class HotelItemOut(BaseModel):
    name: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    stars: Optional[float] = None
    review_score: Optional[float] = None
    review_count: Optional[int] = None
    total_price_amount: Optional[float] = None
    total_price_currency: Optional[str] = None

    # distância/tempo até ao destino final (Geoapify)
    distance_meters: Optional[int] = None
    travel_time_seconds: Optional[int] = None
    distance_units: Literal["meters"] = "meters"
    transport_mode: Literal["walk", "drive"] = "drive"

    provider: Literal["booking_com"] = "booking_com"
    provider_hotel_id: Optional[str] = None
    deep_link: Optional[str] = None


class HotelSearchResultOut(BaseModel):
    """Stable normalized list of hotels (success only).

    total_results is the raw count returned by the provider before any top-k
    pruning or enrichment reordering.
    """

    items: List[HotelItemOut]
    total_results: int = Field(0, description="Raw provider total before top-k.")


class HotelToolResponse(BaseModel):
    """Unified tool response wrapper.

    status: "success" when items are present (possibly empty list) and
    message is None. When an error occurs upstream (geocoding, search, distance
    API), status becomes "error" and message contains a concise explanation.
    """

    status: Literal["success", "error"]
    items: List[HotelItemOut] = Field(
        default_factory=list, description="Normalized, possibly enriched hotel items."
    )
    total_results: int = Field(
        0, description="Raw provider total even on error (0 if unknown)."
    )
    message: Optional[str] = Field(
        default=None, description="Human-readable error summary when status='error'."
    )


__all__ = [
    "HotelItemOut",
    "HotelSearchResultOut",
    "HotelToolResponse",
]
