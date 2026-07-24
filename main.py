import os
import subprocess

def create_study_video(prefix: str, output_filename: str, repeat_config: dict, pause_ms: int = 1000):
    """
    카드 뉴스 이미지와 음성 파일을 결합하여 단어 복습용 동영상(MP4)을 생성합니다.
    """
    abs_prefix = os.path.abspath(prefix)
    pause_sec = pause_ms / 1000.0
    
    # 임시 파일명 설정
    silence_file = f"{abs_prefix}_silence.mp3"
    temp_aud_list = f"{abs_prefix}_temp_aud.txt"
    concat_list = f"{abs_prefix}_concat_list.txt"
    
    # 사용할 4가지 요소 매핑 (이미지 경로, 음성 경로)
    components = {
        "word": (f"{abs_prefix}_1_word.png", f"{abs_prefix}_1_word.mp3"),
        "meaning": (f"{abs_prefix}_2_meaning.png", f"{abs_prefix}_2_meaning.mp3"),
        "eng_sentence": (f"{abs_prefix}_3_eng_sentence.png", f"{abs_prefix}_3_eng_sentence.mp3"),
        "kor_sentence": (f"{abs_prefix}_4_kor_sentence.png", f"{abs_prefix}_4_kor_sentence.mp3")
    }

    print("🎬 비디오 생성을 준비 중입니다...")

    # 1. 1초 무음 파일 생성
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", str(pause_sec), "-c:a", "libmp3lame", silence_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    segment_videos = {}
    
    # 2. 각 파트별로 (이미지 + 오디오 + 무음)이 합쳐진 조각 영상(mp4) 생성
    for key, (img_path, aud_path) in components.items():
        if not os.path.exists(img_path) or not os.path.exists(aud_path):
            print(f"⚠️ [{key}] 이미지 또는 오디오 파일이 없어 건너뜁니다.")
            continue
            
        print(f" - [{key}] 조각 영상을 만들고 있습니다...")
        
        # (1) 원래 음성 뒤에 쉬는 시간(무음) 이어 붙이기
        padded_audio = f"{abs_prefix}_{key}_padded.mp3"
        with open(temp_aud_list, "w", encoding="utf-8") as f:
            f.write(f"file '{aud_path}'\nfile '{silence_file}'\n")
            
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
            "-i", temp_aud_list, "-c", "copy", padded_audio
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # (2) 이미지와 (1)의 오디오를 합쳐서 비디오 생성
        segment_video = f"{abs_prefix}_{key}_segment.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-framerate", "2",
            "-i", img_path, "-i", padded_audio,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-shortest",
            segment_video
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        segment_videos[key] = segment_video
        os.remove(padded_audio) # 쓰임이 끝난 임시 오디오 삭제

    # 3. 설정된 재생 순서에 따라 텍스트 리스트 작성
    with open(concat_list, "w", encoding="utf-8") as f:
        for key, repeat_count in repeat_config.items():
            if key in segment_videos:
                for _ in range(repeat_count):
                    f.write(f"file '{segment_videos[key]}'\n")

    print("\n🎞️ 조각 영상들을 하나의 영상으로 고속 병합하고 있습니다...")
    
    # 4. 전체 조각 영상 하나로 이어 붙이기 (-c copy 옵션으로 화질 저하 없이 초고속 병합)
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        output_filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. 쓰레기 파일(임시 생성물) 청소
    for temp_file in [silence_file, temp_aud_list, concat_list]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    for seg_video in segment_videos.values():
        if os.path.exists(seg_video):
            os.remove(seg_video)

    print(f"\n🎉 완벽합니다! 카드 뉴스와 음성이 결합된 동영상이 생성되었습니다: {output_filename}")


# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    # 이미지와 음성 파일이 모두 저장된 동일한 폴더 경로와 접두어 설정
    # (앞선 과정에서 만든 CardTest_01 파일들이 같은 폴더에 있어야 합니다.)
    OUTPUT_DIR = "./"
    prefix = os.path.join(OUTPUT_DIR, "CardTest_01")
    
    # 최종적으로 만들어질 비디오 파일명
    output_video = os.path.join(OUTPUT_DIR, "CardTest_01_Video.mp4")
    
    # 동영상 재생 순서 및 반복 횟수 설정
    study_playlist = {
        "word": 3,           # 영단어 이미지+음성 3번 반복
        "meaning": 1,        # 한글 뜻 1번
        "eng_sentence": 2,   # 영어 예문 2번
        "kor_sentence": 1    # 한글 해석 1번
    }
    
    # 음성 사이 쉬는 시간(무음) 1.5초(1500ms) 설정
    create_study_video(prefix, output_video, study_playlist, pause_ms=1500)