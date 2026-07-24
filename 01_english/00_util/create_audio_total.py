import os
import re
import asyncio
import subprocess
import edge_tts
from pathlib import Path

# ==========================================
# 1. TTS 음성 생성 로직
# ==========================================
VOICE_MAP = {
    "en": {
        "us": {"M": "en-US-GuyNeural", "F": "en-US-JennyNeural"},     
        "uk": {"M": "en-GB-RyanNeural", "F": "en-GB-SoniaNeural"},    
        "au": {"M": "en-AU-WilliamNeural", "F": "en-AU-NatashaNeural"} 
    },
    "ko": {
        "kr": {"M": "ko-KR-InJoonNeural", "F": "ko-KR-SunHiNeural"}   
    }
}

async def _create_tts(text: str, voice: str, output_path: str):
    """실제 edge-tts를 사용해 음성 파일을 생성하는 비동기 함수"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_audio(text: str, output_filename: str, lang: str = "en", accent: str = "us", gender: str = "F"):
    """설정에 맞는 개별 음성 파일을 생성합니다."""
    try:
        voice = VOICE_MAP[lang][accent][gender]
    except KeyError:
        print(f"❌ 지원하지 않는 설정입니다: {lang}-{accent}-{gender}")
        return

    asyncio.run(_create_tts(text, voice, str(output_filename)))

def create_vocab_audio_set(word, meaning, eng_sentence, kor_sentence, prefix: str):
    """하나의 단어 세트에 대해 4개의 개별 음성 파일을 일괄 생성합니다."""
    
    eng_accent = "uk"
    eng_gender = "M"
    kor_gender = "F"
    
    generate_audio(word, f"{prefix}_1_word.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    generate_audio(meaning, f"{prefix}_2_meaning.mp3", lang="ko", accent="kr", gender=kor_gender)
    generate_audio(eng_sentence, f"{prefix}_3_eng_sentence.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    generate_audio(kor_sentence, f"{prefix}_4_kor_sentence.mp3", lang="ko", accent="kr", gender=kor_gender)


# ==========================================
# 2. FFmpeg 오디오 병합 로직
# ==========================================
def merge_study_audio(prefix: str, output_filename: str, repeat_config: dict, pause_ms: int = 1000):
    """FFmpeg를 제어하여 설정된 반복 횟수와 무음 구간을 적용해 오디오를 병합합니다."""
    files = {
        "word": f"{prefix}_1_word.mp3",
        "meaning": f"{prefix}_2_meaning.mp3",
        "eng_sentence": f"{prefix}_3_eng_sentence.mp3",
        "kor_sentence": f"{prefix}_4_kor_sentence.mp3"
    }
    
    abs_prefix = os.path.abspath(prefix)
    silence_file = f"{abs_prefix}_silence.mp3"
    list_file = f"{abs_prefix}_concat_list.txt"
    pause_sec = pause_ms / 1000.0

    # 1. 무음 mp3 파일 생성 (edge-tts와 동일한 24kHz 모노)
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
        "-t", str(pause_sec), "-c:a", "libmp3lame", silence_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. 파일 목록 작성 (백슬래시 이슈를 막기 위해 슬래시로 변경)
    with open(list_file, "w", encoding="utf-8") as f:
        for key, repeat_count in repeat_config.items():
            file_path = os.path.abspath(files.get(key)).replace('\\', '/')
            silence_path = silence_file.replace('\\', '/')
            
            if not os.path.exists(file_path):
                print(f"⚠️ 경고: {file_path} 파일을 찾을 수 없어 건너뜁니다.")
                continue
                
            for _ in range(repeat_count):
                f.write(f"file '{file_path}'\n")
                f.write(f"file '{silence_path}'\n")

    # 3. 고속 병합
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c:a", "libmp3lame",  
        output_filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. 임시 파일 정리
    if os.path.exists(silence_file):
        os.remove(silence_file)
    if os.path.exists(list_file):
        os.remove(list_file)


# ==========================================
# 3. 텍스트 추출 로직
# ==========================================
def extract_words_from_md(file_path: Path):
    """md 파일에서 단어 데이터를 추출합니다."""
    vocab_list = []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    current_item = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        word_match = re.match(r'^\d+\.\s+([^:]+):\s*(.+)', line)
        if word_match:
            if 'word' in current_item and 'eng_sent' in current_item and 'kor_sent' in current_item:
                vocab_list.append(current_item)
            current_item = {
                'word': word_match.group(1).strip(),
                'meaning': word_match.group(2).strip()
            }
        elif line.startswith('-') and 'word' in current_item:
            sentence = line[1:].strip()
            if 'eng_sent' not in current_item:
                current_item['eng_sent'] = sentence
            elif 'kor_sent' not in current_item:
                current_item['kor_sent'] = sentence
                
    if 'word' in current_item and 'eng_sent' in current_item and 'kor_sent' in current_item:
        vocab_list.append(current_item)
        
    return vocab_list


# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.')
    INPUT_DIR = BASE_DIR / 'input'
    OUTPUT_BASE_DIR = BASE_DIR / 'Audio_Results'
    
    # 병합할 때의 재생 순서 및 반복 횟수 설정
    STUDY_PLAYLIST = {
        "word": 3,           
        "meaning": 1,        
        "eng_sentence": 2,   
        "kor_sentence": 1    
    }

    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
    else:
        OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
        folder_pattern = re.compile(r'^\d{3}-\d{3}$')
        target_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and folder_pattern.match(p.name)]
        
        if not target_folders:
            print(f"⚠️ '{INPUT_DIR.name}' 폴더 안에 '001-010' 형식의 폴더를 찾을 수 없습니다.")
        else:
            print(f"총 {len(target_folders)}개의 대상 폴더를 찾았습니다. 오디오 생성 및 병합을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                # 개별 파일과 통합 파일을 저장할 하위 폴더 경로 설정
                individual_dir = OUTPUT_BASE_DIR / folder.name / 'Individual'
                master_dir = OUTPUT_BASE_DIR / folder.name / 'Master'
                
                # 폴더 생성
                individual_dir.mkdir(parents=True, exist_ok=True)
                master_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"📂 [{folder.name}] 처리 중...")
                
                all_words = []
                for md_file in folder.rglob("*.md"):
                    if "Quiz" in md_file.name or "Answer" in md_file.name:
                        continue
                    all_words.extend(extract_words_from_md(md_file))
                
                if not all_words:
                    print("   -> 단어를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                for index, item in enumerate(all_words, 1):
                    safe_word = "".join([c for c in item['word'] if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')
                    
                    # prefix는 Individual 폴더를 향하도록 설정
                    prefix = str(individual_dir / f"{index:03d}_{safe_word}")
                    # master_output은 Master 폴더를 향하도록 설정
                    master_output = str(master_dir / f"{index:03d}_{safe_word}_Master_Study.mp3")
                    
                    # 1. 개별 음성 파일 4개 생성 (Individual 폴더에 저장됨)
                    create_vocab_audio_set(
                        word=item['word'],
                        meaning=item['meaning'],
                        eng_sentence=item['eng_sent'],
                        kor_sentence=item['kor_sent'],
                        prefix=prefix
                    )
                    
                    # 2. 생성된 4개의 파일을 FFmpeg로 병합 (Master 폴더에 저장됨)
                    merge_study_audio(
                        prefix=prefix,
                        output_filename=master_output,
                        repeat_config=STUDY_PLAYLIST,
                        pause_ms=1500
                    )
                
                print(f"   -> ✅ {len(all_words)}개 단어 세트 생성 완료 (분리 저장됨).")

            print(f"\n🎉 모든 작업이 완료되었습니다! 오디오 파일은 '{OUTPUT_BASE_DIR.name}' 폴더를 확인하세요.")