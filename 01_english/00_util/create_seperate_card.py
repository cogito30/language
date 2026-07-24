import os
from PIL import Image, ImageDraw, ImageFont

def wrap_text_by_pixels(text, font, max_width, draw):
    """
    글자 수가 아닌 '픽셀 너비'를 기준으로 정확하게 줄바꿈을 수행합니다.
    """
    lines = []
    # 이미 줄바꿈이 있는 경우를 대비해 먼저 나눔
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        current_line = []
        
        for word in words:
            # 현재 줄에 단어를 추가했을 때의 너비 테스트
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                # 단어 하나가 너무 길어서 max_width를 넘는 예외 처리
                if not current_line:
                    lines.append(word)
                    current_line = []
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    
        if current_line:
            lines.append(' '.join(current_line))
            
    return lines

def create_single_card(label, content, font_path, output_filename, is_sentence=False):
    width, height = 1080, 1080
    bg_color = (245, 247, 250)
    card_color = (255, 255, 255)
    
    label_color = (59, 130, 246)
    text_color = (33, 37, 41)
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 테두리가 있는 안쪽 카드 박스 (여백 60)
    padding = 60
    draw.rounded_rectangle(
        [(padding, padding), (width - padding, height - padding)],
        radius=40, fill=card_color, outline=(220, 224, 228), width=3
    )

    try:
        # 문장은 너무 크지 않게 60, 단어/뜻은 120으로 설정
        main_font_size = 60 if is_sentence else 120
        font_main = ImageFont.truetype(font_path, main_font_size)
        font_label = ImageFont.truetype(font_path, 50)
    except IOError:
        print("❌ 폰트 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    center_x = width // 2

    # 1. 상단 라벨 그리기
    bbox_label = draw.textbbox((0, 0), label, font=font_label)
    label_w = bbox_label[2] - bbox_label[0]
    draw.text((center_x - label_w // 2, 120), label, font=font_label, fill=label_color)

    # 2. 픽셀 기반 완벽 줄바꿈 적용
    # 카드의 좌우 여백을 충분히 주어 글자가 밖으로 나가지 않게 함 (양옆 120px 여백)
    max_text_width = width - (120 * 2) 
    
    lines = wrap_text_by_pixels(content, font_main, max_text_width, draw)

    # 3. 중앙 정렬을 위한 전체 텍스트 높이 계산
    line_spacing = 40  # 줄 간격
    total_text_height = sum([draw.textbbox((0, 0), line, font=font_main)[3] - draw.textbbox((0, 0), line, font=font_main)[1] for line in lines]) + (len(lines) - 1) * line_spacing
    
    # 텍스트가 시작될 Y 좌표 (정중앙)
    current_y = (height - total_text_height) // 2

    # 4. 계산된 위치에 한 줄씩 가운데 정렬로 그리기
    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=font_main)
        line_w = bbox_line[2] - bbox_line[0]
        line_h = bbox_line[3] - bbox_line[1]
        
        draw.text((center_x - line_w // 2, current_y), line, font=font_main, fill=text_color)
        current_y += line_h + line_spacing

    # 결과 저장
    image.save(output_filename)
    print(f"✅ 생성 완료: {output_filename}")


def generate_exam_cards(word, meaning, eng_sentence, kor_sentence, prefix="001"):
    # Mac 기본 폰트
    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    
    create_single_card("📝 Word (영단어)", word, font_path, f"{prefix}_1_word.png")
    create_single_card("💡 Meaning (뜻)", meaning, font_path, f"{prefix}_2_meaning.png")
    create_single_card("🗣️ Example (예문)", eng_sentence, font_path, f"{prefix}_3_eng_sentence.png", is_sentence=True)
    create_single_card("🇰🇷 Translation (해석)", kor_sentence, font_path, f"{prefix}_4_kor_sentence.png", is_sentence=True)

# 실행 부분
if __name__ == "__main__":
    # 긴 문장으로 테스트해도 이제 밖으로 나가지 않습니다.
    word = "Procrastination"
    meaning = "미루는 버릇, 지연"
    eng_sentence = "Procrastination is often caused by anxiety about failing to complete a task perfectly."
    kor_sentence = "일을 완벽하게 해내지 못할 것이라는 불안감 때문에 미루는 버릇이 자주 발생하곤 합니다."
    
    print("단어 시험용 분리형 카드 뉴스 생성을 시작합니다...\n")
    generate_exam_cards(word, meaning, eng_sentence, kor_sentence, prefix="CardTest_01")
    print("\n🎉 모든 카드 생성 완료!")