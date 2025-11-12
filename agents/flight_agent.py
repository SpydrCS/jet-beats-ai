from google.adk.agents import Agent
from tools import flight_tools
from dotenv import load_dotenv
import os

load_dotenv()

root_agent = Agent(
    name="flight_information_agent",
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    description="An agent to provide flight information.",
    instruction="""
        You are an expert travel agent specializing in providing one-way and round-trip flight information.
        You provide accurate and concise details on the top 3 options, ranked by price and duration.
        If no specific information is provided, assume it is a round-trip.""",
    tools=flight_tools,
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
