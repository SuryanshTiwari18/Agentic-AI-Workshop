import os
from google import genai
from google.genai import types
from dotenv import load_dotenv  

load_dotenv()

# 1. Initialize the client (No more genai.configure)
client = genai.Client(api_key=os.environ.get("API_KEY"))

# 2. Generate content using client.models
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a short poem about the sunrise.",
    config=types.GenerateContentConfig(
        max_output_tokens=1500,
        temperature=0.7
    )
)

print("Response:", response.text)