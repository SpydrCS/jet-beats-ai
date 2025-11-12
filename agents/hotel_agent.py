from dotenv import load_dotenv
import os
from typing import Optional, Literal
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from models.models_hotels import HotelSearchResultOut
from tools import hotel_tools

load_dotenv()

class HotelAgentInput(BaseModel):
    final_destination_address: str = Field(description="Address/POI, e.g., 'Microsoft Parque das Nações, Lisboa'.")
    country_code: Optional[str] = Field(default=None, description="ISO-3166-1 alpha-2, e.g., 'PT'.")
    locality: Optional[str] = Field(default=None, description="City/locality, e.g., 'Lisboa'.")
    checkin_date: str = Field(description="YYYY-MM-DD")
    checkout_date: str = Field(description="YYYY-MM-DD")
    include_breakfast: bool = Field(default=True)
    free_cancellation: bool = Field(default=True)
    transport_mode: Literal["walk", "drive"] = Field(default="walk")
    top_k: int = Field(default=5, ge=1, le=20)

root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    name="hotel_information_agent",
    description="Finds hotels near a final destination and returns normalized results with travel time/distance.",
    instruction=f"""
Return ONLY a single JSON object that matches this JSON Schema:
{HotelSearchResultOut.model_json_schema()}

You are provided a structured input (HotelAgentInput). Steps:
1) Geocode 'final_destination_address' (use country_code/locality if present).
2) Search hotels with the dates and filters.
3) Enrich with distance & travel time (transport_mode).
4) Rank by travel time (asc), then total price (asc).
5) Return exactly the HotelSearchResultOut JSON. If a tool errors, return: {{"error": "<message>"}}.
""",
    input_schema=HotelAgentInput,
    output_schema=HotelSearchResultOut,
    output_key="hotels_result",
    tools=hotel_tools,
)

if __name__ == "__main__":
    import asyncio
    from google.genai import types
    import json
    from utils.run import run_agent

    app_name = "hotel_app"

    TEST_INPUT = {
        "final_destination_address": "Microsoft Portugal, Parque das Nações, Lisboa",
        "country_code": "PT",
        "locality": "Lisboa",
        "checkin_date": "2025-12-09",
        "checkout_date": "2025-12-11",
        "include_breakfast": False,
        "free_cancellation": False,
        "transport_mode": "walk",
        "top_k": 20
    }

    user_content = types.Content(role="user", parts=[types.Part(text=json.dumps(TEST_INPUT))])
    asyncio.run(run_agent(app_name, root_agent, user_content))
