
from google import genai
import os
from dotenv import load_dotenv

load_dotenv("config/.env")
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

# GenerateContentConfig가 지원하는 파라미터 확인
from google.genai import types
print("GenerateContentConfig 필드:")
print(types.GenerateContentConfig.model_fields.keys())
