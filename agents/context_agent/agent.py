from dotenv import load_dotenv
import os
from google.adk.agents import LlmAgent
from .models import TravelPromptInput, StructuredTravelContext
from .prompts import INPUT_PROMPT_1

load_dotenv()


# Exposed agent (name kept as root_agent for consistency with other modules)
root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    name="context_extraction_agent",
    description="Produces structured travel context JSON directly matching the output schema.",
    instruction=f"""
        You receive a JSON object like {{"prompt": "<user natural language travel request>"}}.
        Infer as much structured information as possible.
        Respond ONLY with a JSON matching this schema precisely:
        {StructuredTravelContext.model_json_schema()}
        If a destination has multiple airports, list all IATA codes separated by commas.
        If a field cannot be confidently inferred, set it to null.
        Use 'round-trip' or 'one-way' for trip_type.
        Do not invent impossible data. Keep dates in YYYY-MM-DD.

        Example Query: "{INPUT_PROMPT_1}"
        Example Response: {{
            'origin_airport': 'LIS', 
            'destination_airport': 'CDG,ORY,BVA', 
            'departure_date': '2024-11-20,2024-11-21,2024-11-22', 
            'return_date': '2024-11-24,2024-11-25,2024-11-26', 
            'trip_type': 'round-trip', 
            'final_destination': 'Paris office', 
            'hotel_rating_preference': 'mid-range', 
            'hotel_extras_preference': ['good Wi-Fi', 'breakfast included']
        }}
    """,
    input_schema=TravelPromptInput,
    output_schema=StructuredTravelContext,
    output_key="structured_context_result",
)
