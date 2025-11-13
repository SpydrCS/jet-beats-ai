from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class TravelPromptInput(BaseModel):
    prompt: str = Field(description="Raw user travel request in natural language.")


# TODO: add flight time preference (e.g., morning/evening)
# TODO: add transportation type (e.g., public, walking, taxi, etc.)
# TODO: add loyalty program preferences (e.g., preferred airlines, hotel chains)
class StructuredTravelContext(BaseModel):
    origin_airport: str = Field(
        description="Origin airport(s) IATA code.",
    )
    destination_airport: str = Field(
        description="Destination airport(s) IATA code.",
    )
    departure_date: str = Field(
        description="Departure date(S) in YYYY-MM-DD, separated by commas if multiple.",
    )
    return_date: Optional[str] = Field(
        description="Return date(s) in YYYY-MM-DD, separated by commas if multiple, or null for one-way.",
    )
    trip_type: Literal["one-way", "round-trip"] = Field(
        description="'one-way' or 'round-trip'.",
    )
    final_destination: str = Field(
        description="Specific final destination (address / POI) if inferable, otherwise null.",
    )
    hotel_rating_preference: Optional[str] = Field(
        description="Hotel star rating preference if inferred.",
    )
    hotel_extras_preference: Optional[List[str]] = Field(
        description="List of desired hotel extras (e.g., breakfast included).",
    )
