import vertexai
from vertexai.preview.prompts import Prompt
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")

# Initialize vertexai
vertexai.init(
    project="durable-utility-477513-h0", location="europe-southwest1", api_key=API_KEY
)

variables = [
    {"animal": "Eagles", "activity": "eat berries"},
    {"animal": "Coyotes", "activity": "jump"},
    {"animal": "Squirrels", "activity": "fly"},
]

# define prompt template
prompt = Prompt(
    prompt_data="Do {animal} {activity}?",
    model_name=os.getenv("GEMINI_MODEL_VERSION", "gemini-2.5-pro"),
    variables=variables,
    system_instruction="You are a helpful zoologist which responds to everything in a single sentence.",
    # generation_config=generation_config, # Optional
    # safety_settings=safety_settings, # Optional
)

# Generates content using the assembled prompt.
responses = []
for variable_set in prompt.variables:
    response = prompt.generate_content(
        contents=prompt.assemble_contents(**variable_set)
    )
    responses.append(response)

for response in responses:
    print(response.text, end="")

# Example response
# Assembled prompt replacing: 1 instances of variable animal, 1 instances of variable activity
# Eagles are primarily carnivorous.  While they might *accidentally* ingest a berry......
