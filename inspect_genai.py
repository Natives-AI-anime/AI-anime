
from google import genai
import os
from dotenv import load_dotenv

load_dotenv("config/.env")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("No API Key")
else:
    client = genai.Client(api_key=api_key)
    print(dir(client))
    if hasattr(client, 'models'):
        print("Client.models methods:", dir(client.models))
