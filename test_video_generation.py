import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

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
    
    project_name = simpledialog.askstring("프로젝트 설정", "프로젝트 이름을 입력하세요:\n(예: my_anime_project)")
    
    root.destroy()
    return project_name

def ask_prompt(default_prompt: str = "") -> str:
    """애니메이션 프롬프트 입력"""
    root = tk.Tk()
    root.withdraw()
    
    prompt = simpledialog.askstring(
        "프롬프트 설정", 
        "비디오 생성을 위한 프롬프트를 입력하세요:", 
        initialvalue=default_prompt
    )
    
    root.destroy()
    return prompt if prompt else default_prompt


def main():
    print("=" * 60)
    print("  애니메이션 비디오 생성기 (Kling AI)")
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

    # 2.5 프롬프트 입력
    print("\n[2.5/3] 프롬프트를 입력하세요...")
    user_prompt = ask_prompt()
    print(f"✓ 프롬프트: {user_prompt}")
    
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
        prompt=user_prompt,
    )
    

    # 결과 저장 및 수정 루프
    if frame_paths:
        print(f"\n✓ 프레임 생성 완료! ({len(frame_paths)}장)")
        print(f"  저장 위치: generated_frames/{project_name}/...")
        
        while True:
            # 수정 여부 확인
            root = tk.Tk()
            root.withdraw()
            
            do_revise = messagebox.askyesno("수정", "특정 구간이 마음에 들지 않으신가요?\n\n해당 구간만 다시 생성(Revision)할 수 있습니다.")
            root.destroy()
            
            if not do_revise:
                break
                
            # 구간 선택
            print("\n--- 프레임 수정 모드 ---")
            print(f"현재 총 프레임 수: {len(frame_paths)} (인덱스: 0 ~ {len(frame_paths)-1})")
            
            root = tk.Tk()
            root.withdraw()
            
            start_idx = simpledialog.askinteger("구간 시작", f"수정을 시작할 프레임 번호를 입력하세요 (0 ~ {len(frame_paths)-1}):", minvalue=0, maxvalue=len(frame_paths)-1)
            if start_idx is None: 
                root.destroy()
                continue
                
            end_idx = simpledialog.askinteger("구간 끝", f"수정을 끝낼 프레임 번호를 입력하세요 ({start_idx} ~ {len(frame_paths)-1}):", minvalue=start_idx, maxvalue=len(frame_paths)-1)
            root.destroy()
            
            if end_idx is None:
                continue
                
            target_count = end_idx - start_idx + 1
            print(f"선택 구간: {start_idx} ~ {end_idx} (총 {target_count}장)")
            
            # 재생성 요청
            print("구간 재생성 중... (5초 생성 후 샘플링)")
            new_frames = animator.regenerate_video_segment(
                project_name=project_name,
                start_image_path=frame_paths[start_idx],
                end_image_path=frame_paths[end_idx],
                target_frame_count=target_count,
                original_prompt=user_prompt
            )
            
            if new_frames and len(new_frames) == target_count:
                print("✓ 구간 재생성 성공! 파일을 덮어씁니다.")
                # 파일 덮어쓰기
                for i, new_frame_path in enumerate(new_frames):
                    original_frame_path = frame_paths[start_idx + i]
                    
                    # 새 프레임을 원본 위치로 복사/이동 (덮어쓰기)
                    # new_frames는 revision 폴더에 있음
                    import shutil
                    shutil.copy2(new_frame_path, original_frame_path)
                    print(f"  Updated: {original_frame_path}")
                
                print("수정 완료.")
            else:
                print("❌ 구간 재생성 실패 또는 프레임 수 불일치.")
        
        
        # 최종 결과 복사 (Revision 반영된 최종본)
        if output_dir:
            try:
                # 생성된 프레임들을 사용자가 지정한 위치로 복사
                import shutil
                
                print(f"\n최종 결과물을 지정된 위치로 복사 중...")
                
                for i, src_path in enumerate(frame_paths):
                    filename = os.path.basename(src_path)
                    dst_path = os.path.join(output_dir, filename)
                    shutil.copy2(src_path, dst_path)
                    print(f"  복사됨: {dst_path}")
                
                msg = f"모든 작업이 완료되었습니다!\n\n프로젝트: {project_name}\n추가 저장 위치: {output_dir}\n총 {len(frame_paths)}장"
            except Exception as e:
                print(f"❌ 파일 복사 실패: {e}")
                msg = f"작업은 완료되었으나 복사에 실패했습니다.\n\n프로젝트: {project_name}\n오류: {e}"
        else:
            msg = f"작업이 완료되었습니다!\n\n프로젝트: {project_name}\n저장 위치: generated_frames/{project_name}\n총 {len(frame_paths)}장"

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
