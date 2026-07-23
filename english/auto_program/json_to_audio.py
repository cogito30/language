import json
import os
import sys
import asyncio
import edge_tts

# 1. 억양 및 성별에 따른 Microsoft Edge Neural TTS 목소리 매핑
VOICES = {
    "us": {
        "female": "en-US-AriaNeural",
        "male": "en-US-GuyNeural"
    },
    "uk": {
        "female": "en-GB-SoniaNeural",
        "male": "en-GB-RyanNeural"
    },
    "ko": {
        "female": "ko-KR-SunHiNeural",
        "male": "ko-KR-InJoonNeural"
    }
}

async def generate_speech(text, voice, filename):
    """지정된 텍스트와 목소리로 개별 MP3 파일을 비동기 생성합니다."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filename)

async def create_audio_files(json_path, accent="us", gender="female", output_dir="audio_output"):
    if not os.path.exists(json_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다. ({json_path})")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vocabulary = data.get("vocabulary", [])
    total_words = len(vocabulary)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. 사용자가 선택한 억양과 성별에 맞는 목소리 세팅
    eng_voice = VOICES[accent][gender]
    kor_voice = VOICES["ko"][gender]

    print(f"🚀 총 {total_words}개의 단어 음성 파일 생성을 시작합니다...")
    print(f"🎙️ 설정된 목소리: 영어({accent.upper()}, {gender}) / 한국어({gender})\n")

    # 3. 단어별 음성 생성 로직
    for i, item in enumerate(vocabulary, 1):
        word = item.get("word", "")
        meanings = ", ".join(item.get("meanings", []))
        example_en = item.get("example", "")
        example_ko = item.get("translation", "")

        safe_word = "".join(c for c in word if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        output_filename = os.path.join(output_dir, f"audio_{i:02d}_{safe_word}.mp3")

        # 각 파트별 임시 파일 이름
        temp_files = [
            f"temp_word_{i}.mp3",
            f"temp_mean_{i}.mp3",
            f"temp_ex_en_{i}.mp3",
            f"temp_ex_ko_{i}.mp3"
        ]

        try:
            # 영어 파트는 영어 목소리로, 한국어 파트는 한국어 목소리로 생성
            await generate_speech(word, eng_voice, temp_files[0])
            await generate_speech(meanings, kor_voice, temp_files[1])
            await generate_speech(example_en, eng_voice, temp_files[2])
            await generate_speech(example_ko, kor_voice, temp_files[3])

            # 4개의 조각 파일을 하나의 자연스러운 MP3 파일로 이어붙이기
            with open(output_filename, 'wb') as outfile:
                for temp_file in temp_files:
                    with open(temp_file, 'rb') as infile:
                        outfile.write(infile.read())

            print(f"✅ 생성 완료 ({i}/{total_words}): {output_filename}")

        except Exception as e:
            print(f"❌ 오류 발생 ({word}): {e}")

        finally:
            # 임시 파일 깔끔하게 정리
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    print(f"\n🎉 모든 음성 파일이 '{output_dir}' 폴더에 저장되었습니다!")

if __name__ == "__main__":
    # 실행 시 인자값(Arguments) 확인 및 처리
    if len(sys.argv) < 2:
        print("💡 사용법: python json_to_audio.py <입력파일.json> [us/uk] [male/female]")
        print("💡 기본 실행 (미국/여성): python json_to_audio.py sample.json")
        print("💡 옵션 실행 (영국/남성): python json_to_audio.py sample.json uk male")
        sys.exit(1)
        
    input_json = sys.argv[1]
    
    # 옵션을 입력하지 않았을 경우의 기본값 설정
    accent = "us"
    gender = "female"
    
    if len(sys.argv) >= 3:
        accent = sys.argv[2].lower()
    if len(sys.argv) >= 4:
        gender = sys.argv[3].lower()

    if accent not in ["us", "uk"] or gender not in ["male", "female"]:
        print("❌ 오류: 억양은 'us' 또는 'uk', 성별은 'male' 또는 'female'만 입력 가능합니다.")
        sys.exit(1)

    # 비동기 함수 실행 (파이썬 기본 내장 라이브러리)
    asyncio.run(create_audio_files(input_json, accent, gender))