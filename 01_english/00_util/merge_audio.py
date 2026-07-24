import os
import subprocess

def merge_study_audio(prefix: str, output_filename: str, repeat_config: dict, pause_ms: int = 1000):
    """
    Python 3.13 환경에서 외부 라이브러리(pydub) 없이 FFmpeg를 직접 제어하여 오디오를 병합합니다.
    """
    files = {
        "word": f"{prefix}_1_word.mp3",
        "meaning": f"{prefix}_2_meaning.mp3",
        "eng_sentence": f"{prefix}_3_eng_sentence.mp3",
        "kor_sentence": f"{prefix}_4_kor_sentence.mp3"
    }
    
    # 안전한 처리를 위해 절대 경로 사용
    abs_prefix = os.path.abspath(prefix)
    silence_file = f"{abs_prefix}_silence.mp3"
    list_file = f"{abs_prefix}_concat_list.txt"
    
    pause_sec = pause_ms / 1000.0

    print("🛠️ 임시 무음(쉬는 시간) 파일을 생성 중입니다...")
    # 1. FFmpeg를 사용해 정확한 길이의 무음 mp3 파일 생성 (edge-tts와 동일한 24kHz 모노 설정)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", str(pause_sec), "-c:a", "libmp3lame", silence_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. 병합할 파일의 순서를 담은 텍스트 파일(List) 작성
    with open(list_file, "w", encoding="utf-8") as f:
        for key, repeat_count in repeat_config.items():
            file_path = os.path.abspath(files.get(key))
            
            if not os.path.exists(file_path):
                print(f"⚠️ 경고: {file_path} 파일을 찾을 수 없어 건너뜁니다.")
                continue
                
            for _ in range(repeat_count):
                # FFmpeg concat 규격: file '경로'
                f.write(f"file '{file_path}'\n")
                f.write(f"file '{silence_file}'\n")

    print("🎧 설정된 횟수만큼 오디오를 이어 붙이고 있습니다...")
    # 3. FFmpeg concat 모드를 사용하여 하나의 파일로 고속 병합
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c:a", "libmp3lame",  # 안정성을 위해 재인코딩
        output_filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. 작업이 끝난 후 임시 파일들 정리(삭제)
    if os.path.exists(silence_file):
        os.remove(silence_file)
    if os.path.exists(list_file):
        os.remove(list_file)

    print(f"\n🎉 병합 완료! 최종 오디오 파일이 생성되었습니다: {output_filename}")


# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    OUTPUT_DIR = "./Audio_Files"
    # 앞서 음성을 만들 때 생성된 파일들이 있는 폴더와 접두어 지정
    prefix = os.path.join(OUTPUT_DIR, "CardTest_01")
    output_filename = os.path.join(OUTPUT_DIR, "CardTest_01_Master_Study.mp3")
    
    # 재생 순서 및 반복 횟수 설정
    study_playlist = {
        "word": 3,           # 영단어를 3번 들려줌
        "meaning": 1,        # 한글 뜻 1번
        "eng_sentence": 2,   # 영어 예문 2번
        "kor_sentence": 1    # 한글 해석 1번
    }
    
    # 단어 사이 1.5초 무음 설정으로 실행
    merge_study_audio(prefix, output_filename, study_playlist, pause_ms=1500)