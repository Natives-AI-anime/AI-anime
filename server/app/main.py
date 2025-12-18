# -----------------------------------------------------------------------------
# app/main.py
# -----------------------------------------------------------------------------
# 이 파일은 우리 프로그램의 "대문" 역할을 합니다.
# 서버를 켜면 가장 먼저 이 파일이 실행됩니다.

import sys
import os
import base64
import shutil

# 상위 경로를 시스템 경로에 추가
# ! 타 폴더 모듈 참조 환경 구축
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config.settings import settings  # 우리가 만든 설정 파일(config/settings.py)을 가져옵니다.
from app.animator import animator
from app.animator import animator
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

# 1. FastAPI 앱(서버) 만들기
# title과 version은 설정 파일에서 가져온 값을 씁니다.
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
    비디오 생성 및 Base64 반환 (파일 즉시 삭제)
    """
    
    # 1. 이미지 읽기
    start_bytes = await start_image.read()
    end_bytes = await end_image.read()
    
    # Animator 호출 및 프레임 생성
    # ! 생성 소요 시간 고려 필요
    result = animator.generate_video_from_images(
        project_name=project_name,
        start_image_bytes=start_bytes,
        end_image_bytes=end_bytes,
        prompt=prompt
    )
    
    if not result:
        return {"status": "error", "message": "비디오 생성 실패"}
        
    frame_paths, video_path = result

    video_data_b64 = None
    frames_b64 = []
    
    try:
        # 3. 파일들을 Base64로 읽기
        
        # 3-1. 프레임 이미지 읽기
        for path in frame_paths:
            with open(path, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                ext = os.path.splitext(path)[1].lower().replace('.', '')
                if ext == 'jpg': ext = 'jpeg'
                frames_b64.append(f"data:image/{ext};base64,{b64_str}")
        
        # 3-2. 비디오 파일 읽기 (Original from API)
        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as vid_file:
                b64_vid = base64.b64encode(vid_file.read()).decode('utf-8')
                video_data_b64 = f"data:video/mp4;base64,{b64_vid}"

        # 임시 파일 정리 및 용량 확보
        # ! 특정 프로젝트 하위 폴더만 삭제
        first_frame_dir = os.path.dirname(frame_paths[0])
        if os.path.exists(first_frame_dir):
            shutil.rmtree(first_frame_dir)
            print(f"서버 정리 완료: {first_frame_dir}")
            
    except Exception as e:
        print(f"Error processing files: {e}")
        return {"status": "error", "message": f"파일 처리 중 오류: {str(e)}"}

    return {
        "status": "success",
        "message": "비디오 생성 및 변환 완료",
        "data": {
            "project_name": project_name,
            "frame_count": len(frames_b64),
            "frames": frames_b64,     # Base64 Strings
            "video_data": video_data_b64 # Base64 String (Original API Video)
        }
    }

# 정적 파일 서빙 설정 (혹시 모를 상황 대비해 남겨둠, 하지만 이제 쓰이지 않음)
frames_dir = "generated_frames"
os.makedirs(frames_dir, exist_ok=True)
app.mount("/generated_frames", StaticFiles(directory=frames_dir), name="generated_frames")


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
    Base64 이미지를 받아 임시 파일로 저장 후 Animator 호출, 결과 프레임을 Base64로 반환.
    """
    try:
        # 1. Base64 디코딩 및 임시 파일 저장
        temp_dir = f"temp_{req.project_name}_regen"
        os.makedirs(temp_dir, exist_ok=True)
        
        start_path = os.path.join(temp_dir, "start.jpg")
        end_path = os.path.join(temp_dir, "end.jpg")
        
        with open(start_path, "wb") as f:
            f.write(base64.b64decode(req.start_image.split(",")[1]))
        with open(end_path, "wb") as f:
            f.write(base64.b64decode(req.end_image.split(",")[1]))
            
        # 2. Animator 호출
        new_frames = animator.regenerate_video_segment(
            project_name=req.project_name,
            start_image_path=start_path,
            end_image_path=end_path,
            target_frame_count=req.target_frame_count,
            original_prompt=req.prompt,
            revision_prompt=req.revision_prompt
        )
        
        if not new_frames:
            shutil.rmtree(temp_dir)
            return {"status": "error", "message": "재생성 실패"}
            
        # 3. 결과 Base64 변환
        frames_b64 = []
        for path in new_frames:
            with open(path, "rb") as img_file:
                b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                ext = os.path.splitext(path)[1].lower().replace('.', '')
                if ext == 'jpg': ext = 'jpeg'
                frames_b64.append(f"data:image/{ext};base64,{b64_str}")
        
        # 4. Cleanup
        # temp_dir (inputs) and generated frame dir (outputs scope)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # new_frames의 부모 디렉토리도 삭제 (generated_frames/...)
        if new_frames:
            first_frame_dir = os.path.dirname(new_frames[0])
            if os.path.exists(first_frame_dir) and "generated_frames" in first_frame_dir:
                shutil.rmtree(first_frame_dir)

        return {
            "status": "success",
            "data": {
                "frames": frames_b64
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

class RenderRequest(BaseModel):
    project_name: str
    frames: List[str] # Base64 list
    fps: int = 10

@app.post("/render-video")
async def render_video_endpoint(req: RenderRequest):
    """
    클라이언트가 보낸 프레임(Base64)들을 모아 MP4 비디오로 렌더링 후 Base64 반환.
    """
    try:
        # 1. 임시 디렉토리 생성
        temp_dir = f"temp_{req.project_name}_render"
        os.makedirs(temp_dir, exist_ok=True)
        
        frame_paths = []
        for i, frame_b64 in enumerate(req.frames):
            file_path = os.path.join(temp_dir, f"frame_{i:05d}.jpg")
            # header 제거 (data:image/jpeg;base64,...)
            if "," in frame_b64:
                b64_data = frame_b64.split(",")[1]
            else:
                b64_data = frame_b64
            
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(b64_data))
            frame_paths.append(file_path)
            
        # 2. 비디오 생성 (OpenCV via Animator)
        # 브라우저 호환성을 위해 WebM(VP8) 형식 사용
        output_filename = f"{req.project_name}_final.webm"
        output_path = os.path.join(temp_dir, output_filename)
        
        result_video_path = animator.create_video_from_frames(
            frame_paths=frame_paths,
            output_path=output_path,
            fps=req.fps
        )
        
        # 3. 비디오 Base64 변환
        video_b64 = None
        if result_video_path and os.path.exists(result_video_path):
            with open(result_video_path, "rb") as f:
                video_b64 = "data:video/webm;base64," + base64.b64encode(f.read()).decode('utf-8')
        
        # 렌더링 임시 디렉토리 정리
        # ? 비동기 처리 검토 가능
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        if not video_b64:
            return {"status": "error", "message": "비디오 렌더링 실패"}
            
        return {
            "status": "success",
            "data": {
                "video_data": video_b64
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
