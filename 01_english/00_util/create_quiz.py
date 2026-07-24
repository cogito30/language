import os
import random
import re
from pathlib import Path

def make_blank(sentence: str, word: str) -> str:
    """예문에서 타겟 단어를 찾아 밑줄로 변경합니다."""
    pattern = re.compile(re.escape(word), re.IGNORECASE)
    if not pattern.search(sentence):
        return sentence + f" (힌트: {word} 가 포함된 문장)"
    return pattern.sub("________", sentence)

def generate_quiz_for_folder(input_dir: Path, output_dir: Path):
    """특정 폴더의 md 파일을 읽어 퀴즈와 정답지를 결과 폴더에 생성합니다."""
    vocab_list = []
    folder_name = input_dir.name

    # 1. 대상 폴더의 모든 .md 파일에서 데이터 추출
    for file_path in input_dir.rglob("*.md"):
        # 기존 시험지/정답지가 섞여 있다면 제외
        if "Quiz" in file_path.name or "Answer" in file_path.name:
            continue
            
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
                    
        # 파일의 마지막 항목 추가
        if 'word' in current_item and 'eng_sent' in current_item and 'kor_sent' in current_item:
            vocab_list.append(current_item)

    if not vocab_list:
        print(f"⚠️ [{folder_name}] 폴더에 단어 데이터가 없거나 형식이 맞지 않습니다.")
        return

    print(f"✅ [{folder_name}] 총 {len(vocab_list)}개의 단어 추출 완료. 퀴즈 생성 중...")

    # 2. 각 파트별로 모든 단어를 넣되, 순서를 랜덤하게 섞음
    part1_words = random.sample(vocab_list, len(vocab_list))
    part2_words = random.sample(vocab_list, len(vocab_list))
    part3_words = random.sample(vocab_list, len(vocab_list))
    part4_words = random.sample(vocab_list, len(vocab_list))

    # 결과물 파일 이름 설정 (폴더명_Quiz.md 형태)
    quiz_file = output_dir / f"{folder_name}_Quiz.md"
    answer_file = output_dir / f"{folder_name}_Answer.md"

    # 3. 시험지 작성
    with open(quiz_file, "w", encoding="utf-8") as qf:
        qf.write(f"# 📝 Master English Quiz - {folder_name}\n\n")
        
        qf.write("## Part 1. 단어 뜻 맞추기\n")
        for i, item in enumerate(part1_words, 1):
            if i % 2 == 1:
                qf.write(f"{i}. **{item['word']}** : ____________________\n")
            else:
                qf.write(f"{i}. **{item['meaning']}** : ____________________\n")

        qf.write("\n## Part 2. 문장 빈칸 채우기\n")
        for i, item in enumerate(part2_words, 1):
            blanked = make_blank(item['eng_sent'], item['word'])
            qf.write(f"{i}. {item['kor_sent']}\n   -> {blanked}\n\n")

        qf.write("## Part 3. 문장 영작하기\n")
        for i, item in enumerate(part3_words, 1):
            qf.write(f"{i}. {item['kor_sent']} (단어: {item['word']})\n   -> ________________________________________\n\n")

        qf.write("## Part 4. 문장 해석하기\n")
        for i, item in enumerate(part4_words, 1):
            qf.write(f"{i}. {item['eng_sent']}\n   -> ________________________________________\n\n")

    # 4. 정답지 작성
    with open(answer_file, "w", encoding="utf-8") as af:
        af.write(f"# ✅ Master Answer Key - {folder_name}\n\n")
        
        af.write("## Part 1 정답\n")
        for i, item in enumerate(part1_words, 1):
            af.write(f"{i}. {item['word']} <=> {item['meaning']}\n")
            
        af.write("\n## Part 2 정답 (빈칸 단어)\n")
        for i, item in enumerate(part2_words, 1):
            af.write(f"{i}. **{item['word']}** ({item['eng_sent']})\n")
            
        af.write("\n## Part 3 정답 (영작)\n")
        for i, item in enumerate(part3_words, 1):
            af.write(f"{i}. **{item['eng_sent']}**\n")
            
        af.write("\n## Part 4 정답 (해석)\n")
        for i, item in enumerate(part4_words, 1):
            af.write(f"{i}. **{item['kor_sent']}**\n")

    print(f"   -> 생성 완료: {quiz_file.name}, {answer_file.name}")


# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.') # 현재 스크립트가 실행되는 디렉토리
    INPUT_DIR = BASE_DIR / 'input' # 타겟 폴더들이 있는 input 폴더
    OUTPUT_DIR = BASE_DIR / 'Quiz_Results' # 결과를 모아둘 새 폴더명
    
    # 1. input 폴더 존재 여부 확인
    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
        print("파이썬 스크립트가 위치한 곳에 'input' 폴더를 만들고 그 안에 '001-010' 등의 폴더를 넣어주세요.")
    else:
        # 2. 결과물을 저장할 폴더 생성
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # 3. 폴더 이름이 '001-010', '011-020'처럼 숫자 3자리-숫자 3자리 패턴인지 확인하는 정규식
        folder_pattern = re.compile(r'^\d{3}-\d{3}$')
        
        # input 디렉토리 내에서 패턴에 맞는 폴더들만 리스트로 수집
        target_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and folder_pattern.match(p.name)]
        
        if not target_folders:
            print(f"⚠️ '{INPUT_DIR.name}' 폴더 안에 '001-010', '011-020' 형식의 폴더를 찾을 수 없습니다.")
        else:
            print(f"총 {len(target_folders)}개의 대상 폴더를 찾았습니다. 작업을 시작합니다...\n")
            
            # 찾은 폴더들을 이름순으로 정렬하여 차례대로 퀴즈 생성
            for folder in sorted(target_folders):
                generate_quiz_for_folder(folder, OUTPUT_DIR)
                
            print(f"\n🎉 모든 작업이 완료되었습니다! 결과물은 '{OUTPUT_DIR.name}' 폴더를 확인하세요.")