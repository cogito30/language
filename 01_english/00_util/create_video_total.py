import os
import subprocess
from pathlib import Path

def create_video_from_image_and_audio(image_path: Path, audio_path: Path, output_path: Path):
    """
    FFmpeg를 사용하여 단일 이미지와 오디오를 결합해 동영상(MP4)을 생성합니다.
    """
    if not image_path.exists():
        print(f"⚠️ 이미지 파일을 찾을 수 없습니다: {image_path.name}")
        return False
    if not audio_path.exists():
        print(f"⚠️ 오디오 파일을 찾을 수 없습니다: {audio_path.name}")
        return False

    # FFmpeg 명령어 구성
    # -loop 1: 한 장의 이미지를 영상 내내 반복 출력
    # -shortest: 오디오 길이에 맞춰 동영상 길이 설정
    # -c:v libx264 / -pix_fmt yuv420p: 인스타그램, 유튜브 등 범용 호환성을 위한 비디오 코덱 설정
    # -c:a aac: 범용 오디오 코덱 설정
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path.absolute()),
        "-i", str(audio_path.absolute()),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(output_path.absolute())
    ]

    try:
        # 콘솔 출력을 억제하여 깔끔하게 실행
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 동영상 생성 실패: {output_path.name}")
        return False

# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.')
    
    # 입력으로 사용할 폴더 경로
    CARD_DIR = BASE_DIR / 'Card_Results'
    AUDIO_DIR = BASE_DIR / 'Audio_Results'
    
    # 출력물을 저장할 새 폴더 경로
    VIDEO_DIR = BASE_DIR / 'Video_Results'

    if not CARD_DIR.exists() or not AUDIO_DIR.exists():
        print("⚠️ 'Card_Results' 또는 'Audio_Results' 폴더를 찾을 수 없습니다.")
        print("먼저 카드 뉴스와 오디오 파일을 생성해주세요.")
    else:
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        
        # Card_Results 안에 있는 '001-010' 등의 폴더들 탐색
        target_folders = [p for p in CARD_DIR.iterdir() if p.is_dir()]
        
        if not target_folders:
            print("⚠️ 'Card_Results' 폴더 안에 처리할 하위 폴더가 없습니다.")
        else:
            print(f"🎬 총 {len(target_folders)}개의 폴더에서 동영상 제작을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                folder_name = folder.name
                
                # 영상이 저장될 출력 폴더 생성 (예: Video_Results/001-010)
                folder_video_dir = VIDEO_DIR / folder_name
                folder_video_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"📂 [{folder_name}] 동영상 파일 생성 중...")
                
                # 카드 폴더 안에 있는 모든 통합 카드(_card.png) 탐색
                card_files = list(folder.glob("*_card.png"))
                
                if not card_files:
                    print("   -> 카드 이미지를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                success_count = 0
                for img_path in sorted(card_files):
                    # 파일명에서 단어의 기본 이름(prefix) 추출 
                    # 예: 001_Apple_card.png -> 001_Apple
                    base_name = img_path.name.replace("_card.png", "")
                    
                    # 짝이 맞는 마스터 오디오 파일 경로 추적
                    # (이전 스크립트에서 Master 폴더 안에 저장되도록 설정했었음)
                    audio_path = AUDIO_DIR / folder_name / "Master" / f"{base_name}_Master_Study.mp3"
                    
                    # 출력될 동영상 파일 경로
                    output_video = folder_video_dir / f"{base_name}_Video.mp4"
                    
                    # 동영상 생성 실행
                    if create_video_from_image_and_audio(img_path, audio_path, output_video):
                        success_count += 1
                        
                print(f"   -> ✅ 총 {success_count}개의 동영상 생성 완료.")

            print(f"\n🎉 모든 작업이 완료되었습니다! 숏폼/영상 파일은 '{VIDEO_DIR.name}' 폴더를 확인하세요.")