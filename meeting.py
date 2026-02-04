import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

schedule_meeting_tool = {
    "name": "schedule_meeting",
    "description": "Schedule a meeting with specified attendees at a given time and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of people attending the meeting.",
            },
            "date": {
                "type": "string",
                "description": "Date of the meeting (e.g., '2024-07-01').",
            },
            "time": {
                "type": "string",
                "description": "Time of the meeting (e.g., '14:00').",
            },
            "topic": {
                "type": "string",
                "description": "The subject or topic of the meeting.",
            },
        },
        "required": ["attendees", "date", "time", "topic"],
    },
}

client = genai.Client(api_key=os.environ.get("API_KEY"))
tools = types.Tool(function_declarations=[schedule_meeting_tool])
config = types.GenerateContentConfig(tools=[tools])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Schedule a meeting with Alice and Bob on 2024-07-01 at 14:00 about Project Kickoff.",
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print("Function Call Detected:")
    print(f"Function Name: {function_call.name}")
    print(f"Arguments: {function_call.args}")
    
else:
    print("No function call detected in the response.")
    print(response.text)
