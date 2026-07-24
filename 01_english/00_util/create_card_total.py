import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def wrap_text_by_pixels(text, font, max_width, draw):
    """글자 수가 아닌 '픽셀 너비'를 기준으로 정확하게 줄바꿈을 수행합니다."""
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if not current_line:
                    lines.append(word)
                    current_line = []
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    
        if current_line:
            lines.append(' '.join(current_line))
            
    return lines

def create_combined_card(word, meaning, eng_sentence, kor_sentence, font_path, output_filepath):
    """한 장의 카드에 단어, 뜻, 예문, 해석을 모두 배치하여 생성합니다."""
    # 1. 카드 뉴스 사이즈 및 색상
    width, height = 1080, 1080
    bg_color = (245, 247, 250)      
    card_color = (255, 255, 255)    
    primary_text = (33, 37, 41)     
    accent_color = (59, 130, 246)   
    secondary_text = (107, 114, 128) 

    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 테두리가 있는 안쪽 카드 박스
    padding = 60
    draw.rounded_rectangle(
        [(padding, padding), (width - padding, height - padding)],
        radius=40, fill=card_color, outline=(220, 224, 228), width=3
    )
    
    try:
        font_word = ImageFont.truetype(font_path, 100)       # 영단어
        font_meaning = ImageFont.truetype(font_path, 65)     # 뜻
        font_eng = ImageFont.truetype(font_path, 45)         # 영어 예문
        font_kor = ImageFont.truetype(font_path, 40)         # 한글 해석
    except IOError:
        print(f"❌ 폰트 파일을 찾을 수 없습니다: {font_path}")
        return False

    center_x = width // 2
    current_y = 180  # 시작 Y 좌표

    # [섹션 1] 단어
    bbox_word = draw.textbbox((0, 0), word, font=font_word)
    word_w = bbox_word[2] - bbox_word[0]
    draw.text((center_x - word_w // 2, current_y), word, font=font_word, fill=primary_text)
    current_y += 140

    # [섹션 2] 뜻
    bbox_meaning = draw.textbbox((0, 0), meaning, font=font_meaning)
    meaning_w = bbox_meaning[2] - bbox_meaning[0]
    draw.text((center_x - meaning_w // 2, current_y), meaning, font=font_meaning, fill=accent_color)
    current_y += 180

    # [구분선]
    line_padding = 150
    draw.line([(line_padding, current_y), (width - line_padding, current_y)], fill=(229, 231, 235), width=3)
    current_y += 100

    max_text_width = width - (150 * 2) # 양옆 150px 여백

    # [섹션 3] 영어 예문 (픽셀 기반 자동 줄바꿈)
    eng_lines = wrap_text_by_pixels(eng_sentence, font_eng, max_text_width, draw)
    for line in eng_lines:
        bbox_eng = draw.textbbox((0, 0), line, font=font_eng)
        eng_w = bbox_eng[2] - bbox_eng[0]
        draw.text((center_x - eng_w // 2, current_y), line, font=font_eng, fill=primary_text)
        current_y += 60
    
    current_y += 50 # 영어와 한글 사이 간격

    # [섹션 4] 한글 해석 (픽셀 기반 자동 줄바꿈)
    kor_lines = wrap_text_by_pixels(kor_sentence, font_kor, max_text_width, draw)
    for line in kor_lines:
        bbox_kor = draw.textbbox((0, 0), line, font=font_kor)
        kor_w = bbox_kor[2] - bbox_kor[0]
        draw.text((center_x - kor_w // 2, current_y), line, font=font_kor, fill=secondary_text)
        current_y += 55

    image.save(output_filepath)
    return True

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
    OUTPUT_BASE_DIR = BASE_DIR / 'Card_Total_Results'
    
    # 폰트 경로 설정
    FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    if not os.path.exists(FONT_PATH):
        FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
    else:
        OUTPUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
        folder_pattern = re.compile(r'^\d{3}-\d{3}$')
        target_folders = [p for p in INPUT_DIR.iterdir() if p.is_dir() and folder_pattern.match(p.name)]
        
        if not target_folders:
            print(f"⚠️ '{INPUT_DIR.name}' 폴더 안에 '001-010' 형식의 폴더를 찾을 수 없습니다.")
        else:
            print(f"총 {len(target_folders)}개의 대상 폴더를 찾았습니다. 통합 카드 생성 작업을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                folder_output_dir = OUTPUT_BASE_DIR / folder.name
                folder_output_dir.mkdir(parents=True, exist_ok=True)
                
                print(f"📂 [{folder.name}] 처리 중...")
                
                all_words = []
                for md_file in folder.rglob("*.md"):
                    if "Quiz" in md_file.name or "Answer" in md_file.name:
                        continue
                    all_words.extend(extract_words_from_md(md_file))
                
                if not all_words:
                    print(f"   -> 단어를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                for index, item in enumerate(all_words, 1):
                    # 파일명 안전 처리
                    safe_word = "".join([c for c in item['word'] if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')
                    # 이번엔 한 장으로 합쳐지므로 뒤에 _card 만 붙입니다.
                    output_file = folder_output_dir / f"{index:03d}_{safe_word}_card.png"
                    
                    create_combined_card(
                        word=item['word'],
                        meaning=item['meaning'],
                        eng_sentence=item['eng_sent'],
                        kor_sentence=item['kor_sent'],
                        font_path=FONT_PATH,
                        output_filepath=output_file
                    )
                
                print(f"   -> ✅ {len(all_words)}개 단어 (총 {len(all_words)}장) 통합 카드 생성 완료.")

            print(f"\n🎉 모든 작업이 완료되었습니다! 결과물은 '{OUTPUT_BASE_DIR.name}' 폴더를 확인하세요.")