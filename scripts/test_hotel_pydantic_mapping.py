import json
from agents.hotel_agent.utils import normalize_booking_response

# Load the raw response from file
with open(
    "responses/hotels_lat-38_lng--9_lat-38_lng--9_2025-12-09_2025-12-11_nofilters.json",
    "r",
    encoding="utf-8",
) as f:
    raw_response = json.load(f)

# Normalize the response using your normalizer
normalized = normalize_booking_response(raw_response)

# Print raw and normalized for comparison
print("RAW RESPONSE (truncated):")
for i, item in enumerate((raw_response.get("data", {}).get("results", []))):
    print(f"Hotel {i+1}:")
    print(json.dumps(item, indent=2)[:1000])  # Truncate for readability
    print()

print("\nPYDANTIC NORMALIZED OUTPUT:")
print(json.dumps(normalized.model_dump(), indent=2))
