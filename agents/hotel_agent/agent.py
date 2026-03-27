from dotenv import load_dotenv
import os
from google.adk.agents import LlmAgent
from .models import HotelAgentInput, HotelSearchResultOut
from .tools import hotel_tools

load_dotenv()


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

    **Guidelines:**
    - In case of an error from the tool, respond with:
        {{
            "status": "error",
            "message": "<error_message>"
        }}
    - Your output MUST be **exactly** in the following format (no extra text):
        {HotelSearchResultOut.model_json_schema()}
    """,
    input_schema=HotelAgentInput,
    output_schema=HotelSearchResultOut,
    output_key="structured_hotels_result",
    tools=hotel_tools,
)
