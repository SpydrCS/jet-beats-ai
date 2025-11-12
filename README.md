# jetbeats-ai

Nothing beats a Jet2 holiday

## IMPORTANT NOTE

In user query, specifying "tomorrow" or similar will not return the correct date. If we want this feature, we should implement an agent to retrieve the current time.

## API Limits

-   VertexAI: Added €5, should work for 66.6 million tokens
-   Google Maps API: Same €5 added, first 10.000 requests free
-   RAPID API: Free, limited at 530 requests/month.

## Agents

-   Orchestrator/Planner/Main Agent (TODO)
    -   receives user prompt, decides which sub-agents to call and in what order
    -   kind of like the project manager
-   Context Extraction Agent
    -   turn natural language into structured trip info
-   Flight Information Agent
    -   query flight API for information
-   (Public) Transport Agent (TODO)
    -   query (public) transport information
-   Hotel Agent
    -   suggest hotels near client's final location
-   Itinerary Builder Agent (TODO)
    -   combine everything (flights + hotels + transport) into a readable itinerary

### How they communicate

1. User → Planner (prompt)
2. Planner → ContextExtractor
3. ContextExtractor → structured data → Planner
4. Planner calls (these can run in parallel):
    - FlightAgent
    - TransportAgent
    - HotelAgent
5. Planner collects outputs → sends to ItineraryBuilder
6. ItineraryBuilder → final formatted answer → User

### Optional Agents Later

-   Budget Optimizer Agent → suggests cheaper alternatives
-   Calendar Agent → syncs with Outlook/Google Calendar
-   Personalization Agent → learns user travel preferences
-   Summarizer Agent → outputs trip summary in email form

## Useful Links

-   Repository: https://github.com/Deloitte-Portugal/jetbeats-ai
-   Vertex AI Docs: https://docs.cloud.google.com/python/docs/reference/vertexai/latest
-   Vertex AI Pricing: https://cloud.google.com/vertex-ai/generative-ai/pricing#gemini-models-2.0
-   Google ADK Multi-Agent Documentation: https://google.github.io/adk-docs/agents/multi-agents/
-   Similar project: https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/travel_planner_agent
-   FAST API (flights and hotels): https://rapidapi.com/ntd119/api/booking-com18
-   Geoapify Routing (distance and time from client to hotels): https://apidocs.geoapify.com/docs/route-matrix/
-   Google Maps Geocoding: https://developers.google.com/maps/documentation/geocoding/overview

## Steps

1. Create virtual environment and activate it:

```bash
# install virtual environment
python -m venv venv

# activate virtual environment
.\venv\Scripts\activate
```

2. Install required libraries:

```bash
pip install -r requirements.txt
```

3. Run an agent:

_Note_: The code ran will be whatever is in the condition `if__name__ == "__main__"` statement (usually at the end of the file). If you want to run something different (change the prompt, etc.), change it there.

For example, to run the Hotel Agent:

```bash
python -m agents.hotel_agent
```
