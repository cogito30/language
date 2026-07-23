import os
import sys
import asyncio
import json

# process_file 대신 텍스트 변환 핵심 엔진인 'parse_text'만 가져옵니다.
from converter import parse_text
from json_to_pdf import generate_pdf_from_json
from json_to_cardnews import create_card_news
from json_to_audio import create_audio_files
from json_to_video import create_lesson_video

async def run_auto_studio(input_txt_path):
    """단일 파일에 대해 전체 파이프라인을 실행하는 함수"""
    
    # 원본 파일의 경로와 이름 추출
    base_dir = os.path.dirname(os.path.abspath(input_txt_path))
    base_name = os.path.splitext(os.path.basename(input_txt_path))[0]
    
    # 해당 원고 전용 결과물 폴더 생성
    output_folder = os.path.join(base_dir, f"{base_name}_output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 생성될 결과물들의 경로를 새로 만든 폴더 내부로 지정
    json_path = os.path.join(output_folder, f"{base_name}.json")
    pdf_path = os.path.join(output_folder, f"{base_name}_study_material.pdf")
    video_path = os.path.join(output_folder, f"{base_name}_lesson_video.mp4")
    
    img_dir = os.path.join(output_folder, "cards")
    aud_dir = os.path.join(output_folder, "audios")

    print(f"  [1/5] 📄 JSON 데이터로 변환 중... ({json_path})")
    
    # ---------------------------------------------------------
    # [수정된 부분] 
    # 파일을 직접 읽어 parse_text()로 파싱한 뒤, 명확하게 새 폴더 경로에 저장합니다.
    try:
        with open(input_txt_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        data = parse_text(raw_text)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"  ❌ 파일 읽기/쓰기 오류: {e}")
        return
    # ---------------------------------------------------------

    if not os.path.exists(json_path):
        print("  ❌ JSON 파일 생성에 실패하여 이후 작업을 중단합니다.")
        return

    print(f"  [2/5] 📝 인쇄용 PDF 생성 중... ({pdf_path})")
    generate_pdf_from_json(json_path, pdf_path)

    print(f"  [3/5] 🎨 카드 뉴스 이미지 생성 중... ({img_dir}/)")
    create_card_news(json_path, output_dir=img_dir)

    print(f"  [4/5] 🎧 음성 파일 생성 중... ({aud_dir}/)")
    await create_audio_files(json_path, accent="us", gender="female", output_dir=aud_dir)

    print(f"  [5/5] 🎬 최종 동영상 합성 중... ({video_path})")
    create_lesson_video(json_path, img_dir=img_dir, aud_dir=aud_dir, output_path=video_path)

    print(f"  ✨ '{input_txt_path}'의 모든 콘텐츠가 '{output_folder}' 폴더에 생성 완료되었습니다!\n")

async def main():
    """입력받은 경로나 파일들을 분석하여 파이프라인을 가동하는 메인 함수"""
    args = sys.argv[1:]
    target_files = []

    for arg in args:
        if os.path.isdir(arg):
            for file_name in os.listdir(arg):
                if file_name.lower().endswith(('.md', '.txt')):
                    target_files.append(os.path.join(arg, file_name))
        elif os.path.isfile(arg):
            if arg.lower().endswith(('.md', '.txt')):
                target_files.append(arg)
            else:
                print(f"⚠️ 경고: 지원하지 않는 파일 형식입니다. 건너뜁니다: '{arg}'")
        else:
            print(f"⚠️ 경고: 찾을 수 없는 경로 또는 파일입니다: '{arg}'")

    target_files = sorted(list(set(target_files)))
    total_files = len(target_files)

    if total_files == 0:
        print("❌ 오류: 변환할 .md 또는 .txt 파일을 찾지 못했습니다.")
        sys.exit(1)

    print("==================================================")
    print(f"🚀 대량 콘텐츠 자동 생성 파이프라인 가동 (총 {total_files}개 파일)")
    print("==================================================\n")

    for idx, file_path in enumerate(target_files, 1):
        print(f"▶️ [{idx}/{total_files}] 작업 시작: {file_path}")
        await run_auto_studio(file_path)
        
    print("==================================================")
    print("🎉 모든 파일의 콘텐츠 변환 작업이 완벽하게 종료되었습니다! 🎉")
    print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("💡 사용법: python run_pipeline.py <폴더경로_또는_파일>")
        sys.exit(1)
        
    asyncio.run(main())