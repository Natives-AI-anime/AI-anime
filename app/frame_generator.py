import cv2
import os

# --- 설정 ---
# 비디오가 저장된 유효하고 공개된 URL을 입력하세요. (S3, 일반 웹서버 등)
VIDEO_URL = "https://v16-kling-fdl.klingai.com/bs2/upload-ylab-stunt-sgp/muse/823589032357265490/VIDEO/20251201/0dd0a25f43c7fb2aeda6b83368e7d4da-5dcc5e17-23b7-4b44-95d1-7a1844b65362.mp4?cacheKey=ChtzZWN1cml0eS5rbGluZy5tZXRhX2VuY3J5cHQSsAE-bBsbmhmlIrmrATipavnqbyT9997OYEJMBlqD3FGYK4tiBMfK1MhxiJTod-6LP-uz5zMlSWdi7nZNSDSYC-Al_ShLthj9mU-DxUsJg2HeruKXZyoUDHysrbuFqUeLSMsuv6NLw3EHj1PKp0ay8khS_RN65Zg35cXIICYLAjWoWvU6UKZwr6T4dNYYWKNYfnVM9od3RGAit1GcsR8vMsCkPKxoQMxxfkCw9qyQb6hdsxoSsdEjH3N5CFugfV1OmSbeCusDIiDBHprQub3w2GvBHN6aAas6GtCFJcTsPYG4FLAmFYvJKygFMAE&x-kcdn-pid=112781&ksSecret=5bd5b1cb7fa943ae79be6f5d6e8758e9&ksTime=6953fa63" 
OUTPUT_DIR = "extracted_frames"
FRAME_SKIP = 1 
# --------------

# 출력 폴더 생성
os.makedirs(OUTPUT_DIR, exist_ok=True)

## 비디오 처리 시작 ##

# 1. VideoCapture에 URL을 직접 전달 (내부적으로 스트리밍/버퍼링 시작)
cap = cv2.VideoCapture(VIDEO_URL)

# 2. 비디오가 성공적으로 열렸는지 확인
if not cap.isOpened():
    print(f"❌ 오류: 비디오 URL을 열 수 없습니다. URL이나 네트워크 상태를 확인하세요.")
    exit()

print(f"✅ 비디오 스트림 연결 성공. 프레임 추출을 시작합니다...")
print("  (주의: 대용량 비디오는 시간이 오래 걸릴 수 있습니다.)")

frame_count = 0
saved_count = 0

while True:
    # 3. 프레임 읽기: ret(성공 여부), frame(실제 이미지 데이터)
    ret, frame = cap.read()

    # 프레임을 더 이상 읽을 수 없으면 (비디오 끝) 루프 종료
    if not ret:
        break 

    # 4. 프레임 처리 (설정된 간격마다 저장)
    if frame_count % FRAME_SKIP == 0:
        frame_filename = os.path.join(OUTPUT_DIR, f"frame_{frame_count:06d}.jpg")
        cv2.imwrite(frame_filename, frame)
        saved_count += 1
        print(f"  > 프레임 저장됨: {frame_filename}")

    frame_count += 1

# 5. 사용이 끝난 VideoCapture 객체 해제
cap.release()

print("\n--- 완료 ---")
print(f"총 프레임 수: {frame_count}개")
print(f"저장된 이미지 수: {saved_count}개")