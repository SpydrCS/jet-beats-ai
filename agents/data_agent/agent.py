from flight_agent.agent import root_agent as flight_agent
from hotel_agent.agent import root_agent as hotel_agent
from google.adk.agents import ParallelAgent, LlmAgent, SequentialAgent

parallel_agent = ParallelAgent(
    name="travel_information_agent",
    description="Provides both flight and hotel information based on user requests by leveraging specialized agents.",
    sub_agents=[flight_agent, hotel_agent],
)

merger_agent = LlmAgent(
    name="SynthesisAgent",
    model="gemini-2.5-pro",
    instruction="""
    You are an AI Assistant responsible for combining hotel and flight data into a single comprehensive dataset.

    Your primary task is to join the following datasets. Ensure the final output contains the key points.

    **Crucially: Your entire response MUST be grounded *exclusively* on the information provided in the 'Input Summaries' below. Do NOT add any external knowledge, facts, or details not present in these specific datasets.**

    **Input Summaries:**

    *   **Flight Data:**
        {structured_flight_result}

    *   **Hotel Data:**
        {structured_hotels_result}

    **Output Format:**

    A structured report in JSON format with both flight and hotel information aggregated.

    Do not include introductory or concluding phrases outside this structure, and strictly adhere to using only the provided input content.
    """,
    description="Combines datasets from parallel agents into a structured, combined dataset, strictly grounded on provided inputs.",
)

sequential_pipeline_agent = SequentialAgent(
    name="PipelineTravelAgent",
    # Run parallel research first, then merge
    sub_agents=[parallel_agent, merger_agent],
    description="Coordinates parallel research and combines the results.",
)

root_agent = sequential_pipeline_agent
