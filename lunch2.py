import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("API_KEY"))

def get_menu():
    """Returns the list of available lunch items with their prices and types."""
    return [
        {"item": "Veg Thali", "price": 150, "type": "veg"},
        {"item": "Veg Biryani", "price": 120, "type": "veg"},
        {"item": "Idli Sambar", "price": 40, "type": "veg"},
        {"item": "Aloo Paratha", "price": 25, "type": "veg"},
        {"item": "Chicken Roll", "price": 80, "type": "non-veg"}
    ]

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        tools = [get_menu],
        system_instruction=(
            "You are a Smart Lunch Selector."
            "1. Extract the 'budget' and 'preference' (veg/non-veg) from the user's sentence."
            "2. Call the get_menu to find matching items."
            "3. Only list the name and price of successful findings."
            "4. Do not provide conversational filler, reasoning, or greetings."
            "5. If no items match, simply say 'No matching items found.'"
        )
    )
)

print("---Lunch Agent Terminal---")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ['exit', 'quit']:
        print("Exiting Lunch Agent Terminal.")
        break
    response = chat.send_message(user_input)
    print(f"Result: {response.text}")