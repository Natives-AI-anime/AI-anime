"""
Animator 테스트 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.animator import animator

print("Animator 인스턴스 생성 성공!")
print(f"클라이언트: {animator.client}")
print(f"모델명: {animator.model_name}")

# 간단한 테스트
print("\n사용 가능한 메서드:")
print("- generate_video_from_images(start_bytes, end_bytes, prompt)")
print("- generate_video_from_text(prompt, duration, resolution, style)")
