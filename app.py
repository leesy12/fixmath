from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from mathpix_api import mathpix_ocr
from openai_helper import get_gpt_feedback
from utils import load_problem_data

# 환경 변수 로드
load_dotenv()

# Flask 앱 생성
app = Flask(__name__)

# 이미지 저장 폴더 설정
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# API 엔드포인트: 분석 요청
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 이미지와 문제번호 받기
        file = request.files['image']
        problem_number = int(request.form['problem_number'])
        json_path = request.form.get('json_path')  # 기본 json

        # 이미지 저장
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        # OCR 수행
        user_solution = mathpix_ocr(image_path)

        # 문제 데이터 로드
        problem = load_problem_data(json_path, problem_number)
        if not problem:
            return jsonify({'error': '문제 데이터를 찾을 수 없습니다.'}), 400

        # GPT 피드백 요청
        feedback = get_gpt_feedback(problem, user_solution)
        if not feedback:
            return jsonify({'error': 'GPT 피드백 생성 실패'}), 500

        return jsonify({
            'user_solution': user_solution,
            'feedback': feedback
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
