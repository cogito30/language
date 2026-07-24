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

def generate_all_words_quiz(base_directory: str):
    base_path = Path(base_directory)
    vocab_list = []

    # 1. 모든 하위 폴더의 .md 파일에서 데이터 모두 추출
    for file_path in base_path.rglob("*.md"):
        # 시험지와 정답지 파일 자체는 파싱 대상에서 제외
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
        print("입력된 단어가 없습니다.")
        return

    print(f"✅ 총 {len(vocab_list)}개의 단어를 찾았습니다. 모든 단어에 대해 4가지 유형의 문제를 생성합니다.\n")

    # 2. 각 파트별로 모든 단어를 넣되, 순서를 랜덤하게 섞음
    part1_words = random.sample(vocab_list, len(vocab_list))
    part2_words = random.sample(vocab_list, len(vocab_list))
    part3_words = random.sample(vocab_list, len(vocab_list))
    part4_words = random.sample(vocab_list, len(vocab_list))

    quiz_file = base_path / "Master_Quiz.md"
    answer_file = base_path / "Master_Answer.md"

    # 3. 시험지 작성
    with open(quiz_file, "w", encoding="utf-8") as qf:
        qf.write("# 📝 Master English Quiz (All Words)\n\n")
        
        # 유형 1
        qf.write("## Part 1. 단어 뜻 맞추기\n")
        for i, item in enumerate(part1_words, 1):
            if i % 2 == 1:
                qf.write(f"{i}. **{item['word']}** : ____________________\n")
            else:
                qf.write(f"{i}. **{item['meaning']}** : ____________________\n")

        # 유형 2
        qf.write("\n## Part 2. 문장 빈칸 채우기\n")
        for i, item in enumerate(part2_words, 1):
            blanked = make_blank(item['eng_sent'], item['word'])
            qf.write(f"{i}. {item['kor_sent']}\n   -> {blanked}\n\n")

        # 유형 3
        qf.write("## Part 3. 문장 영작하기\n")
        for i, item in enumerate(part3_words, 1):
            qf.write(f"{i}. {item['kor_sent']} (단어: {item['word']})\n   -> ________________________________________\n\n")

        # 유형 4
        qf.write("## Part 4. 문장 해석하기\n")
        for i, item in enumerate(part4_words, 1):
            qf.write(f"{i}. {item['eng_sent']}\n   -> ________________________________________\n\n")

    # 4. 정답지 작성
    with open(answer_file, "w", encoding="utf-8") as af:
        af.write("# ✅ Master Answer Key\n\n")
        
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

    return quiz_file, answer_file

# ==========================================
# 실행 부분 (테스트 데이터 생성 포함)
# ==========================================
if __name__ == "__main__":
    TARGET_DIR = './Test_Vocabulary'
    Path(TARGET_DIR).mkdir(parents=True, exist_ok=False)
    
#     # 3개의 단어만 샘플로 생성하여 모든 단어가 4개 파트에 전부 나오는지 테스트
#     sample_data = """# Vocabulary(English)
# 1. Apple: 사과
# - I eat an apple.
# - 나는 사과를 먹는다.
# 2. Water: 물
# - Drink water.
# - 물을 마셔라.
# 3. Book: 책
# - Read a book.
# - 책을 읽어라.
# """
#     with open(Path(TARGET_DIR) / "001.md", "w", encoding="utf-8") as f:
#         f.write(sample_data)
        
    quiz_file, answer_file = generate_all_words_quiz(TARGET_DIR)
    
    # 생성된 시험지 결과 콘솔에 출력 (확인용)
    with open(quiz_file, "r", encoding="utf-8") as q:
        print(q.read())