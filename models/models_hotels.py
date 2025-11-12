# models/models_hotels.py
from pydantic import BaseModel, Field
from typing import Optional, List, Literal

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
    items: List[HotelItemOut]
    total_results: int = Field(0, description="Total bruto devolvido pela API (antes de top-k).")
