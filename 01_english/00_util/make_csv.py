import os
import re
import csv
from pathlib import Path

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

def write_to_csv(vocab_list, output_filepath):
    """추출된 단어 리스트를 CSV 파일로 저장합니다."""
    # utf-8-sig를 사용하여 엑셀에서 열었을 때 한글이 깨지지 않도록 합니다.
    with open(output_filepath, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # 첫 줄(헤더) 작성: Anki나 Quizlet 가져오기 시 매핑하기 좋습니다.
        writer.writerow(['Word', 'Meaning', 'English Sentence', 'Korean Sentence'])
        
        # 데이터 작성
        for item in vocab_list:
            writer.writerow([
                item['word'], 
                item['meaning'], 
                item['eng_sent'], 
                item['kor_sent']
            ])

# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.')
    INPUT_DIR = BASE_DIR / 'input'
    CSV_DIR = BASE_DIR / 'CSV_Results'
    
    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
    else:
        CSV_DIR.mkdir(parents=True, exist_ok=True)
        folder_pattern = re.compile(r'^\d{3}-\d{3}$')
        target_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and folder_pattern.match(p.name)]
        
        if not target_folders:
            print(f"⚠️ '{INPUT_DIR.name}' 폴더 안에 '001-010' 형식의 폴더를 찾을 수 없습니다.")
        else:
            print(f"📊 총 {len(target_folders)}개의 폴더에서 플래시카드용 CSV 추출을 시작합니다...\n")
            
            all_master_words = [] # 전체 단어를 모을 리스트
            
            for folder in sorted(target_folders):
                folder_name = folder.name
                print(f"📂 [{folder_name}] 데이터 추출 중...")
                
                folder_words = []
                for md_file in folder.rglob("*.md"):
                    if "Quiz" in md_file.name or "Answer" in md_file.name:
                        continue
                    folder_words.extend(extract_words_from_md(md_file))
                
                if not folder_words:
                    print("   -> 단어를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                # 1. 개별 폴더 단위 CSV 저장 (예: 001-010_Deck.csv)
                folder_csv_path = CSV_DIR / f"{folder_name}_Deck.csv"
                write_to_csv(folder_words, folder_csv_path)
                
                all_master_words.extend(folder_words)
                print(f"   -> ✅ {len(folder_words)}개 단어 추출 완료: {folder_csv_path.name}")
            
            # 2. 전체 단어를 하나로 묶은 마스터 CSV 저장 (통합 복습용)
            if all_master_words:
                master_csv_path = CSV_DIR / "Master_Deck_All.csv"
                write_to_csv(all_master_words, master_csv_path)
                print(f"\n🌟 총 {len(all_master_words)}개의 전체 단어가 포함된 마스터 덱이 생성되었습니다: {master_csv_path.name}")

            print(f"\n🎉 모든 작업이 완료되었습니다! 파일은 '{CSV_DIR.name}' 폴더를 확인하세요.")