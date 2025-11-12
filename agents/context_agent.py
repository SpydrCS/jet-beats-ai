from google.adk.agents import Agent
from tools import context_tools
from dotenv import load_dotenv
import os

load_dotenv()

root_agent = Agent(
    name="context_extraction_agent",
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    description="An agent to extract trip information from user prompts.",
    instruction=""",
        You are a travel context extractor. 
        From a user prompt, extract structured information in the form of JSON.

        Formatting rules:
        - Origin and destination airports should be in IATA code format.
        - Departure and return dates should be in YYYY-MM-DD format.

        Output only valid JSON with these keys:
        - origin_airport (or multiple, if origin city has multiple airports)
        - destination_airport (or multiple, if destination city has multiple airports)
        - departure_date
        - return_date (if round-trip)
        - trip_type ("one-way" or "round-trip")
        - final_destination (as specific as possible, e.g., exact address)
        - hotel_rating_preference (if available, e.g., "5-star")
        - hotel_extras_preference (if available, e.g., "breakfast included", "free cancellation")

        If missing info, infer sensibly or leave as null.""",
    tools=context_tools,
)

if __name__ == "__main__":
    from vertexai.agent_engines import AdkApp
    from vertexai import init

    init(project="us-con-gcp-sbx-0001193-100925", location="europe-west1")

    app = AdkApp(agent=root_agent)

    async def run_agent():
        async for event in app.async_stream_query(
            message="I am in Porto and I want to go to London, to visit the London Eye, on 2026-10-10, and return on 2026-10-16. What are my options?.",
            user_id="user123",
        ):
            try:
                print(event["content"]["parts"][0]["text"], end="\n\n\n")
            except Exception as e:
                print(f"Error processing event: {e}")

    import asyncio

    asyncio.run(run_agent())
