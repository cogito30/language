import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

def create_card_news(word, meaning, eng_sentence, kor_sentence, output_filename="card_news.png"):
    # 1. 카드 뉴스 사이즈 (인스타그램 표준 정방형 1080x1080)
    width, height = 1080, 1080
    
    # 2. 색상 테마 설정
    bg_color = (245, 247, 250)      # 부드러운 배경색 (연한 회색/파랑 톤)
    card_color = (255, 255, 255)    # 카드 자체의 색상 (흰색)
    primary_text = (33, 37, 41)     # 메인 텍스트 (진한 흑회색)
    accent_color = (59, 130, 246)   # 포인트 색상 (파란색)
    secondary_text = (107, 114, 128) # 보조 텍스트 (중간 회색)

    # 3. 바탕 캔버스 생성 및 하얀색 카드 영역 그리기
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # 테두리가 있는 안쪽 카드 박스 (여백 60px)
    padding = 60
    draw.rounded_rectangle(
        [(padding, padding), (width - padding, height - padding)],
        radius=40, fill=card_color, outline=(220, 224, 228), width=3
    )

    # 4. Mac 기본 한글 폰트 설정
    # Mac 환경의 기본 고딕 폰트 경로입니다.
    font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    
    try:
        font_word = ImageFont.truetype(font_path, 100)       # 영단어 (아주 크게)
        font_meaning = ImageFont.truetype(font_path, 65)     # 뜻 (크게)
        font_eng = ImageFont.truetype(font_path, 45)         # 영어 예문 (중간)
        font_kor = ImageFont.truetype(font_path, 40)         # 한글 해석 (조금 작게)
    except IOError:
        print("❌ 폰트 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    # 5. 텍스트 배치 좌표 설정
    center_x = width // 2
    current_y = 180  # 시작 Y 좌표

    # [섹션 1] 단어
    # 단어 가운데 정렬을 위해 텍스트 길이 계산 (Pillow 최신 버전 방식)
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

    # [섹션 3] 영어 예문 (자동 줄바꿈 적용)
    # 한 줄에 들어갈 글자 수 설정 (대략 40자)
    wrapped_eng = textwrap.fill(eng_sentence, width=40)
    
    for line in wrapped_eng.split('\n'):
        bbox_eng = draw.textbbox((0, 0), line, font=font_eng)
        eng_w = bbox_eng[2] - bbox_eng[0]
        draw.text((center_x - eng_w // 2, current_y), line, font=font_eng, fill=primary_text)
        current_y += 60  # 줄간격
    
    current_y += 50 # 영어와 한글 사이 간격

    # [섹션 4] 한글 해석 (자동 줄바꿈 적용)
    wrapped_kor = textwrap.fill(kor_sentence, width=35)
    
    for line in wrapped_kor.split('\n'):
        bbox_kor = draw.textbbox((0, 0), line, font=font_kor)
        kor_w = bbox_kor[2] - bbox_kor[0]
        draw.text((center_x - kor_w // 2, current_y), line, font=font_kor, fill=secondary_text)
        current_y += 55

    # 6. 결과 저장
    image.save(output_filename)
    print(f"✅ 카드 뉴스 '{output_filename}' 생성 완료!")

# 실행 부분
if __name__ == "__main__":
    # 이전에 만든 마크다운 데이터 형식을 그대로 활용합니다.
    word = "Apple"
    meaning = "사과"
    eng_sentence = "I eat an apple every morning to stay healthy."
    kor_sentence = "나는 건강을 유지하기 위해 매일 아침 사과를 먹는다."
    
    create_card_news(word, meaning, eng_sentence, kor_sentence, output_filename="001_Apple_card.png")