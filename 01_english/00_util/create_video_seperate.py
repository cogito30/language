import os
import subprocess
from pathlib import Path

def create_video_from_image_and_audio(image_path: Path, audio_path: Path, output_path: Path):
    """FFmpeg를 사용하여 단일 이미지와 오디오를 결합해 동영상(MP4)을 생성합니다."""
    if not image_path.exists():
        return False
    if not audio_path.exists():
        return False

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
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 동영상 생성 실패: {output_path.name}")
        return False

def find_image_file(card_dir: Path, target_filename: str):
    """카드 폴더 내에서 특정 이름의 이미지 파일을 재귀적으로 찾습니다."""
    for img_path in card_dir.rglob("*.png"):
        if img_path.name == target_filename:
            return img_path
    return None

# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.')
    
    CARD_DIR = BASE_DIR / 'Card_Results'
    AUDIO_DIR = BASE_DIR / 'Audio_Results'
    VIDEO_DIR = BASE_DIR / 'Video_Results'

    if not CARD_DIR.exists() or not AUDIO_DIR.exists():
        print("⚠️ 'Card_Results' 또는 'Audio_Results' 폴더를 찾을 수 없습니다.")
    else:
        VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        
        # Audio_Results 안의 '001-010' 등 대상 폴더 탐색
        target_folders = [p for p in AUDIO_DIR.iterdir() if p.is_dir()]
        
        if not target_folders:
            print("⚠️ 'Audio_Results' 폴더 안에 처리할 하위 폴더가 없습니다.")
        else:
            print(f"🎬 총 {len(target_folders)}개의 폴더에서 동영상 제작을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                folder_name = folder.name
                print(f"📂 [{folder_name}] 처리 중...")
                
                # 영상이 저장될 출력 폴더 (Individual / Master 분리)
                individual_video_dir = VIDEO_DIR / folder_name / 'Individual'
                master_video_dir = VIDEO_DIR / folder_name / 'Master'
                individual_video_dir.mkdir(parents=True, exist_ok=True)
                master_video_dir.mkdir(parents=True, exist_ok=True)
                
                # 짝을 찾을 카드 폴더 경로
                current_card_dir = CARD_DIR / folder_name
                
                # --------------------------------------------------
                # 1. 개별(Individual) 동영상 병합
                # --------------------------------------------------
                individual_audio_dir = folder / 'Individual'
                indiv_success = 0
                
                if individual_audio_dir.exists():
                    for audio_path in individual_audio_dir.glob("*.mp3"):
                        # 예: 001_Apple_1_word.mp3 -> 001_Apple_1_word.png 찾기
                        base_name = audio_path.stem
                        img_filename = f"{base_name}.png"
                        img_path = find_image_file(current_card_dir, img_filename)
                        
                        if img_path:
                            output_video = individual_video_dir / f"{base_name}_Video.mp4"
                            if create_video_from_image_and_audio(img_path, audio_path, output_video):
                                indiv_success += 1
                
                # --------------------------------------------------
                # 2. 통합 마스터(Master) 동영상 병합
                # --------------------------------------------------
                master_audio_dir = folder / 'Master'
                master_success = 0
                
                if master_audio_dir.exists():
                    for audio_path in master_audio_dir.glob("*_Master_Study.mp3"):
                        # 예: 001_Apple_Master_Study.mp3 -> 001_Apple_card.png 찾기
                        base_name = audio_path.name.replace("_Master_Study.mp3", "")
                        img_filename = f"{base_name}_card.png"
                        img_path = find_image_file(current_card_dir, img_filename)
                        
                        if img_path:
                            output_video = master_video_dir / f"{base_name}_Master_Video.mp4"
                            if create_video_from_image_and_audio(img_path, audio_path, output_video):
                                master_success += 1
                                
                print(f"   -> ✅ 개별 영상 {indiv_success}개 / 마스터 영상 {master_success}개 생성 완료.")

            print(f"\n🎉 모든 작업이 완료되었습니다! 분리된 영상 파일들은 '{VIDEO_DIR.name}' 폴더를 확인하세요.")