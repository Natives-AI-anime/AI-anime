# -----------------------------------------------------------------------------
# app/main.py
# -----------------------------------------------------------------------------
# 이 파일은 우리 프로그램의 "대문" 역할을 합니다.
# 서버를 켜면 가장 먼저 이 파일이 실행됩니다.

import sys
import os

# 현재 파일(main.py)의 부모의 부모 폴더(AI-anime)를 파이썬 경로에 추가합니다.
# 이렇게 해야 'config' 폴더를 찾을 수 있습니다.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from config.settings import settings  # 우리가 만든 설정 파일(config/settings.py)을 가져옵니다.

# 1. FastAPI 앱(서버) 만들기
# title과 version은 설정 파일에서 가져온 값을 씁니다.
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# 2. 기본 접속 주소 ("/") 만들기
# 사용자가 인터넷 주소창에 우리 서버 주소(예: http://localhost:8000/)만 치고 들어왔을 때
# 실행될 함수입니다.
@app.get("/")
def read_root():
    """
    메인 페이지 접속 시 보여줄 메시지입니다.
    """
    # 딕셔너리({}) 형태로 데이터를 돌려주면, 브라우저에는 JSON(글자) 형태로 보입니다.
    return {
        "message": "환영합니다! AI Anime Generator 서버입니다.",
        "status": "200",
        "docs_url": "/docs"  # 자동으로 만들어지는 설명서 주소를 알려줍니다.
    }

# -----------------------------------------------------------------------------
# 실행 방법 (터미널에서 아래 명령어를 입력하세요)
# -----------------------------------------------------------------------------
# uvicorn app.main:app --reload
