
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from utils import parse_filename, load_problem_data
from mathpix_api import mathpix_ocr
from openai_helper import get_gpt_feedback

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        file = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(image_path)

        json_path, subject, problem_number = parse_filename(image_path)
        user_solution = mathpix_ocr(image_path)
        problem = load_problem_data(json_path, subject, problem_number)
        if problem is None:
            return jsonify({'error': '문제를 찾을 수 없습니다.'}), 400

        feedback = get_gpt_feedback(problem, user_solution)
        if not feedback:
            return jsonify({'error': 'GPT 피드백 생성 실패'}), 500

        return jsonify({'user_solution': user_solution, 'feedback': feedback})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
