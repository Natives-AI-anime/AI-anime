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


def select_output_directory() -> str:
    """프레임 저장 디렉토리 선택"""
    root = tk.Tk()
    root.withdraw()
    
    dir_path = filedialog.askdirectory(
        title="최종 결과물 저장 디렉토리 선택 (선택 사항)"
    )
    
    root.destroy()
    return dir_path

def ask_project_name() -> str:
    """프로젝트 이름 입력"""
    root = tk.Tk()
    root.withdraw()
    
    from tkinter import simpledialog
    project_name = simpledialog.askstring("프로젝트 설정", "프로젝트 이름을 입력하세요:\n(예: my_anime_project)")
    
    root.destroy()
    return project_name


def main():
    print("=" * 60)
    print("  애니메이션 비디오 생성기 (Google Veo 2)")
    print("=" * 60)
    
    # 0. 프로젝트 이름 입력
    print("\n[0/3] 프로젝트 이름을 입력하세요...")
    project_name = ask_project_name()
    
    if not project_name:
        print("❌ 프로젝트 이름이 입력되지 않았습니다. 종료합니다.")
        return
        
    print(f"✓ 프로젝트: {project_name}")

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
    
    # 3. 저장 위치 선택 (선택 사항)
    print("\n[3/3] 최종 결과물을 저장할 디렉토리를 선택하세요 (취소 시 프로젝트 폴더에만 저장됨)...")
    output_dir = select_output_directory()
    
    if output_dir:
        print(f"✓ 출력 디렉토리: {output_dir}")
    else:
        print("✓ 별도 저장 안 함 (프로젝트 폴더에만 저장)")
    
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
    
    frame_paths = animator.generate_video_from_images(
        project_name=project_name,
        start_image_bytes=start_bytes,
        end_image_bytes=end_bytes,
        prompt="Create a smooth anime-style animation transitioning from the first frame to the second frame",
    )
    
    # 결과 저장
    if frame_paths:
        print(f"\n✓ 프레임 생성 완료! ({len(frame_paths)}장)")
        print(f"  저장 위치: generated_frames/{project_name}/...")
        
        if output_dir:
            try:
                # 생성된 프레임들을 사용자가 지정한 위치로 복사
                import shutil
                
                print(f"  지정된 위치로 복사 중...")
                
                for i, src_path in enumerate(frame_paths):
                    filename = os.path.basename(src_path)
                    dst_path = os.path.join(output_dir, filename)
                    shutil.copy2(src_path, dst_path)
                    print(f"  복사됨: {dst_path}")
                
                msg = f"프레임 생성이 완료되었습니다!\n\n프로젝트: {project_name}\n추가 저장 위치: {output_dir}\n총 {len(frame_paths)}장"
            except Exception as e:
                print(f"❌ 파일 복사 실패: {e}")
                msg = f"프레임 생성은 완료되었으나 복사에 실패했습니다.\n\n프로젝트: {project_name}\n오류: {e}"
        else:
            msg = f"프레임 생성이 완료되었습니다!\n\n프로젝트: {project_name}\n저장 위치: generated_frames/{project_name}\n총 {len(frame_paths)}장"

        # 성공 메시지 박스
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("완료", msg)
        root.destroy()
            
    else:
        print("\n❌ 프레임 생성 실패")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("오류", "프레임 생성에 실패했습니다.")
        root.destroy()


if __name__ == "__main__":
    main()
