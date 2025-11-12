from google.adk.agents import LlmAgent
from tools import flight_tools
from dotenv import load_dotenv
import os
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

load_dotenv()


class TripTypeEnum(str, Enum):
    one_way = "one-way"
    round_trip = "round-trip"


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
    trip_type: TripTypeEnum = Field(
        description="'one-way' or 'round-trip'.",
    )


root_agent = LlmAgent(
    name="flight_information_agent",
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    description="Provides structured and verified flight information based on structured user requests.",
    instruction="""
        You are an expert virtual travel agent specializing in flight search.

        **Your task:**
        - Choose the correct tool based on the user's intent and the input schema:
            - If `trip_type` is "one-way" OR `return_date` is null → call `search_oneway_flights`.
            - If `trip_type` is "round-trip" AND a `return_date` is provided → call `search_roundtrip_flights`.

        **Guidelines:**
        - Never call both tools in a single request.
        - Always validate that IATA codes and dates are provided before calling a tool.
        - When providing results, order options by balancing price and duration.

        **Response style:**
        - Keep results concise, structured, and easy to compare.
        - Highlight essential info such as airline, price, departure/arrival times, and duration.
        - Avoid speculation — only return verified tool results.
    """,
    tools=flight_tools,
    input_schema=FlightRequest,
)

if __name__ == "__main__":
    from vertexai.agent_engines import AdkApp

    app = AdkApp(agent=root_agent)

    async def run_agent():
        async for event in app.async_stream_query(
            message="I am in Porto and I want to go to Lisbon on 2026-10-10, and return on 2026-10-16. Find me the best flights.",
            user_id="user123",
        ):
            try:
                print(event["content"]["parts"][0]["text"], end="\n\n\n")
            except Exception as e:
                print(f"Error processing event: {e}")

    import asyncio

    asyncio.run(run_agent())
