# -----------------------------------------------------------------------------
# app/main.py
# -----------------------------------------------------------------------------
# 이 파일은 우리 프로그램의 "대문" 역할을 합니다.
# 서버를 켜면 가장 먼저 이 파일이 실행됩니다.

import sys
import os

# 상위 경로를 시스템 경로에 추가
# ! 타 폴더 모듈 참조 환경 구축
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import settings
from app.services import VideoService
from pydantic import BaseModel
from typing import List

# 1. FastAPI 앱(서버) 만들기
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS 설정
# ? 개발 시 전면 허용, 운영 시 제한 권장
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 기본 접속 주소 ("/") 만들기
@app.get("/")
def read_root():
    """
    메인 페이지 접속 시 보여줄 메시지입니다.
    """
    return {
        "message": "환영합니다! AI Anime Generator 서버입니다.",
        "status": "200",
        "docs_url": "/docs"
    }

@app.post("/generate-video")
async def generate_video_endpoint(
    start_image: UploadFile = File(...),
    end_image: UploadFile = File(...),
    prompt: str = Form(...),
    project_name: str = Form(...)
):
    """
    비디오 생성 및 Base64 반환 (파일 즉시 삭제)
    Service 계층에 로직 위임
    """
    return await VideoService.generate_video(
        start_image, end_image, prompt, project_name
    )

# --- Revision & Export Endpoints ---

class RegenerateRequest(BaseModel):
    project_name: str
    start_image: str  # Base64
    end_image: str    # Base64
    prompt: str
    revision_prompt: str = "" # Optional specific prompt for revision
    target_frame_count: int

@app.post("/regenerate")
async def regenerate_endpoint(req: RegenerateRequest):
    """
    특정 구간 재생성 엔드포인트
    Service 계층에 로직 위임
    """
    return VideoService.regenerate_segment(
        req.project_name,
        req.start_image,
        req.end_image,
        req.prompt,
        req.revision_prompt,
        req.target_frame_count
    )

class RenderRequest(BaseModel):
    project_name: str
    frames: List[str] # Base64 list
    fps: int = 10

@app.post("/render-video")
async def render_video_endpoint(req: RenderRequest):
    """
    클라이언트가 보낸 프레임(Base64)들을 모아 MP4 비디오로 렌더링 후 Base64 반환.
    Service 계층에 로직 위임
    """
    return VideoService.render_video(
        req.project_name,
        req.frames,
        req.fps
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
