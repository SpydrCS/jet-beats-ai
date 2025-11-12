from .flight_tool import search_oneway_flights, search_roundtrip_flights
from .context_tool import extract_travel_context
from .hotel_tool import get_ranked_hotels_near_client

flight_tools: list = [search_oneway_flights, search_roundtrip_flights]
context_tools: list = [extract_travel_context]
hotel_tools: list = [get_ranked_hotels_near_client]
