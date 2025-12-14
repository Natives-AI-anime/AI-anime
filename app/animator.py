"""
Animator Module - Kling AI를 사용한 애니메이션 생성
"""
import os
import time
import requests
import base64
from typing import Optional
from PIL import Image
import io
import cv2
from typing import List

from app.frame_generator import extract_frames_from_url

from config.settings import settings


class Animator:
    """
    Kling AI를 사용하여 두 이미지 사이의 애니메이션을 생성하는 클래스
    """
    
    def __init__(self):
        """Kling AI 클라이언트 초기화"""
        self.access_key = settings.KLING_ACCESS_KEY
        self.secret_key = settings.KLING_SECRET_KEY
        self.base_url = "https://api-singapore.klingai.com/v1/videos/image2video"
        
    def _generate_jwt_token(self) -> str:
        """
        Access Key와 Secret Key로 JWT 토큰 생성 (Header에 kid 추가)
        """
        import jwt
        import time
    
        if not self.access_key or not self.secret_key:
            print("❌ Error: KLING_ACCESS_KEY or KLING_SECRET_KEY is missing!")
            return ""

        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800, 
            "nbf": int(time.time()) - 5 
        }
        
        # 디버깅: 키 확인 (일부만 출력)
        print(f"DEBUG: AK={self.access_key[:5]}... SK={self.secret_key[:5]}...")
        
        token = jwt.encode(payload, self.secret_key.strip(), algorithm="HS256", headers=headers)
        
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        return token
        
    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """이미지를 base64로 인코딩"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def generate_video_from_images(
        self, 
        project_name: str,
        start_image_bytes: bytes, 
        end_image_bytes: bytes,
        prompt: str,
        duration: int = 5
    ) -> Optional[List[str]]:
        """
        두 이미지를 시작과 끝 프레임으로 사용하여 비디오 생성
        
        Args:
            start_image_bytes: 시작 프레임 이미지 (bytes)
            end_image_bytes: 끝 프레임 이미지 (bytes)
            prompt: 비디오 생성 프롬프트
            duration: 비디오 길이 (초, 5 또는 10)
            
        Returns:
            생성된 프레임 파일 경로 리스트 또는 None
        """
        try:
            print("Kling AI API 호출 중...")
            
            # 이미지를 base64로 인코딩
            start_b64 = self._encode_image_to_base64(start_image_bytes)
            end_b64 = self._encode_image_to_base64(end_image_bytes)
            
            # API 요청 헤더
            token = self._generate_jwt_token()
            print("token 값:")
            print(token)
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # API 요청 페이로드
            # 참고: 실제 Kling AI API 스펙에 맞게 조정 필요
            payload = {
                "model_name": "kling-v1",  # 또는 "kling-v1-pro"
                "prompt": """
                Create a smooth anime-style animation transitioning from the first frame to the second frame.
                """+prompt,
                "image": start_b64,  # 시작 프레임
                "image_tail": end_b64,  # 끝 프레임 (필드명은 API 문서 확인 필요)
                "duration": str(duration),
                "aspect_ratio": "16:9",
                "mode": "pro"  # 또는 "standard"
            }
            
            # API 호출
            print("데이터 업로드 및 작업 요청 중... (이미지 크기에 따라 1~2분 소요될 수 있습니다)")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=120  # 2분 타임아웃
            )
            
            # response.raise_for_status() 라인 위에 삽입
            if response.status_code == 400:
                print(">>> 400 Bad Request 서버 응답 상세:")
                print(response.text) # <--- 이 코드를 통해 정확한 오류 메시지를 확인해야 합니다.
                return None
            
            response.raise_for_status()
            result = response.json()

            print(result)
            
            # 작업 ID 가져오기
            task_id = result.get("data", {}).get("task_id")
            if not task_id:
                print(f"작업 ID를 가져올 수 없습니다: {result}")
                return None
            
            print(f"작업 시작됨: {task_id}")
            print("비디오 생성 대기 중... (수 분 소요될 수 있습니다)")
            
            # 작업 완료 대기 (폴링)
            max_attempts = 180  # 최대 30분 대기
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(10)
                attempt += 1
                
                # 작업 상태 확인
                status_response = requests.get(
                    f"{self.base_url}/{task_id}",
                    headers=headers,
                    timeout=10
                )
                
                status_response.raise_for_status()
                status_result = status_response.json()
                
                task_status = status_result.get("data", {}).get("task_status")
                
                # 디버깅: 상태 출력 (매번 출력하여 확인)
                print(f" [Status: {task_status}] ", end="", flush=True)

                if task_status == "succeed" or task_status == "completed": 
                    print("\n비디오 생성 완료!")
                   
                    # 비디오 URL 가져오기
                    data = status_result.get("data", {})
                    
                    # 1. task_result 구조 확인 (새로운 응답 형식)
                    video_url = None
                    task_result = data.get("task_result", {})
                    # 디버깅: task_result 타입 확인
                    print(f"DEBUG: task_result type: {type(task_result)}")
                    print(f"DEBUG: task_result content: {task_result}")
                    
                    if task_result and "videos" in task_result:
                        videos = task_result.get("videos")
                        print(f"DEBUG: videos: {videos}")
                        
                        if videos and len(videos) > 0:
                            video_url = videos[0].get("url")
                            print(f"DEBUG: Extracted URL: {video_url}")
                            
                    # 2. 기존 구조 확인 (fallback)
                    if not video_url:
                        print("DEBUG: trying fallback...")
                        video_url = data.get("video_url")
                        
                    if not video_url and "video_result_list" in data:
                        video_list = data.get("video_result_list")
                        if video_list and len(video_list) > 0:
                            video_url = video_list[0].get("url")
                    
                    print(f"Video URL: {video_url}")

                    if not video_url:
                        print("비디오 URL을 가져올 수 없습니다. 응답을 확인하세요.")
                        print(f"DEBUG Response: {status_result}")
                        return None
                    
                    # 1. 비디오 파일 다운로드 (스트리밍 안정성 확보)
                    print(f"비디오 다운로드 중... ({video_url})")
                    try:
                        temp_video_path = f"temp_{task_id}.mp4"
                        video_response = requests.get(video_url, stream=True, timeout=60)
                        video_response.raise_for_status()
                        
                        with open(temp_video_path, 'wb') as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                        print(f"다운로드 완료: {temp_video_path}")
                        
                        # 2. 로컬 파일에서 프레임 추출
                        print("프레임 추출 중...")
                        output_dir = os.path.join("generated_frames", project_name, task_id)
                        frames = extract_frames_from_url(temp_video_path, output_dir)
                        
                        # 3. 임시 파일 삭제
                        if os.path.exists(temp_video_path):
                            os.remove(temp_video_path)
                            
                        return frames
                        
                    except Exception as e:
                        print(f"비디오 다운로드 및 추출 실패: {e}")
                        return None
                    
                elif task_status == "failed":
                    print("\n비디오 생성 실패")
                    error_msg = status_result.get("data", {}).get("error")
                    print(f"오류: {error_msg}")
                    return None
                else:
                    print(".", end="", flush=True)
            
            print("\n타임아웃: 비디오 생성이 너무 오래 걸립니다")
            return None

        except Exception as e:
            print(f"Video generation error: {e}")
            import traceback
            traceback.print_exc()
            return None



    def regenerate_video_segment(
        self,
        project_name: str,
        start_image_path: str,
        end_image_path: str,
        target_frame_count: int,
        original_prompt: str = ""
    ) -> Optional[List[str]]:
        """
        특정 구간의 영상을 재생성하고, 필요한 프레임 수만큼 샘플링하여 반환
        
        Args:
            project_name: 프로젝트 이름
            start_image_path: 시작 프레임 이미지 경로
            end_image_path: 끝 프레임 이미지 경로
            target_frame_count: 필요한 목표 프레임 수
            original_prompt: 원본 프롬프트
            
        Returns:
            샘플링된 프레임 파일 경로 리스트
        """
        try:
            # 1. 이미지 로드
            with open(start_image_path, "rb") as f:
                start_bytes = f.read()
            with open(end_image_path, "rb") as f:
                end_bytes = f.read()
                
            # 2. 프롬프트 수정 (Slow Motion 적용)
            # 5초 영상을 짧은 구간에 넣을 것이므로, 가능한 느리고 부드럽게 움직이도록 유도
            modified_prompt = f"{original_prompt}, extremely slow motion, high detail, smooth transition, detailed interpolation"
            print(f"재생성 프롬프트: {modified_prompt}")
            
            # 3. 비디오 생성 (전체 프레임 추출)
            revision_project_name = f"{project_name}_revision"
            
            all_frames = self.generate_video_from_images(
                project_name=revision_project_name,
                start_image_bytes=start_bytes,
                end_image_bytes=end_bytes,
                prompt=modified_prompt,
                duration=5 # 최소 5초
            )
            
            if not all_frames:
                print("재생성 실패: 프레임을 생성하지 못했습니다.")
                return None
                
            total_frames = len(all_frames)
            print(f"생성된 총 프레임 수: {total_frames} -> 목표 프레임 수: {target_frame_count}")
            
            if target_frame_count <= 0:
                print("목표 프레임 수가 0 이하입니다.")
                return []
                
            if target_frame_count == 1:
                return [all_frames[total_frames // 2]]
            
            # 4. 프레임 샘플링 (Linear Interpolation)
            sampled_frames = []
            if total_frames <= target_frame_count:
                # 생성된 프레임이 목표보다 적으면 그대로 반환
                sampled_frames = all_frames
            else:
                # 정확한 간격으로 샘플링
                indices = [int(i * (total_frames - 1) / (target_frame_count - 1)) for i in range(target_frame_count)]
                for idx in indices:
                    sampled_frames.append(all_frames[idx])
            
            print(f"샘플링 완료: {len(sampled_frames)}장")
            return sampled_frames
            
        except Exception as e:
            print(f"Segement regeneration error: {e}")
            import traceback
            traceback.print_exc()
            return None


# 싱글톤 인스턴스
animator = Animator()
