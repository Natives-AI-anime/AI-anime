import cv2
import os
import requests
import uuid
import time
from typing import List

def extract_frames_from_url(video_url: str, output_dir: str, frame_skip: int = 1) -> List[str]:
    """
    URL에서 비디오를 다운로드 후 프레임을 추출하고 저장합니다.
    (직접 URL 스트리밍보다 다운로드 후 처리가 훨씬 안정적입니다)
    
    Args:
        video_url: 비디오 URL 혹은 로컬 파일 경로
        output_dir: 프레임을 저장할 디렉토리 경로
        frame_skip: 프레임 저장 간격 (기본값: 1)
        
    Returns:
        List[str]: 저장된 프레임 파일 경로 리스트
    """
    # 출력 폴더 생성
    os.makedirs(output_dir, exist_ok=True)
    
    temp_file_path = None
    is_url = video_url.startswith("http")
    
    # 1. URL인 경우 다운로드 진행
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
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
            print("🧹 임시 비디오 파일 삭제 완료")
        except Exception as e:
            print(f"⚠️ 임시 파일 삭제 실패 (무시됨): {e}")
    
    return saved_files

if __name__ == "__main__":
    # 테스트용 코드
    VIDEO_URL = "https://v16-kling-fdl.klingai.com/bs2/upload-ylab-stunt-sgp/muse/823589032357265490/VIDEO/20251201/0dd0a25f43c7fb2aeda6b83368e7d4da-5dcc5e17-23b7-4b44-95d1-7a1844b65362.mp4?cacheKey=ChtzZWN1cml0eS5rbGluZy5tZXRhX2VuY3J5cHQSsAE-bBsbmhmlIrmrATipavnqbyT9997OYEJMBlqD3FGYK4tiBMfK1MhxiJTod-6LP-uz5zMlSWdi7nZNSDSYC-Al_ShLthj9mU-DxUsJg2HeruKXZyoUDHysrbuFqUeLSMsuv6NLw3EHj1PKp0ay8khS_RN65Zg35cXIICYLAjWoWvU6UKZwr6T4dNYYWKNYfnVM9od3RGAit1GcsR8vMsCkPKxoQMxxfkCw9qyQb6hdsxoSsdEjH3N5CFugfV1OmSbeCusDIiDBHprQub3w2GvBHN6aAas6GtCFJcTsPYG4FLAmFYvJKygFMAE&x-kcdn-pid=112781&ksSecret=5bd5b1cb7fa943ae79be6f5d6e8758e9&ksTime=6953fa63" 
    OUTPUT_DIR = "extracted_frames"
    extract_frames_from_url(VIDEO_URL, OUTPUT_DIR)