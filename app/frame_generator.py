import cv2
import os
from typing import List

def extract_frames_from_url(video_url: str, output_dir: str, frame_skip: int = 1) -> List[str]:
    """
    URL에서 비디오를 스트리밍하여 프레임을 추출하고 저장합니다.
    
    Args:
        video_url: 비디오 URL
        output_dir: 프레임을 저장할 디렉토리 경로
        frame_skip: 프레임 저장 간격 (기본값: 1, 모든 프레임 저장)
        
    Returns:
        List[str]: 저장된 프레임 파일 경로 리스트
    """
    # 출력 폴더 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # VideoCapture에 URL을 직접 전달
    cap = cv2.VideoCapture(video_url)
    
    if not cap.isOpened():
        print(f"❌ 오류: 비디오 URL을 열 수 없습니다. URL이나 네트워크 상태를 확인하세요.")
        return []
        
    print(f"✅ 비디오 스트림 연결 성공. 프레임 추출을 시작합니다...")
    
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
    
    return saved_files

if __name__ == "__main__":
    # 테스트용 코드
    VIDEO_URL = "https://v16-kling-fdl.klingai.com/bs2/upload-ylab-stunt-sgp/muse/823589032357265490/VIDEO/20251201/0dd0a25f43c7fb2aeda6b83368e7d4da-5dcc5e17-23b7-4b44-95d1-7a1844b65362.mp4?cacheKey=ChtzZWN1cml0eS5rbGluZy5tZXRhX2VuY3J5cHQSsAE-bBsbmhmlIrmrATipavnqbyT9997OYEJMBlqD3FGYK4tiBMfK1MhxiJTod-6LP-uz5zMlSWdi7nZNSDSYC-Al_ShLthj9mU-DxUsJg2HeruKXZyoUDHysrbuFqUeLSMsuv6NLw3EHj1PKp0ay8khS_RN65Zg35cXIICYLAjWoWvU6UKZwr6T4dNYYWKNYfnVM9od3RGAit1GcsR8vMsCkPKxoQMxxfkCw9qyQb6hdsxoSsdEjH3N5CFugfV1OmSbeCusDIiDBHprQub3w2GvBHN6aAas6GtCFJcTsPYG4FLAmFYvJKygFMAE&x-kcdn-pid=112781&ksSecret=5bd5b1cb7fa943ae79be6f5d6e8758e9&ksTime=6953fa63" 
    OUTPUT_DIR = "extracted_frames"
    extract_frames_from_url(VIDEO_URL, OUTPUT_DIR)