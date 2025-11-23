from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config.settings import settings  # 우리가 만든 설정 파일 사용

class AnimeRecommender:
    def __init__(self):
        # 1. 생성자: 필요한 도구들을 준비합니다.
        self.llm = ChatGoogleGenerativeAI(google_api_key=settings.GOOGLE_API_KEY, model=settings.GOOGLE_API_MODEL, temperature=0.7)
        self.prompt = PromptTemplate.from_template("""
            너는 {genre} 장르의 애니메이션 전문가야.
            사용자가 "{user_input}"라고 물어봤어.
            이에 맞는 애니메이션을 추천해줘.
            """)
        self.chain = self.prompt | self.llm
    
    # 2. 메서드: 실제 기능을 수행합니다. (비동기 지원(api 호출 시간 동안 다른 일을 할 수 있음))
    async def recommend(self, genre: str, user_input: str):
        return await self.chain.ainvoke({
            "genre": genre,
            "user_input": user_input
        })

# 3. 인스턴스 생성 (싱글톤 디자인 패턴)
anime_recommender = AnimeRecommender()