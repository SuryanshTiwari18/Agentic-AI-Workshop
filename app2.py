import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load your credentials
load_dotenv()
client = genai.Client(api_key=os.environ.get("API_KEY"))

# 2. Define the Logic Function
# The docstring is critical—it tells Gemini what the tool does!
def calculator(a: float, b: float, operation: str) -> float:
    """
    Perform basic math operations.
    Args:
        a: The first number.
        b: The second number.
        operation: The operation to perform ('add', 'sub', 'mul', 'div').
    """
    if operation == 'add': return a + b
    if operation == 'sub': return a - b
    if operation == 'mul': return a * b
    if operation == 'div': return a / b if b != 0 else "Error: Division by zero"
    return "Invalid operation"

# 3. Define the Tool Object (Manual Declaration)
calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="A tool for basic arithmetic: add, sub, mul, div.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "a": {"type": "NUMBER"},
            "b": {"type": "NUMBER"},
            "operation": {"type": "STRING", "enum": ["add", "sub", "mul", "div"]}
        },
        "required": ["a", "b", "operation"]
    }
)

calculator_tool = types.Tool(function_declarations=[calculator_declaration])

# 4. Start the Chat Session
# Pass the function directly in the tools list to enable Automatic Function Calling
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        tools=[calculator], # <--- Pass the function here for 'automatic' mode
        system_instruction="You are a helpful mentor. Use the calculator tool for math.",
        max_output_tokens=500
    )
)

print("--- Gemini Agent Active (with Calculator) ---")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]: break

    try:
        # Gemini will automatically call 'calculator' if it needs to!
        response = chat.send_message(user_input)
        print(f"Gemini: {response.text}\n")
        
    except Exception as e:
        if "429" in str(e):
            print("⏳ Limit reached. Waiting 30s...")
            time.sleep(30)
        else:
            print(f"❌ Error: {e}")