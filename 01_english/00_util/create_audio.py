import asyncio
import edge_tts
import os

# 1. 국가 및 성별에 따른 AI 목소리 매핑
VOICE_MAP = {
    "en": {
        "us": {"M": "en-US-GuyNeural", "F": "en-US-JennyNeural"},     # 미국: 남/여
        "uk": {"M": "en-GB-RyanNeural", "F": "en-GB-SoniaNeural"},    # 영국: 남/여
        "au": {"M": "en-AU-WilliamNeural", "F": "en-AU-NatashaNeural"} # 호주: 남/여
    },
    "ko": {
        "kr": {"M": "ko-KR-InJoonNeural", "F": "ko-KR-SunHiNeural"}   # 한국: 남/여
    }
}

async def _create_tts(text: str, voice: str, output_path: str):
    """실제 edge-tts를 사용해 음성 파일을 생성하는 비동기 함수"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_audio(text: str, output_filename: str, lang: str = "en", accent: str = "us", gender: str = "F"):
    """
    설정에 맞는 음성 파일을 생성합니다.
    :param lang: 언어 ("en" 또는 "ko")
    :param accent: 발음 국가 ("us", "uk", "au" / 한국어는 "kr")
    :param gender: 성별 ("M" 또는 "F")
    """
    try:
        voice = VOICE_MAP[lang][accent][gender]
    except KeyError:
        print(f"❌ 지원하지 않는 설정입니다: {lang}-{accent}-{gender}")
        return

    # 비동기 함수 실행을 위한 래퍼
    asyncio.run(_create_tts(text, voice, output_filename))
    print(f"✅ 음성 생성 완료: {output_filename} (Voice: {voice})")

def create_vocab_audio_set(word, meaning, eng_sentence, kor_sentence, prefix="001"):
    """하나의 단어 세트에 대해 4개의 음성 파일을 일괄 생성합니다."""
    
    # 설정 예시: 영어는 영국 남자(uk, M), 한국어는 여자(kr, F)로 설정해보겠습니다.
    eng_accent = "uk"
    eng_gender = "M"
    kor_gender = "F"
    
    print(f"[{word}] 음성 파일 생성을 시작합니다...")
    
    # 1. 영단어 음성
    generate_audio(word, f"{prefix}_1_word.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    
    # 2. 뜻 음성
    generate_audio(meaning, f"{prefix}_2_meaning.mp3", lang="ko", accent="kr", gender=kor_gender)
    
    # 3. 영어 예문 음성
    generate_audio(eng_sentence, f"{prefix}_3_eng_sentence.mp3", lang="en", accent=eng_accent, gender=eng_gender)
    
    # 4. 한글 해석 음성
    generate_audio(kor_sentence, f"{prefix}_4_kor_sentence.mp3", lang="ko", accent="kr", gender=kor_gender)


# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    # 테스트용 폴더 생성
    OUTPUT_DIR = "./Audio_Files"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 샘플 데이터
    word = "Procrastination"
    meaning = "미루는 버릇, 지연"
    eng_sentence = "Procrastination is often caused by anxiety."
    kor_sentence = "미루는 버릇은 종종 불안감 때문에 발생합니다."
    
    # 출력 경로 설정
    prefix = os.path.join(OUTPUT_DIR, "CardTest_01")
    
    # 함수 실행
    create_vocab_audio_set(word, meaning, eng_sentence, kor_sentence, prefix=prefix)
    
    print("\n🎉 모든 오디오 파일 생성이 완료되었습니다. 폴더를 확인해보세요!")