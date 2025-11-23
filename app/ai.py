from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config.settings import settings
from openai import OpenAI

class AnimeRecommender:
    # 1. 생성자: 필요한 도구들을 준비합니다.
    def __init__(self):
        self.text_llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY, 
            model=settings.GOOGLE_API_TEXT_MODEL, 
            temperature=0.7
        )
        self.prompt = "Remove all speech bubbles, text, sound effects, and onomatopoeia from this manga panel. Fill the removed areas naturally with the surrounding background and art style. Keep all characters and scenery intact. This will be used as a clean animation frame, so make it look professional and seamless without any text or effects."
        
        # OpenAI 클라이언트
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # 2. 메서드: 만화 컷에서 깨끗한 프레임 생성
    def generate_frame(self, image_bytes: bytes, additional_prompt: str = ""):
        """
        원본 만화 컷 이미지에서 말풍선을 제거합니다.
        
        Args:
            image_bytes: 원본 만화 컷 이미지 (바이트)
            additional_prompt: 추가 지시사항 (선택)
        
        Returns:
            생성된 이미지 바이트 데이터 (16:9 비율, 1024x576)
        """
        import io
        from PIL import Image, ImageDraw
        import requests
        
        # 추가 프롬프트가 있으면 결합
        final_prompt = f"{self.prompt}. {additional_prompt}" if additional_prompt else self.prompt
        
        # 이미지 바이트를 PIL Image로 변환
        original_image = Image.open(io.BytesIO(image_bytes))
        
        # RGBA 모드로 변환
        if original_image.mode != 'RGBA':
            original_image = original_image.convert('RGBA')
        
        # 1024x1024로 리사이즈
        square_size = 1024
        original_image = original_image.resize((square_size, square_size), Image.Resampling.LANCZOS)
        
        # 마스크 생성 - 중앙 영역을 투명하게 (편집할 영역)
        mask = Image.new('L', (square_size, square_size), 0)  # 검은색 배경
        draw = ImageDraw.Draw(mask)
        # 중앙 80% 영역을 흰색으로 (편집 대상)
        margin = int(square_size * 0.1)
        draw.rectangle([margin, margin, square_size - margin, square_size - margin], fill=255)
        
        # PNG로 변환
        image_buffer = io.BytesIO()
        original_image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        
        mask_buffer = io.BytesIO()
        mask_image = Image.new('RGBA', (square_size, square_size), (0, 0, 0, 0))
        mask_image.putalpha(mask)
        mask_image.save(mask_buffer, format='PNG')
        mask_buffer.seek(0)
        
        try:
            # OpenAI 이미지 편집 API 호출
            response = self.openai_client.images.edit(
                image=image_buffer,
                mask=mask_buffer,
                prompt=final_prompt,
                n=1,
                size="1024x1024"
            )
            
            # 생성된 이미지 URL에서 다운로드
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            generated_image = Image.open(io.BytesIO(image_response.content))
            
            # 16:9 비율로 크롭
            target_height = int(1024 / (16/9))  # 576
            top = (1024 - target_height) // 2
            generated_image = generated_image.crop((0, top, 1024, top + target_height))
            
            # 최종 이미지를 바이트로 변환
            output_buffer = io.BytesIO()
            generated_image.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            print(f"OpenAI API 에러: {e}")
            # 에러 발생 시 원본 이미지를 16:9로 크롭해서 반환
            target_height = int(1024 / (16/9))
            top = (1024 - target_height) // 2
            cropped = original_image.crop((0, top, 1024, top + target_height))
            
            output_buffer = io.BytesIO()
            cropped.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            
            return output_buffer.getvalue()


# 인스턴스 생성 (싱글톤 디자인 패턴)
anime_recommender = AnimeRecommender()