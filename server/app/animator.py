"""
Animator Module - Kling AI를 사용한 애니메이션 생성
"""
import os
import time
import requests
import base64
from typing import Optional, List
import cv2
import uuid

from config.settings import settings


class Animator:
    """
    Kling AI를 사용하여 두 이미지 사이의 애니메이션을 생성하는 클래스
    """
    
    def __init__(self):
        """Kling AI 클라이언트 초기화"""
        # ! API 키 설정 확인 필수
        self.access_key = settings.KLING_ACCESS_KEY
        self.secret_key = settings.KLING_SECRET_KEY
        self.base_url = "https://api-singapore.klingai.com/v1/videos/image2video"
        
    def extract_frames_from_url(self, video_url: str, output_dir: str, frame_skip: int = 1) -> List[str]:
        """비디오/URL 프레임 추출 및 저장"""
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        temp_file_path = None
        is_url = video_url.startswith("http")
        
        # 1. 다운로드 진행
        if is_url:
            try:
                print(f"📥 비디오 다운로드 중... ({video_url[:30]}...)")
                temp_file_path = os.path.join(output_dir, f"temp_{uuid.uuid4().hex}.mp4")
                
                with requests.get(video_url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(temp_file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                print(f"✅ 다운로드 완료: {temp_file_path}")
                video_source = temp_file_path
            except Exception as e:
                print(f"❌ 비디오 다운로드 실패: {e}")
                return []
        else:
            video_source = video_url
        
        # 2. 비디오 파일 열기
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            print(f"❌ 오류: 비디오 파일을 열 수 없습니다: {video_source}")
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return []
            
        print(f"✅ 비디오 열기 성공. 프레임 추출을 시작합니다...")
        
        frame_count = 0
        saved_files = []
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
                
            if frame_count % frame_skip == 0:
                frame_filename = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_filename, frame)
                saved_files.append(frame_filename)
                
            frame_count += 1
            
        cap.release()
        print(f"총 {len(saved_files)}개의 프레임이 저장되었습니다.")
        
        # 3. 임시 파일 정리
        return saved_files
        
        return saved_files

    def _generate_jwt_token(self) -> str:
        """
        Kling AI API 인증용 JWT 생성
        ? 만료/시작 시간 보안 정책 확인
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
    ) -> Optional[tuple[List[str], str]]:
        """
        두 이미지를 시작과 끝 프레임으로 사용하여 비디오 생성
        
        Args:
            start_image_bytes: 시작 프레임 이미지 (bytes)
            end_image_bytes: 끝 프레임 이미지 (bytes)
            prompt: 비디오 생성 프롬프트
            duration: 비디오 길이 (초, 5 또는 10)
            
        Returns:
            (프레임 경로 리스트, 비디오 파일 경로) 튜플 또는 None
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
                print(f" [Status: {task_status}]\n")

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
                        # output_dir 준비 (frames 저장될 곳)
                        output_dir = os.path.join("generated_frames", project_name, task_id)
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # 비디오 파일도 output_dir 안에 저장
                        temp_video_path = os.path.join(output_dir, f"original_{task_id}.mp4")
                        
                        video_response = requests.get(video_url, stream=True, timeout=60)
                        video_response.raise_for_status()
                        
                        with open(temp_video_path, 'wb') as f:
                            for chunk in video_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                
                        print(f"다운로드 완료: {temp_video_path}")
                        
                        # 2. 로컬 파일에서 프레임 추출
                        print("프레임 추출 중...")
                        frames = self.extract_frames_from_url(temp_video_path, output_dir)
                        
                        # Return frames AND video path
                        return frames, temp_video_path
                        
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

    def generate_frame(self, image_data: bytes, prompt: str) -> bytes:
        """단일 프레임 생성 (미구현)"""
        # TODO: AI 프레임 생성 로직 구현 필요 !
        return image_data

    def _get_slow_motion_keyword(self, target_frame_count: int, duration: int = 5) -> str:
        """
        목표 프레임 수와 영상 길이를 기반으로 '얼마나 느리게' 해야 하는지 계산하고,
        그에 맞는 프롬프트 키워드를 반환하는 함수
        """
        # Kling은 보통 5초 영상에 30fps = 150프레임 정도를 만듦 (가정)
        estimated_kling_frames = 30 * duration
        
        # 압축 비율 계산 (Ratio)
        if target_frame_count <= 0: return ""
        
        slow_ratio = estimated_kling_frames / target_frame_count
        print(f"📉 계산된 슬로우 모션 비율: 약 {slow_ratio:.1f}배 (Target: {target_frame_count})")

        # 숫자 -> 형용사 매핑 (Thresholding)
        if slow_ratio > 8.0:
            return "frozen time, suspended in air, almost static"
        elif slow_ratio > 4.0:
            return "extremely slow motion, bullet time"
        elif slow_ratio > 2.0:
            return "slow motion, fluid movement"
        elif slow_ratio > 1.2:
            return "slightly slow motion, cinematic pace"
        else:
            return "normal speed, real time"

    def regenerate_video_segment(
        self,
        project_name: str,
        start_image_path: str,
        end_image_path: str,
        target_frame_count: int,
        original_prompt: str = "",
        revision_prompt: str = ""
    ) -> Optional[List[str]]:
        """
        특정 구간의 영상을 재생성하고, 필요한 프레임 수만큼 샘플링하여 반환
        """
        try:
            # 1. 이미지 로드
            with open(start_image_path, "rb") as f:
                start_bytes = f.read()
            with open(end_image_path, "rb") as f:
                end_bytes = f.read()
                
            # 2. 프롬프트 수정 (Dynamic Slow Motion & Fluidity 적용)
            # 사용자가 수정을 위해 입력한 별도 프롬프트가 있으면 그걸 우선 사용
            base_prompt = revision_prompt if revision_prompt and revision_prompt.strip() else original_prompt
            
            speed_control = self._get_slow_motion_keyword(target_frame_count)
            fluidity = "fluid motion, liquid motion, smooth morphing"
            modified_prompt = f"{base_prompt}, {speed_control}, {fluidity}, high quality, high detail, smooth transition"
            print(f"재생성 프롬프트: {modified_prompt} (Base: {base_prompt})")
            
            # 3. 비디오 생성 (전체 프레임 추출)
            revision_project_name = f"{project_name}_revision"
            
            # self.generate_video_from_images 호출
            result = self.generate_video_from_images(
                project_name=revision_project_name,
                start_image_bytes=start_bytes,
                end_image_bytes=end_bytes,
                prompt=modified_prompt,
                duration=5 
            )
            
            if not result:
                print("재생성 실패: 프레임을 생성하지 못했습니다.")
                return None

            all_frames, _ = result
                
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
                sampled_frames = all_frames
            else:
                indices = [int(i * (total_frames - 1) / (target_frame_count - 1)) for i in range(target_frame_count)]
                for idx in indices:
                    sampled_frames.append(all_frames[idx])
            
            print(f"샘플링 완료: {len(sampled_frames)}장")
            return sampled_frames
            
        except Exception as e:
            print(f"Segment regeneration error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_video_from_frames(self, frame_paths: List[str], output_path: str, fps: int = 15) -> Optional[str]:
        """
        프레임 이미지 리스트를 하나의 비디오 파일로 병합 (OpenCV 사용)
        """
        if not frame_paths:
            print("병합할 프레임이 없습니다.")
            return None

        try:
            # 첫 번째 프레임으로 크기 확인
            first_frame = cv2.imread(frame_paths[0])
            if first_frame is None:
                print(f"프레임을 읽을 수 없습니다: {frame_paths[0]}")
                return None
                
            height, width, layers = first_frame.shape
            size = (width, height)
            
            # 코덱 선택 및 폴백
            # ? 브라우저 재생 가능 코덱 우선순위 적용
            base, ext = os.path.splitext(output_path)
            ext = ext.lower()
            
            # 시도 코덱 목록
            # ! 1. WebM (VP8) - 높은 호환성
            # ! 2. WebM (VP9) - 고효율
            # ! 3. MP4 (mp4v) - 최종 폴백
            
            attempts = []
            if ext == '.webm':
                attempts.append(('VP80', output_path))
                attempts.append(('VP90', output_path))
                attempts.append(('mp4v', base + '.mp4')) # Fallback to MP4 container
            else:
                attempts.append(('mp4v', output_path))
                attempts.append(('avc1', output_path)) # Try safe avc1 if mp4 requested
            
            active_out = None
            final_path = output_path
            
            for FourCC_str, target_path in attempts:
                fourcc = cv2.VideoWriter_fourcc(*FourCC_str)
                temp_out = cv2.VideoWriter(target_path, fourcc, fps, size)
                
                if temp_out.isOpened():
                    print(f"코덱 성공: {FourCC_str} -> {target_path}")
                    active_out = temp_out
                    final_path = target_path
                    break
                else:
                    print(f"코덱 초기화 실패: {FourCC_str}")
                    if os.path.exists(target_path):
                        try: os.remove(target_path)
                        except: pass
            
            if active_out is None:
                print("모든 코덱 시도 실패")
                return None
                
            active_out.write(first_frame) # Write first frame explicitly checked above? No, rewriting loop
            
            print(f"비디오 생성 시작: {final_path} ({len(frame_paths)} frames, {fps} fps)")
            
            # 첫 번째 프레임은 이미 shape 확인용으로 읽었지만 loop에서 다시 읽음 (효율성 off)
            for i, path in enumerate(frame_paths):
                # 0번 프레임은 위에서 읽었으나 여기서 다시 읽어서 쓴다.
                if i == 0:
                    active_out.write(first_frame)
                    continue
                    
                if not os.path.exists(path):
                    continue
                
                img = cv2.imread(path)
                if img is not None:
                    active_out.write(img)
                else:
                    print(f"이미지 읽기 실패: {path}")
            
            active_out.release()
            
            # 파일 크기 확인 (0바이트면 실패로 간주)
            if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                print(f"비디오 생성 완료: {final_path} ({os.path.getsize(final_path)} bytes)")
                return final_path
            else:
                print("비디오 파일이 생성되지 않았거나 비어있습니다.")
                return None
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_zip_from_frames(self, frame_paths: List[str], output_path: str) -> Optional[str]:
        """
        프레임 이미지 리스트를 하나의 ZIP 파일로 압축
        """
        import zipfile
        
        if not frame_paths:
            return None
            
        try:
            print(f"ZIP 생성 시작: {output_path}")
            with zipfile.ZipFile(output_path, 'w') as zipf:
                for file_path in frame_paths:
                    if os.path.exists(file_path):
                        # ZIP 파일 내에 저장될 이름 (파일명만)
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                    else:
                        print(f"파일 누락 (스킵): {file_path}")
            
            print("ZIP 생성 완료")
            return output_path
        except Exception as e:
            print(f"ZIP 생성 중 오류 발생: {e}")
            return None

# 싱글톤 인스턴스
animator = Animator()
