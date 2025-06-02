from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import pytesseract
import json

app = Flask(__name__)

# Load OpenAI API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Optional: Tesseract 경로 설정 (Windows 전용)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# 문제 불러오기 함수
def get_problem_data(year, exam_type, problem_number):
    path = os.path.join('data', str(year), f"{exam_type}.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return next((p for p in data if p['problem_number'] == problem_number), None)
    except Exception as e:
        print(f"[ERROR] 문제 파일 로딩 실패: {e}")
        return None


# 피드백 생성 함수
def get_solution_feedback(problem, user_solution):
    try:
        prompt = f"""
다음은 고등학생이 작성한 수학 문제 풀이입니다. 학생이 자신감을 잃지 않도록, 따뜻하고 친절한 말투로 정중하게 피드백을 해주세요.

문제: {problem['question']}
정답: {problem['correct_option']}
정답 풀이 과정: {', '.join(problem['solution_steps'])}
피드백 기준: {', '.join(problem['feedback_criteria'])}

[학생의 풀이]
{user_solution}

GPT의 피드백 형식:
1. 풀이가 맞았는지 여부
2. 잘한 점
3. 아쉬운 점이 있다면 개선 방향
4. 마지막에 학생을 응원하는 한 줄

말투는 선생님이 학생에게 말하듯이, 다정하고 긍정적인 어조로 작성해주세요.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful math tutor who provides detailed feedback on student solutions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] 피드백 생성 실패: {e}")
        return None


# 메인 페이지
@app.route('/')
def index():
    years = ['2022', '2023', '2024']
    return render_template('index.html', years=years)


# 문제 가져오기 API
@app.route('/get_problem', methods=['POST'])
def get_problem():
    data = request.json
    year = data.get('year')
    exam_type = data.get('exam_type')
    number = data.get('problem_number')

    problem = get_problem_data(year, exam_type, number)
    if problem:
        return jsonify({'success': True, 'problem': problem})
    return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'})


# 피드백 생성 API
@app.route('/get_feedback', methods=['POST'])
def get_feedback():
    data = request.json
    year = data.get('year')
    exam_type = data.get('exam_type')
    number = data.get('problem_number')
    user_solution = data.get('solution')

    problem = get_problem_data(year, exam_type, number)
    if not problem:
        return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'})

    feedback = get_solution_feedback(problem, user_solution)
    if feedback:
        return jsonify({'success': True, 'feedback': feedback})
    return jsonify({'success': False, 'message': '피드백 생성 실패'})


# 이미지 업로드 및 자동 채점 API
@app.route('/upload_and_feedback', methods=['POST'])
def upload_and_feedback():
    try:
        file = request.files.get('image')
        year = request.form.get('year')
        exam_type = request.form.get('exam_type')
        number = int(request.form.get('problem_number'))

        if not file or not year or not exam_type or not number:
            return jsonify({'success': False, 'message': '모든 값을 입력해주세요.'})

        image = Image.open(file.stream)
        extracted = pytesseract.image_to_string(image, lang='eng+kor')

        problem = get_problem_data(year, exam_type, number)
        if not problem:
            return jsonify({'success': False, 'message': '문제를 찾을 수 없습니다.'})

        feedback = get_solution_feedback(problem, extracted)
        if not feedback:
            return jsonify({'success': False, 'message': '피드백 생성 실패'})

        return jsonify({
            'success': True,
            'extracted_text': extracted,
            'feedback': feedback
        })

    except Exception as e:
        print(f"[ERROR] 이미지 업로드 오류: {e}")
        return jsonify({'success': False, 'message': '서버 내부 오류'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
