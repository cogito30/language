import json
import os
import sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def create_lesson_video(json_path, img_dir="card_news_output", aud_dir="audio_output", output_path="lesson_video.mp4"):
    # 1. JSON 파일 읽어오기
    if not os.path.exists(json_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다. ({json_path})")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    vocabulary = data.get("vocabulary", [])
    total_words = len(vocabulary)
    
    video_clips = []

    print(f"🚀 총 {total_words}개의 단어 데이터를 바탕으로 동영상 합성을 시작합니다...")

    # 2. 이미지와 음성을 하나씩 매칭하여 개별 영상 클립으로 만들기
    for i, item in enumerate(vocabulary, 1):
        word = item.get("word", "")
        # 앞선 음성 파일명 생성 규칙과 동일하게 파일명 매칭
        safe_word = "".join(c for c in word if c.isalnum() or c in (' ', '_')).replace(' ', '_')
        
        img_path = os.path.join(img_dir, f"card_{i:02d}.png")
        aud_path = os.path.join(aud_dir, f"audio_{i:02d}_{safe_word}.mp3")

        # 파일 존재 여부 확인
        if not os.path.exists(img_path) or not os.path.exists(aud_path):
            print(f"⚠️ 경고: {i}번째 단어의 이미지 또는 음성 파일이 없어 건너뜁니다.")
            continue

        try:
            # 음성 파일 불러오기
            audio_clip = AudioFileClip(aud_path)
            
            # 이미지 파일 불러오기 및 재생 시간을 음성 파일의 길이에 맞춤
            image_clip = ImageClip(img_path).set_duration(audio_clip.duration)
            
            # 이미지 클립에 음성 입히기
            video_clip = image_clip.set_audio(audio_clip)
            
            video_clips.append(video_clip)
            print(f"✅ 영상 클립 준비 완료 ({i}/{total_words}): {word}")
            
        except Exception as e:
            print(f"❌ 클립 생성 오류 ({word}): {e}")

    if not video_clips:
        print("❌ 합성할 클립이 없습니다. 이미지와 음성 파일이 잘 생성되었는지 확인해주세요.")
        return

    print("\n🎬 모든 클립을 하나의 영상으로 렌더링합니다. (시간이 조금 소요될 수 있습니다...)")
    
    try:
        # 3. 준비된 모든 단어 클립을 순서대로 하나로 이어 붙이기
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # 4. 최종 MP4 파일로 추출 (웹 및 모바일 최적화 코덱 사용)
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger="bar" # 진행 상태바 표시
        )
        print(f"\n🎉 성공적으로 동영상이 생성되었습니다: '{output_path}'")
        
    except Exception as e:
        print(f"❌ 동영상 렌더링 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("💡 사용법: python json_to_video.py <입력파일.json>")
        sys.exit(1)
        
    input_json = sys.argv[1]
    create_lesson_video(input_json)