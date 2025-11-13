from pydantic import BaseModel, Field
from typing import Optional, Literal


class FlightRequest(BaseModel):
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


class FlightAirport(BaseModel):
    code: str = Field(description="IATA airport code.")
    name: str = Field(description="Full name of the airport.")
    cityName: str = Field(description="City where the airport is located.")
    countryName: str = Field(description="Country where the airport is located.")


class FlightLeg(BaseModel):
    departureTime: str = Field(
        description="Scheduled departure time in ISO 8601 format."
    )
    arrivalTime: str = Field(description="Scheduled arrival time in ISO 8601 format.")
    departureAirport: FlightAirport = Field(description="Departure airport details.")
    arrivalAirport: FlightAirport = Field(description="Arrival airport details.")
    totalTime: int = Field(description="Total duration of the leg in seconds.")
    flightNumber: int = Field(description="Flight number.")
    operatingCarrier: str = Field(description="Operating carrier code.")


class FlightSegment(BaseModel):
    departureAirport: FlightAirport = Field(description="Departure airport details.")
    arrivalAirport: FlightAirport = Field(description="Arrival airport details.")
    departureTime: str = Field(
        description="Scheduled departure time in ISO 8601 format."
    )
    arrivalTime: str = Field(description="Scheduled arrival time in ISO 8601 format.")
    legs: list[FlightLeg] = Field(description="List of flight legs in this segment.")
    totalTime: int = Field(description="Total duration of the segment in seconds.")


class FlightPrice(BaseModel):
    currencyCode: str = Field(description="Currency code (e.g., 'USD').")
    units: float = Field(description="Total price amount.")


class FlightData(BaseModel):
    segments: list[FlightSegment] = Field(description="List of flight segments.")
    totalPrice: FlightPrice = Field(
        description="Total price information with currency code and amount."
    )


class FlightToolResponse(BaseModel):
    status: str = Field(
        description="Status of the request ('success', 'no_results', 'error')."
    )
    data: Optional[list[FlightData]] = Field(
        description="Returned on success. List of available flight options.",
        default=None,
    )
    message: Optional[str] = Field(
        description="Returned on error. Descriptive message.", default=None
    )
