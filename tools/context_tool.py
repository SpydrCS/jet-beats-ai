import json
from dotenv import load_dotenv
import os
from google import genai
from google.genai.types import GenerateContentConfig

load_dotenv()
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

client = genai.Client(api_key=GOOGLE_GENAI_API_KEY)


def extract_travel_context(user_prompt: str) -> dict:
    """Extracts structured trip details from a user prompt using Gemini model.
    Fields extracted include origin airport, destination airport, departure date, and return date (if round-trip).

    Args:
        user_prompt (str): The user's travel-related prompt.

    Returns:
        dict:
        - on success: a dictionary containing extracted travel context.
        - on Gemini failure: a dictionary with the original user prompt.
        - on JSON parsing failure: a dictionary with the raw text response from the model.

        Example successful output:
        {
            "origin_airport": "OPO",
            "destination_airport": "LIS",
            "departure_date": "2025-11-08",
            "return_date": "2025-11-11"
        }

        Example Gemini failure output:
        {
            "raw_text": "I want to fly from Oporto to Lisbon tomorrow and return next Monday."
        }

        Example JSON parsing failure output:
        {
            "raw_text": "{
                "origin_airport": "OPO",
                "destination_airport": "LIS",
                "departure_date": "2025-11-08",
                "return_date": "2025-11-11""
        }
    """
    # TODO: extract more fields like flight preference (direct/indirect), class (economy/business), etc.
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
        contents=user_prompt,
        config=GenerateContentConfig(
            system_instruction=[
                """
                You are a travel context extractor. 
                From a user prompt, extract structured information.

                Formatting rules:
                - Origin and destination airports should be in IATA code format.
                - Departure and return dates should be in YYYY-MM-DD format.

                Output only valid JSON with these keys:
                - origin_airport
                - destination_airport
                - departure_date
                - return_date (if round-trip)

                If missing info, infer sensibly or leave as null."""
            ],
        ),
    )

    if not response.text:
        return {"raw_text": user_prompt}

    try:
        return json.loads(response.text.strip("```json"))
    except json.JSONDecodeError as e:
        print(e)
        return {"raw_text": response.text.strip()}


if __name__ == "__main__":
    test_prompt = (
        "I am in Porto and I want to go to Lisbon tomorrow, and return the next Monday."
    )
    context = extract_travel_context(test_prompt)
    print(context)
