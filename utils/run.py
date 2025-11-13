import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.agents import LlmAgent


async def run_agent(app_name: str, root_agent: LlmAgent, user_content: types.Content):
    """
    Run the structured agent and prints JSON output.
    Executes a single prompt through a `Runner` with an in-memory session and prints both the raw final
    response and the parsed JSON stored under the agent's output_key.
    """
    user_id = "demo_user"
    session_id = "inline_demo"
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    runner = Runner(
        agent=root_agent, app_name=app_name, session_service=session_service
    )

    final_text = "(no final response)"
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=user_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text

    print(f"\nAgent name: {root_agent.name}")
    print("Raw final response:\n", final_text)

    session = await session_service.get_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    if not session:
        print("Error: session not found!")
        return

    output_key = root_agent.output_key

    if not output_key:
        print("Error: agent has no output_key defined!")
        return

    stored = session.state.get(output_key)

    if not stored:
        print("(no stored output found)")
        return

    print(f"\nStored session state key '{output_key}':")

    try:
        print(json.dumps(json.loads(stored), indent=2))
    except Exception:
        print(stored)
