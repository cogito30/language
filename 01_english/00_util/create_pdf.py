import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_a4_page(page_cards, title, font_path):
    """4장의 카드 이미지를 A4 사이즈(300dpi) 한 장에 배치합니다."""
    # A4 사이즈 (300 DPI 기준: 2480 x 3508 픽셀)
    a4_width, a4_height = 2480, 3508
    page = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))
    draw = ImageDraw.Draw(page)

    # 폰트 설정 (타이틀용)
    try:
        font = ImageFont.truetype(font_path, 100)
    except IOError:
        font = ImageFont.load_default()

    # 상단에 폴더명(타이틀) 적기
    bbox = draw.textbbox((0, 0), f"{title} - Vocabulary Workbook", font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((a4_width - text_w) // 2, 250), f"{title} - Vocabulary Workbook", font=font, fill=(33, 37, 41))
    draw.line([(200, 400), (a4_width - 200, 400)], fill=(220, 224, 228), width=5)

    # 2x2 그리드 좌표 계산
    card_size = 1080
    x_margin = (a4_width - (card_size * 2)) // 3  # 약 106px
    y_spacing = 150
    
    # 세로 중앙 정렬을 위한 시작점
    total_grid_height = (card_size * 2) + y_spacing
    y_start = 400 + (a4_height - 400 - total_grid_height) // 2

    positions = [
        (x_margin, y_start),                                      # 좌상단
        (x_margin * 2 + card_size, y_start),                      # 우상단
        (x_margin, y_start + card_size + y_spacing),              # 좌하단
        (x_margin * 2 + card_size, y_start + card_size + y_spacing) # 우하단
    ]

    # 카드 이미지를 A4 용지에 붙여넣기
    for idx, card_path in enumerate(page_cards):
        try:
            with Image.open(card_path) as card_img:
                page.paste(card_img, positions[idx])
        except Exception as e:
            print(f"⚠️ 이미지 삽입 실패 ({card_path.name}): {e}")

    return page

# ==========================================
# 실행 부분
# ==========================================
if __name__ == "__main__":
    BASE_DIR = Path('.')
    CARD_DIR = BASE_DIR / 'Card_Results'
    PDF_DIR = BASE_DIR / 'PDF_Results'
    
    # Mac / Windows 기본 폰트 설정
    FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    if not os.path.exists(FONT_PATH):
        FONT_PATH = "C:/Windows/Fonts/malgun.ttf"

    if not CARD_DIR.exists() or not CARD_DIR.is_dir():
        print("⚠️ 'Card_Results' 폴더를 찾을 수 없습니다. 먼저 카드뉴스를 생성해 주세요.")
    else:
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        target_folders = [p for p in CARD_DIR.iterdir() if p.is_dir()]
        
        if not target_folders:
            print("⚠️ 'Card_Results' 폴더 안에 처리할 이미지가 없습니다.")
        else:
            print(f"📄 총 {len(target_folders)}개의 폴더에서 PDF 워크북 제작을 시작합니다...\n")
            
            for folder in sorted(target_folders):
                folder_name = folder.name
                print(f"📂 [{folder_name}] PDF 병합 중...")
                
                # 병합할 통합 카드 이미지(_card.png)만 수집 후 정렬
                card_files = sorted(list(folder.glob("*_card.png")))
                
                if not card_files:
                    print("   -> 통합 카드 이미지를 찾지 못했습니다. 건너뜁니다.")
                    continue
                
                # 4장씩 끊어서 페이지 리스트 생성
                pages = []
                for i in range(0, len(card_files), 4):
                    chunk = card_files[i:i+4]
                    a4_page = create_a4_page(chunk, folder_name, FONT_PATH)
                    pages.append(a4_page)
                
                # 생성된 페이지들을 하나의 PDF 파일로 묶어서 저장
                if pages:
                    output_pdf = PDF_DIR / f"{folder_name}_Workbook.pdf"
                    pages[0].save(
                        output_pdf, 
                        "PDF", 
                        resolution=300.0, 
                        save_all=True, 
                        append_images=pages[1:]
                    )
                    print(f"   -> ✅ 총 {len(card_files)}단어, {len(pages)}페이지 분량의 PDF 생성 완료.")
                    
            print(f"\n🎉 워크북 생성이 완료되었습니다! 파일은 '{PDF_DIR.name}' 폴더를 확인하세요.")