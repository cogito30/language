import json
import os
import sys
import re

def parse_text(text):
    """
    정해진 영어 단어장 템플릿 규칙에 따라 텍스트를 파싱하여 딕셔너리로 반환합니다.
    """
    parsed_data = {
        "title": "",
        "vocabulary": []
    }
    
    current_word = {}
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. 제목 파싱 ( '#' 으로 시작하는 줄 )
        if line.startswith('#'):
            parsed_data["title"] = line.lstrip('#').strip()
            continue
            
        # 2. 단어와 뜻 파싱 ( '숫자. 단어: 뜻' 형태 )
        word_match = re.match(r'^\d+\.\s*([^:]+):\s*(.*)$', line)
        if word_match:
            # 새로운 단어가 시작되기 전, 이전에 파싱하던 단어 데이터를 리스트에 저장
            if current_word:
                parsed_data["vocabulary"].append(current_word)
                
            word = word_match.group(1).strip()
            # 쉼표(,)가 있을 경우 여러 뜻으로 분리, 없으면 하나의 뜻으로 리스트화
            meanings = [m.strip() for m in word_match.group(2).split(',')]
            
            current_word = {
                "word": word,
                "meanings": meanings,
                "example": "",
                "translation": ""
            }
            continue
            
        # 3. 예문과 해석 파싱 ( '-' 으로 시작하는 줄 )
        if line.startswith('*') and current_word:
            content = line.lstrip('*').strip()
            
            # 예문이 비어있다면 영문 예문에 먼저 채우고, 채워져 있다면 한글 해석에 채움
            if not current_word["example"]:
                current_word["example"] = content
            elif not current_word["translation"]:
                current_word["translation"] = content
                
    # 마지막으로 작업 중이던 단어 데이터 리스트에 추가
    if current_word:
        parsed_data["vocabulary"].append(current_word)
        
    return parsed_data

def process_file(input_path):
    """단일 파일을 읽어서 JSON으로 변환하고 저장합니다."""
    
    base_name, ext = os.path.splitext(input_path)
    
    if ext.lower() not in ['.txt', '.md']:
        print(f"⚠️ 건너뜀: '{input_path}' (.txt 또는 .md 파일만 지원)")
        return

    output_path = f"{base_name}.json"

    if not os.path.exists(input_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다. ('{input_path}')")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        print(f"❌ 파일 읽기 오류 ('{input_path}'): {e}")
        return

    json_data = parse_text(raw_text)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 성공: '{input_path}' ➔ '{output_path}'")
    except Exception as e:
        print(f"❌ 파일 저장 오류 ('{output_path}'): {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("💡 사용법: python converter.py <파일1.txt> <파일2.md> ...")
        print("💡 예시 (폴더 내 모든 txt 변환): python converter.py *.txt")
        sys.exit(1)
        
    input_files = sys.argv[1:]
    
    print(f"🚀 총 {len(input_files)}개의 파일 변환을 시작합니다...\n")
    
    for file_path in input_files:
        process_file(file_path)
        
    print("\n🎉 모든 작업이 완료되었습니다!")