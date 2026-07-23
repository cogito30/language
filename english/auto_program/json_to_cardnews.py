import json
import os
import sys
import textwrap
from PIL import Image, ImageDraw, ImageFont

def create_card_news(json_path, output_dir="card_news_output"):
    # 1. JSON 파일 읽기
    if not os.path.exists(json_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다. ({json_path})")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data.get("title", "English Vocabulary")
    vocabulary = data.get("vocabulary", [])
    total_cards = len(vocabulary)

    # 2. 결과물을 저장할 폴더 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3. macOS 기본 한글 폰트 설정 (AppleSDGothicNeo)
    # 폰트 경로가 다를 경우 시스템에 설치된 다른 ttf/ttc 파일 경로로 변경 가능합니다.
    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    
    try:
        font_word = ImageFont.truetype(font_path, 80)      # 단어용 (가장 큼)
        font_meaning = ImageFont.truetype(font_path, 50)   # 뜻용
        font_example_en = ImageFont.truetype(font_path, 40)# 영문 예문용
        font_example_ko = ImageFont.truetype(font_path, 35)# 한글 해석용
        font_counter = ImageFont.truetype(font_path, 30)   # 페이지 번호용
    except IOError:
        print("❌ 오류: macOS 기본 폰트를 찾을 수 없습니다. font_path를 확인해주세요.")
        return

    print(f"🚀 총 {total_cards}장의 카드 뉴스 생성을 시작합니다...")

    # 4. 단어별로 이미지(카드) 생성
    for i, item in enumerate(vocabulary, 1):
        word = item.get("word", "")
        meanings = ", ".join(item.get("meanings", []))
        example_en = item.get("example", "")
        example_ko = item.get("translation", "")

        # 배경 이미지 생성 (1080x1080 인스타그램 사이즈, 아주 연한 회색/파란색 톤)
        img = Image.new('RGB', (1080, 1080), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)

        # 텍스트가 길 경우 자동 줄바꿈 처리 (가로폭 기준)
        wrapped_en = textwrap.fill(example_en, width=45)
        wrapped_ko = textwrap.fill(example_ko, width=40)

        # ---------------- 중앙 정렬로 텍스트 그리기 ----------------
        # 1) 상단 페이지 번호 (예: 1 / 10)
        draw.text((540, 100), f"{i} / {total_cards}", font=font_counter, fill=(150, 150, 150), anchor="mm")

        # 2) 메인 영단어
        draw.text((540, 350), word, font=font_word, fill=(41, 128, 185), anchor="mm")

        # 3) 한글 뜻
        draw.text((540, 480), meanings, font=font_meaning, fill=(231, 76, 60), anchor="mm")

        # 4) 구분선
        draw.line([(340, 600), (740, 600)], fill=(200, 200, 200), width=3)

        # 5) 영문 예문
        draw.text((540, 700), f"\"{wrapped_en}\"", font=font_example_en, fill=(44, 62, 80), anchor="mm", align="center")

        # 6) 한글 해석
        # 영문 예문이 몇 줄인지에 따라 한글 해석의 Y축 위치를 동적으로 살짝 내림
        line_count = len(wrapped_en.split('\n'))
        ko_y_pos = 780 + (line_count - 1) * 50
        draw.text((540, ko_y_pos), wrapped_ko, font=font_example_ko, fill=(127, 140, 141), anchor="mm", align="center")
        # -------------------------------------------------------------

        # 이미지 파일로 저장 (예: card_01.png, card_02.png)
        output_filename = os.path.join(output_dir, f"card_{i:02d}.png")
        img.save(output_filename)
        print(f"✅ 생성 완료: {output_filename}")

    print(f"\n🎉 모든 카드 뉴스가 '{output_dir}' 폴더에 저장되었습니다!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("💡 사용법: python json_to_cardnews.py <입력파일.json>")
        sys.exit(1)
        
    input_json = sys.argv[1]
    create_card_news(input_json)