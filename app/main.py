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

from fastapi import FastAPI, UploadFile, File, Form
from config.settings import settings  # 우리가 만든 설정 파일(config/settings.py)을 가져옵니다.
from app.animator import animator

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
    result_bytes = animator.generate_frame(image_data, prompt)
    
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



@app.post("/generate-video")
async def generate_video_endpoint(
    start_image: UploadFile = File(...),
    end_image: UploadFile = File(...),
    prompt: str = Form(...),
    project_name: str = Form(...)
):
    """
    비디오 생성 엔드포인트
    
    Args:
        start_image: 시작 프레임 이미지
        end_image: 끝 프레임 이미지
        prompt: 비디오 생성 프롬프트
        project_name: 프로젝트 이름
    """
    import shutil
    
    # 1. 이미지 읽기
    start_bytes = await start_image.read()
    end_bytes = await end_image.read()
    
    # 2. Animator 호출
    # 결과는 생성된 프레임 파일들의 경로 리스트
    frame_paths = animator.generate_video_from_images(
        project_name=project_name,
        start_image_bytes=start_bytes,
        end_image_bytes=end_bytes,
        prompt=prompt
    )
    
    if not frame_paths:
        return {"status": "error", "message": "비디오 생성 실패"}
        
    # 3. 결과 반환
    # 실제 서비스에서는 이미지 URL을 반환해야 하지만, 여기서는 로컬 파일 경로 반환
    return {
        "status": "success",
        "message": "비디오 생성 완료",
        "data": {
            "project_name": project_name,
            "frame_count": len(frame_paths),
            "frames": frame_paths
        }
    }

from pydantic import BaseModel

class RevisionRequest(BaseModel):
    project_name: str
    start_image_path: str
    end_image_path: str
    target_frame_count: int
    prompt: str

@app.post("/regenerate-segment")
async def regenerate_segment_endpoint(request: RevisionRequest):
    """
    특정 구간 재생성 (Revision) 엔드포인트
    """
    new_frames = animator.regenerate_video_segment(
        project_name=request.project_name,
        start_image_path=request.start_image_path,
        end_image_path=request.end_image_path,
        target_frame_count=request.target_frame_count,
        original_prompt=request.prompt
    )
    
    if new_frames is None:
        return {"status": "error", "message": "구간 재생성 실패"}
        
    return {
        "status": "success",
        "message": "구간 재생성 완료",
        "data": {
            "frames": new_frames
        }
    }

