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
    
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        payload = {
            "iss": self.access_key,
            "exp": int(time.time()) + 1800, # The valid time, in this example, represents the current time+1800s(30min)
            "nbf": int(time.time()) - 5 # The time when it starts to take effect, in this example, represents the current time minus 5s
        }
        token = jwt.encode(payload, self.secret_key.strip(), headers=headers)
        return token
        
    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """이미지를 base64로 인코딩"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def generate_video_from_images(
        self, 
        start_image_bytes: bytes, 
        end_image_bytes: bytes,
        prompt: str = "Create a smooth anime-style animation transitioning from the first frame to the second frame",
        duration: int = 5
    ) -> Optional[str]:
        """
        두 이미지를 시작과 끝 프레임으로 사용하여 비디오 생성
        
        Args:
            start_image_bytes: 시작 프레임 이미지 (bytes)
            end_image_bytes: 끝 프레임 이미지 (bytes)
            prompt: 비디오 생성 프롬프트
            duration: 비디오 길이 (초, 5 또는 10)
            
        Returns:
            생성된 비디오 파일 경로 또는 None
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
                "prompt": prompt,
                "image": start_b64,  # 시작 프레임
                "image_tail": end_b64,  # 끝 프레임 (필드명은 API 문서 확인 필요)
                "duration": str(duration),
                "aspect_ratio": "16:9",
                "mode": "pro"  # 또는 "standard"
            }
            
            # API 호출
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
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
            max_attempts = 60  # 최대 10분 대기
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
                
                task_status = status_result.get("data", {}).get("status")
                
                if task_status == "completed":
                    print("\n비디오 생성 완료!")
                    
                    # 비디오 URL 가져오기
                    video_url = status_result.get("data", {}).get("video_url")
                    
                    if not video_url:
                        print("비디오 URL을 가져올 수 없습니다")
                        return None
                    
                    # 비디오 다운로드
                    print("비디오 다운로드 중...")
                    video_response = requests.get(video_url, timeout=60)
                    video_response.raise_for_status()
                    
                    # 임시 파일로 저장
                    temp_path = "temp_kling_video.mp4"
                    with open(temp_path, "wb") as f:
                        f.write(video_response.content)
                    
                    return temp_path
                    
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


# 싱글톤 인스턴스
animator = Animator()
