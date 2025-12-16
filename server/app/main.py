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
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import settings  # 우리가 만든 설정 파일(config/settings.py)을 가져옵니다.
from app.animator import animator

# 1. FastAPI 앱(서버) 만들기
# title과 version은 설정 파일에서 가져온 값을 씁니다.
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS 설정 (프론트엔드에서 접근 가능하도록 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    # 절대 경로를 웹 URL로 변환
    # 예: C:\work\AI-anime\server\generated_frames\...\frame.jpg -> http://localhost:8000/generated_frames/...\frame.jpg
    frame_urls = []
    for path in frame_paths:
        # generated_frames 이후의 경로만 추출
        if "generated_frames" in path:
            rel_path = path.split("generated_frames")[-1].replace("\\", "/").lstrip("/")
            frame_urls.append(f"http://localhost:8000/generated_frames/{rel_path}")
        else:
            frame_urls.append(path)

    return {
        "status": "success",
        "message": "비디오 생성 완료",
        "data": {
            "project_name": project_name,
            "frame_count": len(frame_paths),
            "frames": frame_urls
        }
    }

from fastapi.staticfiles import StaticFiles
# generated_frames 폴더를 /generated_frames 주소로 연결 (정적 파일 서빙)
# 이미지 데이터를 직접 전송하지 않는 FAST API의 특징이라고 함
# 주의: 이 코드는 app 선언 이후에 위치해야 함
app.mount("/generated_frames", StaticFiles(directory="generated_frames"), name="generated_frames")

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

    # 절대 경로를 웹 URL로 변환
    frame_urls = []
    for path in new_frames:
        if "generated_frames" in path:
            rel_path = path.split("generated_frames")[-1].replace("\\", "/").lstrip("/")
            frame_urls.append(f"http://localhost:8000/generated_frames/{rel_path}")
        else:
            frame_urls.append(path)
        
    return {
        "status": "success",
        "message": "구간 재생성 완료",
        "data": {
            "frames": frame_urls
        }
    }

class ExportRequest(BaseModel):
    project_name: str
    frame_paths: list[str] # 상대 경로 리스트 (generated_frames/...)
    fps: int = 15

@app.post("/export-video")
async def export_video_endpoint(request: ExportRequest):
    """
    현재 프레임 리스트를 비디오로 병합하여 다운로드 URL 반환
    """
    # 1. 경로 절대 경로로 변환
    # 클라이언트에서는 "generated_frames/project/frame.jpg" 형태의 상대 경로를 보냄
    # 서버에서는 이를 절대 경로로 변환해야 함
    
    abs_frame_paths = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # server
    
    for rel_path in request.frame_paths:
        # 혹시 모를 경로 조작 방지
        safe_rel_path = rel_path.replace("..", "").lstrip("/\\")
        full_path = os.path.join(base_dir, safe_rel_path)
        abs_frame_paths.append(full_path)
        
    # 2. 출력 파일 경로 설정
    output_filename = f"{request.project_name}_final_{len(abs_frame_paths)}.mp4"
    # generated_frames 폴더 내 프로젝트 폴더에 저장
    output_dir = os.path.join("generated_frames", request.project_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    # 3. 비디오 생성
    result_path = animator.create_video_from_frames(
        frame_paths=abs_frame_paths,
        output_path=output_path,
        fps=request.fps
    )
    
    if not result_path:
        return {"status": "error", "message": "비디오 생성 실패"}
        
    # 4. URL 변환
    # generated_frames/... -> http://...
    rel_url_path = os.path.relpath(result_path, start="generated_frames").replace("\\", "/")
    video_url = f"http://localhost:8000/generated_frames/{rel_url_path}"
    
    return {
        "status": "success",
        "message": "비디오 내보내기 완료",
        "data": {
            "video_url": video_url
        }
    }

@app.post("/export-frames")
async def export_frames_endpoint(request: ExportRequest):
    """
    현재 프레임 리스트를 ZIP으로 압축하여 다운로드 URL 반환
    """
    abs_frame_paths = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # server
    
    for rel_path in request.frame_paths:
        safe_rel_path = rel_path.replace("..", "").lstrip("/\\")
        full_path = os.path.join(base_dir, safe_rel_path)
        abs_frame_paths.append(full_path)
        
    output_filename = f"{request.project_name}_frames.zip"
    output_dir = os.path.join("generated_frames", request.project_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    
    result_path = animator.create_zip_from_frames(
        frame_paths=abs_frame_paths,
        output_path=output_path
    )
    
    if not result_path:
        return {"status": "error", "message": "ZIP 생성 실패"}
        
    rel_url_path = os.path.relpath(result_path, start="generated_frames").replace("\\", "/")
    zip_url = f"http://localhost:8000/generated_frames/{rel_url_path}"
    
    return {
        "status": "success",
        "message": "프레임 압축 완료",
        "data": {
            "zip_url": zip_url
        }
    }

if __name__ == "__main__":
    # 파이썬 명령어로 직접 실행할 때 (python main.py)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
