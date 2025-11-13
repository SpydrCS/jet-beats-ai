from google.adk.agents import LlmAgent
from .tools import flight_tools
from dotenv import load_dotenv
import os
from .models import FlightRequest, FlightToolResponse

load_dotenv()


root_agent = LlmAgent(
    name="flight_information_agent",
    model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    description="Provides structured and verified flight information based on structured user requests.",
    instruction=f"""
        You are an expert virtual travel agent specializing in flight search.

        **Your task:**
        - Receive structured flight requests from users in the following format:
            {FlightRequest.model_json_schema()}
        - Choose the correct tool based on the user's intent and the input schema:
            - If `trip_type` is "one-way" OR `return_date` is null → call `search_oneway_flights`.
            - If `trip_type` is "round-trip" AND a `return_date` is provided → call `search_roundtrip_flights`.

        **Guidelines:**
        - Never call both tools in a single request.
        - Always validate that IATA codes and dates are provided before calling a tool.
        - When providing results, order options by balancing price and duration.

        **Response style:**
        - Keep results concise, structured, and easy to compare.
        - Avoid speculation — only return verified tool results.
        - The final output should be in the following format:
            {FlightToolResponse.model_json_schema()}
    """,
    tools=flight_tools,
    input_schema=FlightRequest,
    output_schema=FlightToolResponse,
    output_key="structured_flight_result",
)

if __name__ == "__main__":
    import asyncio
    from google.genai import types
    import json
    from utils.run import run_agent
    from agents.flight_agent.prompts import INPUT_PROMPT_1

    app_name = "flight_information_app"

    user_content = types.Content(
        role="user", parts=[types.Part(text=json.dumps(INPUT_PROMPT_1))]
    )

    asyncio.run(run_agent(app_name, root_agent, user_content))
    name = ("flight_information_tool_agent",)
