import os
import shutil
import base64
import traceback
from typing import List, Optional, Tuple, Dict, Any
from fastapi import UploadFile
from app.animator import animator

class VideoService:
    @staticmethod
    async def generate_video(
        start_image: UploadFile,
        end_image: UploadFile,
        prompt: str,
        project_name: str
    ) -> Dict[str, Any]:
        """
        비디오 생성 및 Base64 반환 서비스 로직
        """
        try:
            # 1. 이미지 읽기
            start_bytes = await start_image.read()
            end_bytes = await end_image.read()
            
            # Animator 호출 및 프레임 생성
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
            
            # 3. 파일들을 Base64로 읽기
            
            # 3-1. 프레임 이미지 읽기
            for path in frame_paths:
                with open(path, "rb") as img_file:
                    b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                    ext = os.path.splitext(path)[1].lower().replace('.', '')
                    if ext == 'jpg': ext = 'jpeg'
                    frames_b64.append(f"data:image/{ext};base64,{b64_str}")
            
            # 3-2. 비디오 파일 읽기
            if video_path and os.path.exists(video_path):
                with open(video_path, "rb") as vid_file:
                    b64_vid = base64.b64encode(vid_file.read()).decode('utf-8')
                    video_data_b64 = f"data:video/mp4;base64,{b64_vid}"
    
            # 임시 파일 정리 및 용량 확보
            first_frame_dir = os.path.dirname(frame_paths[0])
            if os.path.exists(first_frame_dir):
                shutil.rmtree(first_frame_dir)
                print(f"서버 정리 완료: {first_frame_dir}")
                
            return {
                "status": "success",
                "message": "비디오 생성 및 변환 완료",
                "data": {
                    "project_name": project_name,
                    "frame_count": len(frames_b64),
                    "frames": frames_b64,
                    "video_data": video_data_b64
                }
            }
            
        except Exception as e:
            print(f"Error processing files: {e}")
            return {"status": "error", "message": f"파일 처리 중 오류: {str(e)}"}

    @staticmethod
    def regenerate_segment(
        project_name: str,
        start_image_b64: str,
        end_image_b64: str,
        prompt: str,
        revision_prompt: str,
        target_frame_count: int
    ) -> Dict[str, Any]:
        """
        특정 구간 재생성 서비스 로직
        """
        temp_dir = f"temp_{project_name}_regen"
        try:
            # 1. Base64 디코딩 및 임시 파일 저장
            os.makedirs(temp_dir, exist_ok=True)
            
            start_path = os.path.join(temp_dir, "start.jpg")
            end_path = os.path.join(temp_dir, "end.jpg")
            
            # Remove header if present
            start_data = start_image_b64.split(",")[1] if "," in start_image_b64 else start_image_b64
            end_data = end_image_b64.split(",")[1] if "," in end_image_b64 else end_image_b64

            with open(start_path, "wb") as f:
                f.write(base64.b64decode(start_data))
            with open(end_path, "wb") as f:
                f.write(base64.b64decode(end_data))
                
            # 2. Animator 호출
            new_frames = animator.regenerate_video_segment(
                project_name=project_name,
                start_image_path=start_path,
                end_image_path=end_path,
                target_frame_count=target_frame_count,
                original_prompt=prompt,
                revision_prompt=revision_prompt
            )
            
            if not new_frames:
                if os.path.exists(temp_dir):
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
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    @staticmethod
    def render_video(
        project_name: str,
        frames_b64: List[str],
        fps: int
    ) -> Dict[str, Any]:
        """
        프레임 리스트를 비디오로 렌더링하는 서비스 로직
        """
        temp_dir = f"temp_{project_name}_render"
        try:
            # 1. 임시 디렉토리 생성
            os.makedirs(temp_dir, exist_ok=True)
            
            frame_paths = []
            for i, frame_b64 in enumerate(frames_b64):
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
            output_filename = f"{project_name}_final.webm"
            output_path = os.path.join(temp_dir, output_filename)
            
            result_video_path = animator.create_video_from_frames(
                frame_paths=frame_paths,
                output_path=output_path,
                fps=fps
            )
            
            # 3. 비디오 Base64 변환
            video_b64 = None
            if result_video_path and os.path.exists(result_video_path):
                with open(result_video_path, "rb") as f:
                    video_b64 = "data:video/webm;base64," + base64.b64encode(f.read()).decode('utf-8')
            
            if not video_b64:
                return {"status": "error", "message": "비디오 렌더링 실패"}
                
            return {
                "status": "success",
                "data": {
                    "video_data": video_b64
                }
            }
    
        except Exception as e:
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
