from dotenv import load_dotenv
import os
from typing import Optional, Literal
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from .models import HotelSearchResultOut
from .tools import hotel_tools

load_dotenv()



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
    hotel_rating_preference: Optional[str] = Field(default=None, description="Hotel rating preference, e.g., 'budget-friendly'.")
    hotel_extras_preference: Optional[list[str]] = Field(default=None, description="List of hotel extras, e.g., ['Wi-Fi', 'breakfast included'].")
    include_breakfast: bool = Field(default=True)
    free_cancellation: bool = Field(default=True)
    transport_mode: Literal["walk", "drive"] = Field(default="walk")
    top_k: int = Field(default=5, ge=1, le=20)


root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    name="hotel_information_agent",
    description="Finds hotels near a final destination and returns normalized results with travel time/distance.",
    instruction=f"""
    You are provided a structured input in the following format:
    {HotelAgentInput.model_json_schema()}
    
    **Steps:**
    1) Geocode 'final_destination_address' (use country_code/locality if present).
    2) Search hotels with the dates and filters.
    3) Enrich with distance & travel time (transport_mode).
    4) Rank by travel time (asc), then total price (asc).
    5) Return exactly the HotelSearchResultOut JSON. If a tool errors, return: {{"error": "<message>"}}.

    Your output MUST be **exactly** in the following format (no extra text):
    {HotelSearchResultOut.model_json_schema()}
    """,
    input_schema=HotelAgentInput,
    output_schema=HotelSearchResultOut,
    output_key="structured_hotels_result",
    tools=hotel_tools,
)
