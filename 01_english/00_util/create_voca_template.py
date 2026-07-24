import os
from pathlib import Path

def create_vocab_folders_and_files(base_directory: str):
    base_path = Path(base_directory)
    base_path.mkdir(parents=True, exist_ok=True)

    # 1. 마크다운 파일에 들어갈 단어장 템플릿(1~10번) 생성
    template_lines = ["# Vocabulary(English)\n"]
    for i in range(1, 11):
        template_lines.append(f"{i}.\n- \n- \n")
    template_content = "\n".join(template_lines)

    file_counter = 1  # 001 ~ 100까지 파일 번호를 카운트하기 위한 변수

    # 2. 총 10개의 폴더를 생성하는 반복문
    for folder_idx in range(1, 11):
        # 폴더 이름 생성 (예: 001-010, 011-020 ... 091-100)
        start_num = (folder_idx - 1) * 10 + 1
        end_num = folder_idx * 10
        folder_name = f"{start_num:03d}-{end_num:03d}"
        folder_path = base_path / folder_name
        
        # 폴더 생성
        folder_path.mkdir(exist_ok=True)
        
        # 3. 각 폴더 안에 10개의 마크다운 파일 생성
        for _ in range(10):
            file_name = f"{file_counter:03d}.md"
            file_path = folder_path / file_name
            
            # 템플릿 내용을 파일에 작성
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(template_content)
                
            file_counter += 1 # 파일 번호 1 증가
            
        print(f"[{folder_name}] 폴더에 10개의 마크다운 파일 생성 완료")

    print("\n모든 폴더 및 파일 생성이 완료되었습니다!")

# 실행 부분
if __name__ == "__main__":
    # 파일들이 생성될 최상위 폴더명 지정 (원하는 경로로 수정 가능)
    TARGET_DIR = './Vocabulary_Files'
    
    create_vocab_folders_and_files(TARGET_DIR)