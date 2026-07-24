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

def create_single_card(label, content, font_path, output_filepath):
    """단일 카드 이미지를 일정한 글자 크기로 생성하고 저장합니다."""
    width, height = 1080, 1080
    bg_color = (245, 247, 250)
    card_color = (255, 255, 255)
    label_color = (59, 130, 246)
    text_color = (33, 37, 41)
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    padding = 60
    draw.rounded_rectangle(
        [(padding, padding), (width - padding, height - padding)],
        radius=40, fill=card_color, outline=(220, 224, 228), width=3
    )

    try:
        # 단어, 뜻, 예문 모두 80px로 크기 통일
        main_font_size = 80 
        font_main = ImageFont.truetype(font_path, main_font_size)
        font_label = ImageFont.truetype(font_path, 50)
    except IOError:
        print(f"❌ 폰트 파일을 찾을 수 없습니다: {font_path}")
        return False

    center_x = width // 2

    # 1. 상단 라벨
    bbox_label = draw.textbbox((0, 0), label, font=font_label)
    label_w = bbox_label[2] - bbox_label[0]
    draw.text((center_x - label_w // 2, 120), label, font=font_label, fill=label_color)

    # 2. 텍스트 줄바꿈
    max_text_width = width - (120 * 2) 
    lines = wrap_text_by_pixels(content, font_main, max_text_width, draw)

    # 3. Y좌표 중앙 정렬 계산
    line_spacing = 40
    total_text_height = sum([draw.textbbox((0, 0), line, font=font_main)[3] - draw.textbbox((0, 0), line, font=font_main)[1] for line in lines]) + (len(lines) - 1) * line_spacing
    current_y = (height - total_text_height) // 2

    # 4. 텍스트 그리기
    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=font_main)
        line_w = bbox_line[2] - bbox_line[0]
        line_h = bbox_line[3] - bbox_line[1]
        
        draw.text((center_x - line_w // 2, current_y), line, font=font_main, fill=text_color)
        current_y += line_h + line_spacing

    image.save(output_filepath)
    return True

def generate_exam_cards(word, meaning, eng_sentence, kor_sentence, output_dir: Path, prefix, font_path):
    """한 단어에 대한 4장의 카드를 생성합니다."""
    create_single_card("📝 Word (영단어)", word, font_path, output_dir / f"{prefix}_1_word.png")
    create_single_card("💡 Meaning (뜻)", meaning, font_path, output_dir / f"{prefix}_2_meaning.png")
    create_single_card("🗣️ Example (예문)", eng_sentence, font_path, output_dir / f"{prefix}_3_eng_sentence.png")
    create_single_card("🇰🇷 Translation (해석)", kor_sentence, font_path, output_dir / f"{prefix}_4_kor_sentence.png")

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
    OUTPUT_BASE_DIR = BASE_DIR / 'Card_Results'
    
    # 폰트 경로 설정 (Mac 기본 지원, 없으면 Windows 맑은고딕으로 자동 시도)
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
            print(f"총 {len(target_folders)}개의 대상 폴더를 찾았습니다. 카드 생성 작업을 시작합니다...\n")
            
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
                    # 파일명에 불법 문자가 들어가지 않도록 공백 등을 안전하게 처리
                    safe_word = "".join([c for c in item['word'] if c.isalpha() or c.isdigit() or c==' ']).strip().replace(' ', '_')
                    prefix = f"{index:03d}_{safe_word}"
                    
                    generate_exam_cards(
                        word=item['word'],
                        meaning=item['meaning'],
                        eng_sentence=item['eng_sent'],
                        kor_sentence=item['kor_sent'],
                        output_dir=folder_output_dir,
                        prefix=prefix,
                        font_path=FONT_PATH
                    )
                
                print(f"   -> ✅ {len(all_words)}개 단어 (총 {len(all_words) * 4}장) 카드 생성 완료.")

            print(f"\n🎉 모든 카드 생성이 완료되었습니다! 결과물은 '{OUTPUT_BASE_DIR.name}' 폴더를 확인하세요.")