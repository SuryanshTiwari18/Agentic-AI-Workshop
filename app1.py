import os
import time # For the wait timer
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("API_KEY"))

# Using 1.5-flash because it has a more reliable Free Tier quota
MODEL_ID = "gemini-2.5-flash-lite"

# Start the chat session
chat = client.chats.create(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful coding mentor."
    )
)

print(f"--- Mini Gemini Terminal ({MODEL_ID}) ---")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # We wrap the request in a loop to handle the "Retry in X seconds"
    success = False
    while not success:
        try:
            response = chat.send_message(user_input)
            print(f"Gemini: {response.text}\n")
            success = True # Move to the next user input
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                print("⏳ Quota exhausted. Waiting 30 seconds to retry...")
                time.sleep(30) # Wait and the 'while' loop will try again
            else:
                print(f"❌ Error: {e}")
                break # Stop if it's a different error (like 404 or 400)