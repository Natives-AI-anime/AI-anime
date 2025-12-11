"""
GUI로 이미지 2장 선택해서 비디오 생성
"""
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.animator import animator


def select_image(title: str) -> str:
    """파일 선택 대화상자를 열어 이미지 선택"""
    root = tk.Tk()
    root.withdraw()  # 메인 윈도우 숨기기
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[
            ("이미지 파일", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("모든 파일", "*.*")
        ]
    )
    
    root.destroy()
    return file_path


def save_video_dialog() -> str:
    """비디오 저장 위치 선택"""
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.asksaveasfilename(
        title="비디오 저장 위치 선택",
        defaultextension=".mp4",
        filetypes=[
            ("MP4 비디오", "*.mp4"),
            ("모든 파일", "*.*")
        ]
    )
    
    root.destroy()
    return file_path


def main():
    print("=" * 60)
    print("  애니메이션 비디오 생성기 (Google Veo 2)")
    print("=" * 60)
    
    # 1. 시작 프레임 선택
    print("\n[1/3] 시작 프레임 이미지를 선택하세요...")
    start_image_path = select_image("시작 프레임 선택")
    
    if not start_image_path:
        print("❌ 시작 이미지가 선택되지 않았습니다. 종료합니다.")
        return
    
    print(f"✓ 시작 이미지: {start_image_path}")
    
    # 2. 끝 프레임 선택
    print("\n[2/3] 끝 프레임 이미지를 선택하세요...")
    end_image_path = select_image("끝 프레임 선택")
    
    if not end_image_path:
        print("❌ 끝 이미지가 선택되지 않았습니다. 종료합니다.")
        return
    
    print(f"✓ 끝 이미지: {end_image_path}")
    
    # 3. 저장 위치 선택
    print("\n[3/3] 비디오 저장 위치를 선택하세요...")
    output_path = save_video_dialog()
    
    if not output_path:
        print("❌ 저장 위치가 선택되지 않았습니다. 종료합니다.")
        return
    
    print(f"✓ 출력 경로: {output_path}")
    
    # 이미지 파일 읽기
    print("\n" + "=" * 60)
    print("이미지 로딩 중...")
    print("=" * 60)
    
    try:
        with open(start_image_path, "rb") as f:
            start_bytes = f.read()
        print(f"✓ 시작 이미지 로드 완료 ({len(start_bytes):,} bytes)")
        
        with open(end_image_path, "rb") as f:
            end_bytes = f.read()
        print(f"✓ 끝 이미지 로드 완료 ({len(end_bytes):,} bytes)")
        
    except Exception as e:
        print(f"❌ 이미지 로드 실패: {e}")
        return
    
    # 비디오 생성
    print("\n" + "=" * 60)
    print("비디오 생성 중... (시간이 걸릴 수 있습니다)")
    print("=" * 60)
    
    temp_video_path = animator.generate_video_from_images(
        start_image_bytes=start_bytes,
        end_image_bytes=end_bytes,
        prompt="Create a smooth anime-style animation transitioning from the first frame to the second frame",
    )
    
    # 결과 저장
    if temp_video_path and os.path.exists(temp_video_path):
        try:
            # 임시 파일을 사용자가 지정한 위치로 복사
            import shutil
            shutil.move(temp_video_path, output_path)
            
            file_size = os.path.getsize(output_path)
            print(f"\n✓ 비디오 생성 완료!")
            print(f"  파일: {output_path}")
            print(f"  크기: {file_size:,} bytes")
            
            # 성공 메시지 박스
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(
                "완료", 
                f"비디오가 성공적으로 생성되었습니다!\n\n{output_path}"
            )
            root.destroy()
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
    else:
        print("\n❌ 비디오 생성 실패")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("오류", "비디오 생성에 실패했습니다.")
        root.destroy()


if __name__ == "__main__":
    main()
