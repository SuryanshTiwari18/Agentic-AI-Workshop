import os
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("API_KEY"))

def get_weather(city: str):
    """
    Fetch real-time weather details for a specific city using OpenWeatherMap.
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"The current temperature in {city} is {temp}°C with {desc}."
        else:
            return f"Could not retrieve weather data for {city}. Reason: {data.get('message', 'Unknown error')}."
    except Exception as e:
        return f"An error occurred while fetching weather data: {str(e)}"
    
chat = client.chats.create(
    model="gemini-2.5-flash",
    config = types.GenerateContentConfig(
        tools=[get_weather],
        system_instruction="You are a helpful Weather Agent. Use the get_weather tool for any weather queries."
    )                           
)

print("---Real-Time Weather Agent Active---")
while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit", "bye"]: break

    response = chat.send_message(user_input)
    print(f"Weather Agent: {response.text}")