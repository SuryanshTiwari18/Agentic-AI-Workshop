import os
from google import genai
from google.genai.types import (
    FunctionDeclaration,
    Tool,
    GenerateContentConfig,
    Part,
    Content,
)
from dotenv import load_dotenv

# 1. SETUP: Load API Key and Initialize Client
load_dotenv()
API_KEY = os.environ.get("API_KEY")
client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash" 

# --- 2. TOOL IMPLEMENTATION (The Python Logic) ---
# This is our mock database
db_users = [
    {"id": 1, "name": "Suryansh Tiwari", "role": "CS Student", "college": "AKGEC"},
    {"id": 2, "name": "Aditya Singh", "role": "Developer", "college": "KIET"},
    {"id": 3, "name": "Priya Sharma", "role": "Data Analyst", "college": "AKGEC"},
]

def get_users(name: str = None):
    """Retrieves user details from the database. 
    Can filter by name if provided."""
    if name:
        # Case-insensitive search
        results = [u for u in db_users if name.lower() in u['name'].lower()]
        return {"users": results} if results else {"error": "User not found"}
    return {"users": db_users}

# --- 3. TOOL SCHEMA (The Declaration for Gemini) ---
get_users_fn = FunctionDeclaration(
    name="get_users",
    description="Fetch user records from the database. You can search for all users or a specific name.",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string", 
                "description": "Optional: The name of the person to look up."
            },
        },
    },
)

# Bundle the declaration into a Tool object
db_tool = Tool(function_declarations=[get_users_fn])

# --- 4. THE EXECUTION LOOP ---
print(f"--- Database Agent Active ({MODEL_NAME}) ---")
print("Try asking: 'Who are the students from AKGEC?' or 'Is Suryansh in the system?'")

while True:
    prompt = input("\nYou: ")
    if prompt.lower() in ["exit", "quit"]:
        break

    # Step A: Initial call to Gemini to see if it wants to use the tool
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[db_tool],
            system_instruction="You are a professional Database Assistant. Use the 'get_users' tool to answer any questions about people or users."
        ),
    )

    # Step B: Check if Gemini requested a function call
    has_tool_call = False
    model_parts = response.candidates[0].content.parts
    
    for part in model_parts:
        if part.function_call:
            has_tool_call = True
            fn_name = part.function_call.name
            args = part.function_call.args
            
            print(f"  [Agent is querying the database for: {args if args else 'All Users'}]")

            # Execute the local Python logic
            if fn_name == "get_users":
                result = get_users(**args)
            
            # Step C: Send the data BACK to Gemini to generate a natural response
            final_response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    Content(role="user", parts=[Part(text=prompt)]), 
                    Content(role="model", parts=model_parts),
                    Content(role="user", parts=[
                        Part.from_function_response(name=fn_name, response={"result": result})
                    ]),
                ],
                config=GenerateContentConfig(tools=[db_tool]),
            )
            print(f"Gemini: {final_response.text}")
            break
            
    # If the user just said "Hi" and no tool was needed
    if not has_tool_call:
        print(f"Gemini: {response.text}")