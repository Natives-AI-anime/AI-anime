import os
from google import genai
from dotenv import load_dotenv

# .env 파일 로드
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", ".env")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: API Key not found!")
else:
    client = genai.Client(api_key=api_key)
    print("Available Models:")
    try:
        # google-genai 라이브러리의 모델 목록 조회
        for m in client.models.list():
            print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
