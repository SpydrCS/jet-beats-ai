from google.adk.agents import Agent
from tools import hotel_tools
from dotenv import load_dotenv
import os

load_dotenv()

root_agent = Agent(
    name="hotel_information_agent",
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    description="An agent to provide hotel information.",
    instruction="""
        You are an expert travel agent specializing in providing hotel information.
        You provide accurate and concise details on the top 5 options, ranked by distance to final location and price, in a tabular format.
        From the destination provided, induce as much information as possible about the final location (e.g., if the user says he wants to visit Lisbon, and he is going to the Microsoft office, find where the Microsoft office is located in Lisbon and provide hotels near that location).
        If no specific information is provided, assume the user wants hotels near the final destination (usually the client).
        If no specific information is provided, assume a 3-star hotel with breakfast included.
        """,
    tools=hotel_tools,
)

if __name__ == "__main__":
    from vertexai.agent_engines import AdkApp

    app = AdkApp(agent=root_agent)

    async def run_agent():
        async for event in app.async_stream_query(
            message="I am in Porto and I want to go to Lisbon on 09/11/2026, and return on 11/11/2026. I will go to visit the Microsoft office. Provide me the travel information.",
            user_id="user123",
        ):
            # breakpoint()
            try:
                print(event["content"]["parts"][0]["text"], end="\n\n\n")
            except Exception as e:
                print(f"Error processing event: {e}")

    import asyncio

    asyncio.run(run_agent())
