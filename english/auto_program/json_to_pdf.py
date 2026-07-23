import json
import sys
import os
from weasyprint import HTML

def generate_pdf_from_json(json_path, pdf_path):
    # 1. JSON 파일 읽기
    if not os.path.exists(json_path):
        print(f"❌ 오류: 파일을 찾을 수 없습니다. ({json_path})")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data.get("title", "English Vocabulary")
    vocabulary = data.get("vocabulary", [])

    # 2. PDF 디자인을 위한 HTML & CSS 템플릿 작성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
            background-color: #f8f9fa; /* 눈이 편안한 옅은 배경색 */
        }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #2c3e50;
        }}
        *, *::before, *::after {{
            box-sizing: border-box;
        }}
        .header {{
            text-align: center;
            padding-bottom: 20px;
            margin-bottom: 30px;
            border-bottom: 2px solid #bdc3c7;
        }}
        h1 {{
            font-size: 24pt;
            color: #2c3e50;
            margin: 0;
            letter-spacing: 1px;
        }}
        .word-block {{
            page-break-inside: avoid; /* 단어 블록이 페이지 중간에 잘리지 않도록 설정 */
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-left: 6px solid #3498db; /* 왼쪽 포인트 컬러 */
            padding: 15px 20px;
            margin-bottom: 15px;
            border-radius: 4px;
        }}
        .word-header {{
            margin-bottom: 10px;
        }}
        .word-number {{
            font-size: 14pt;
            font-weight: bold;
            color: #7f8c8d;
            margin-right: 5px;
        }}
        .word-title {{
            font-size: 16pt;
            font-weight: bold;
            color: #2980b9;
        }}
        .word-meaning {{
            font-size: 12pt;
            font-weight: bold;
            color: #e74c3c;
            margin-left: 10px;
        }}
        .example-box {{
            background-color: #fdfefe;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #ecf0f1;
        }}
        .example-en {{
            font-size: 11pt;
            color: #34495e;
            margin: 0 0 5px 0;
            font-weight: bold;
        }}
        .example-ko {{
            font-size: 10.5pt;
            color: #7f8c8d;
            margin: 0;
        }}
    </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
        </div>
    """

    # 3. JSON 데이터를 HTML 포맷 안에 반복해서 주입
    for i, item in enumerate(vocabulary, 1):
        word = item.get("word", "")
        meanings = ", ".join(item.get("meanings", []))
        example = item.get("example", "")
        translation = item.get("translation", "")
        
        html_content += f"""
        <div class="word-block">
            <div class="word-header">
                <span class="word-number">{i}.</span>
                <span class="word-title">{word}</span>
                <span class="word-meaning">({meanings})</span>
            </div>
            <div class="example-box">
                <p class="example-en">" {example} "</p>
                <p class="example-ko">{translation}</p>
            </div>
        </div>
        """
        
    html_content += """
    </body>
    </html>
    """

    # 4. 임시 HTML 파일 생성 및 WeasyPrint로 PDF 변환
    temp_html = "temp_render.html"
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"⏳ PDF를 생성 중입니다. 잠시만 기다려주세요...")
    HTML(filename=temp_html).write_pdf(pdf_path)
    
    # 임시 파일 삭제
    if os.path.exists(temp_html):
        os.remove(temp_html)
        
    print(f"✅ 학습용 문서 생성이 완료되었습니다: '{pdf_path}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("💡 사용법: python json_to_pdf.py <입력파일.json> <출력파일.pdf>")
        sys.exit(1)
        
    input_json = sys.argv[1]
    output_pdf = sys.argv[2]
    
    generate_pdf_from_json(input_json, output_pdf)