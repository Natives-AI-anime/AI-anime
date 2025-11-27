from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config.settings import settings
import base64
import json
import re

class ImageAnalyzer:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GOOGLE_API_IMAGE_MODEL,
            temperature=0.5  # 분석은 일관성이 중요하므로 온도를 낮춤
        )

    def analyze_scene(self, image_bytes: bytes) -> dict:
        """
        만화 컷을 분석하여 상황, 배경, 분위기를 텍스트로 추출합니다.
        """
        prompt = """
        Analyze this manga panel and provide a structured description in JSON format with the following keys:
        - situation: What is happening in the scene? (e.g., battle, conversation, running)
        - background: Describe the background scenery. (e.g., classroom, forest, city street)
        - mood: What is the emotional atmosphere? (e.g., tense, joyful, gloomy)
        - time: Time of day (e.g., day, night, sunset)
        
        Answer only in JSON format.
        """
        
        try:
            # 이미지 바이트를 base64로 인코딩
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            
            message = HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
            ])
            
            # Vision AI 호출
            response = self.llm.invoke([message])
            content = response.content
            
            # JSON 파싱 시도 (Markdown 코드 블록 제거)
            json_str = re.sub(r'```json|```', '', content).strip()
            return json.loads(json_str)
            
        except Exception as e:
            print(f"이미지 분석 실패: {e}")
            return {
                "situation": "unknown",
                "background": "unknown",
                "mood": "unknown",
                "time": "unknown"
            }

# 인스턴스 생성
image_analyzer = ImageAnalyzer()
