import os
import re
import asyncio
import edge_tts
from pathlib import Path

# 1. 국가 및 성별에 따른 AI 목소리 매핑
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
    """설정에 맞는 음성 파일을 생성합니다."""
    try:
        voice = VOICE_MAP[lang][accent][gender]
    except KeyError:
        print(f"❌ 지원하지 않는 설정입니다: {lang}-{accent}-{gender}")
        return

    # 비동기 함수 실행을 위한 래퍼
    asyncio.run(_create_tts(text, voice, str(output_filename)))

def create_vocab_audio_set(word, meaning, eng_sentence, kor_sentence, output_dir: Path, prefix: str):
    """하나의 단어 세트에 대해 4개의 음성 파일을 일괄 생성합니다."""
    
    # 설정: 영어는 영국 남자(uk, M), 한국어는 한국 여자(kr, F)
    eng_accent = "uk"
    eng_gender = "M"
    kor_gender = "F"
    
    # 1. 영단어 음성
    generate_audio(word, output_dir / f"{prefix}_1_word.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    
    # 2. 뜻 음성
    generate_audio(meaning, output_dir / f"{prefix}_2_meaning.mp3", lang="ko", accent="kr", gender=kor_gender)
    
    # 3. 영어 예문 음성
    generate_audio(eng_sentence, output_dir / f"{prefix}_3_eng_sentence.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    
    # 4. 한글 해석 음성
    generate_audio(kor_sentence, output_dir / f"{prefix}_4_kor_sentence.mp3", lang="ko", accent="kr", gender=kor_gender)

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
    OUTPUT_BASE_DIR = BASE_DIR / 'Audio_Results' # 오디오 결과를 모아둘 새 폴더명
    
    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
    else:
        OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
        folder_pattern = re.compile(r'^\d{3}-\d{3}$')
        target_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and folder_pattern.match(p.name)]
        
        if not target_folders:
            print(f"⚠️ '{INPUT_DIR.name}' 폴더 안에 '001-010' 형식의 폴더를 찾을 수 없습니다.")
        else:
            print(f"총 {len(target_folders)}개의 대상 폴더를 찾았습니다. 오디오 생성 작업을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                # 각 폴더(예: 001-010)별로 결과물 폴더를 별도로 생성
                folder_output_dir = OUTPUT_BASE_DIR / folder.name
                folder_output_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"📂 [{folder.name}] 오디오 파일 생성 중...")
                
                all_words = []
                for md_file in folder.rglob("*.md"):
                    if "Quiz" in md_file.name or "Answer" in md_file.name:
                        continue
                    all_words.extend(extract_words_from_md(md_file))
                
                if not all_words:
                    print("   -> 단어를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                for index, item in enumerate(all_words, 1):
                    # 파일명에 들어갈 단어 이름 안전하게 처리
                    safe_word = "".join([c for c in item['word'] if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')
                    prefix = f"{index:03d}_{safe_word}"
                    
                    create_vocab_audio_set(
                        word=item['word'],
                        meaning=item['meaning'],
                        eng_sentence=item['eng_sent'],
                        kor_sentence=item['kor_sent'],
                        output_dir=folder_output_dir,
                        prefix=prefix
                    )
                
                print(f"   -> ✅ {len(all_words)}개 단어 (총 {len(all_words) * 4}개) 음성 생성 완료.")

            print(f"\n🎉 모든 작업이 완료되었습니다! 오디오 파일은 '{OUTPUT_BASE_DIR.name}' 폴더를 확인하세요.")