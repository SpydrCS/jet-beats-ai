from .flight_tool import search_oneway_flights, search_roundtrip_flights
from .hotel_tool import get_hotels_near_destination

flight_tools: list = [search_oneway_flights, search_roundtrip_flights]
hotel_tools: list = [get_hotels_near_destination]
