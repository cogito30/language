import os
import sys
import time
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """개별 파이썬 스크립트를 실행하고 결과를 반환합니다."""
    if not os.path.exists(script_name):
        print(f"❌ 오류: '{script_name}' 파일을 찾을 수 없습니다.")
        print(f"   -> 해당 파일이 같은 폴더에 있는지 확인해 주세요.\n")
        return False

    print(f"\n{'='*50}")
    print(f"🚀 [STEP] {description} 시작... ({script_name})")
    print(f"{'='*50}\n")
    
    try:
        # sys.executable을 사용해 현재 실행 중인 파이썬 환경과 동일한 환경으로 서브 스크립트 실행
        result = subprocess.run([sys.executable, script_name], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ [실패] {script_name} 실행 중 오류가 발생했습니다. 작업을 중단합니다.")
        return False

if __name__ == "__main__":
    print("✨ 단어장 원클릭 자동화 시스템을 시작합니다 ✨\n")
    
    # 1. input 폴더 확인
    BASE_DIR = Path('.')
    INPUT_DIR = BASE_DIR / 'input'
    
    if not INPUT_DIR.exists() or not INPUT_DIR.is_dir():
        print(f"⚠️ 오류: '{INPUT_DIR.name}' 폴더를 찾을 수 없습니다.")
        print("작업을 시작하기 전에 'input' 폴더에 단어장 마크다운(.md) 파일들을 넣어주세요.")
        sys.exit(1)

    # 2. 실행할 스크립트 목록 정의 (실행 순서대로 배치)
    scripts_to_run = [
        ("create_quiz.py", "📝 마크다운 퀴즈 및 정답지 생성"),
        ("create_card_total.py", "🖼️ 분리형/통합형 카드 뉴스 생성"),
        ("create_pdf.py", "📄 A4 사이즈 단어장 PDF 워크북 병합"),
        ("create_audio_total.py", "🎧 AI 원어민 오디오 생성 및 스터디 병합"),
        ("create_video_total.py", "🎬 최종 학습용 숏폼 동영상 병합")
    ]

    total_start_time = time.time()

    # 3. 스크립트 순차 실행
    for script_name, description in scripts_to_run:
        success = run_script(script_name, description)
        if not success:
            # 하나라도 실패하면 다음 단계로 넘어가지 않고 즉시 종료
            sys.exit(1)
            
        time.sleep(1) # 스크립트 간 약간의 딜레이 부여

    # 4. 최종 완료 메시지
    total_elapsed_time = time.time() - total_start_time
    minutes, seconds = divmod(total_elapsed_time, 60)
    
    print(f"\n{'='*50}")
    print(f"🎉 모든 자동화 작업이 성공적으로 완료되었습니다! 🎉")
    print(f"⏱️ 총 소요 시간: {int(minutes)}분 {int(seconds)}초")
    print(f"{'='*50}")
    print("\n[생성된 결과물 폴더를 확인해 보세요]")
    print(" 📂 Quiz_Results  : 단어 시험지 및 정답지")
    print(" 📂 Card_Results  : 정방형 카드 뉴스 이미지")
    print(" 📂 Audio_Results : 개별 단어 음성 및 마스터 오디오")
    print(" 📂 Video_Results : 최종 업로드용 MP4 동영상")