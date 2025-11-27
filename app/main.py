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

from fastapi import FastAPI, UploadFile, File
from config.settings import settings  # 우리가 만든 설정 파일(config/settings.py)을 가져옵니다.
from app.frame_generator import frame_generator

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


@app.post("/generate-frame")
async def generate_frame_endpoint(file: UploadFile = File(...),  prompt: str = ""):
    """
    만화 컷 이미지를 업로드하면 말풍선과 효과음을 제거한 깨끗한 프레임을 생성합니다.
    
    Args:
        file: 업로드할 이미지 파일 (jpg, png 등)
        prompt: 추가 요청사항 (선택)
    
    Returns:
        생성된 프레임 이미지 (base64 인코딩)
    """
    import base64
    
    # 이미지 파일 읽기
    image_data = await file.read()
    
    # AI에게 프레임 생성 요청 (동기 함수)
    result_bytes = frame_generator.generate_frame(image_data, prompt)
    
    # 이미지 바이트를 base64로 인코딩
    result_b64 = base64.b64encode(result_bytes).decode("utf-8")
    
    return {
        "message": "프레임 생성이 완료되었습니다.",
        "status": "200",
        "data": {
            "original_filename": file.filename,
            "generated_image": f"data:image/png;base64,{result_b64}"
        }
    }



# -----------------------------------------------------------------------------
# 실행 방법 (터미널에서 아래 명령어를 입력하세요)
# -----------------------------------------------------------------------------
# uvicorn app.main:app --reload
