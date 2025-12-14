import requests

# 이미지 파일 경로
image_path = r"C:/Users/rladu/.gemini/antigravity/brain/228ed353-8601-42f2-8bc5-b1879dda9180/uploaded_image_1763895300422.png"

# API 엔드포인트
url = "http://localhost:8000/generate-frame"

# 이미지 파일 열기
with open(image_path, "rb") as f:
    files = {"file": ("manga_panel.png", f, "image/png")}
    data = {"prompt": ""}  # 추가 프롬프트 없음
    
    print("🚀 API 요청 전송 중...")
    print(f"📸 원본 이미지: {image_path}")
    
    try:
        response = requests.post(url, files=files, data=data, timeout=60)
        
        print(f"\n✅ 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n📊 응답 내용:")
            print(f"  - 메시지: {result['message']}")
            print(f"  - 원본 파일명: {result['data']['original_filename']}")
            
            # 생성된 이미지 저장
            import base64
            image_data = result['data']['generated_image']
            
            # data:image/png;base64, 부분 제거
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # base64 디코딩
            image_bytes = base64.b64decode(image_data)
            
            # 파일로 저장
            output_path = "generated_frame_16_9.png"
            with open(output_path, "wb") as out_file:
                out_file.write(image_bytes)
            
            print(f"\n💾 생성된 이미지 저장됨: {output_path}")
            print(f"   크기: {len(image_bytes)} bytes")
            print(f"   비율: 16:9 (1024x576)")
        else:
            print(f"\n❌ 에러 발생:")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
