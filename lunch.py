import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("API_KEY"))

def get_menu():
    """Returns the list of lunch items with their prices and types."""
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
        system_instruction = (
            "You are a Smart Lunch Selector."
            "STRICT RUELES: "
            "1. Only show the name and price items that strictly fit the budget and preference."
            "2. Do not explain your reasoning or provide conversational filler."
            "3. If nothing is found, just say 'No matching items found.' "
            "4. Be extremely concise."
        )
    )
)

print("---Lunch Agent Terminal---")
while True:
    try:
        budget = input("\nEnter your budget (or type 'quit'): ")
        if(budget.lower() == 'quit'):
            print("Exiting Lunch Agent Terminal.")
            break
        pref = input("Enter your preference (veg/non-veg): ")

        prompt = f"Budget: {budget}, Preference: {pref}. Find items."

        print("\nSearching...")
        response = chat.send_message(prompt)

        print(f"Result: \n{response.text}")
    except Exception as e:
        print(f"Error: {e}")