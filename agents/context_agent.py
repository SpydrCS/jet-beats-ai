from prompts.input.context_agent import INPUT_PROMPT_1
from dotenv import load_dotenv
import os
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from google.adk.agents import LlmAgent

load_dotenv()


class TravelPromptInput(BaseModel):
    prompt: str = Field(description="Raw user travel request in natural language.")


class TripTypeEnum(str, Enum):
    one_way = "one-way"
    round_trip = "round-trip"


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
    trip_type: TripTypeEnum = Field(
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
            'trip_type': <TripTypeEnum.round_trip: 'round-trip'>, 
            'final_destination': 'Paris office', 
            'hotel_rating_preference': 'mid-range', 
            'hotel_extras_preference': ['good Wi-Fi', 'breakfast included']
        }}
    """,
    input_schema=TravelPromptInput,
    output_schema=StructuredTravelContext,
    output_key="structured_context_result",
)


if __name__ == "__main__":

    import asyncio
    from google.genai import types
    import json
    from utils.run import run_agent

    app_name = "travel_context_app"
    TEST_INPUT = {"prompt": INPUT_PROMPT_1}

    user_content = types.Content(
        role="user", parts=[types.Part(text=json.dumps(TEST_INPUT))]
    )

    asyncio.run(run_agent(app_name, root_agent, user_content))
    name = ("travel_context_tool_agent",)
