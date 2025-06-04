import os
import json
import base64
import requests
from flask import Flask, request, jsonify
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ✅ Flask 앱 인스턴스 생성 (반드시 이 위치에!)
app = Flask(__name__)

# ✅ 업로드 폴더 설정
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ .env 환경변수 불러오기
load_dotenv()
MATHPIX_APP_ID = os.getenv('MATHPIX_APP_ID')
MATHPIX_APP_KEY = os.getenv('MATHPIX_APP_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ✅ OpenAI 클라이언트 설정
client = OpenAI(api_key=OPENAI_API_KEY)

# ✅ 루트 경로 응답 (브라우저에서 확인용)
@app.route("/", methods=["GET"])
def index():
    return "✅ 서버 실행 중입니다. /analyze로 POST 요청을 보내세요."

# ✅ Mathpix OCR 함수
def mathpix_ocr(image_path):
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode()

    headers = {
        'app_id': MATHPIX_APP_ID,
        'app_key': MATHPIX_APP_KEY,
        'Content-type': 'application/json'
    }

    data = {
        'src': f'data:image/png;base64,{image_base64}',
        'formats': ['text', 'latex_styled'],
        'ocr': ['math', 'text']
    }

    response = requests.post('https://api.mathpix.com/v3/text', headers=headers, json=data)
    result = response.json()
    return result.get("text", "").strip()

# ✅ 문제 데이터 불러오기
def load_problem_data(json_path, problem_number):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # ✅ JSON이 리스트일 경우만 작동
        return next((item for item in data if item['problem_number'] == problem_number), None)

# ✅ GPT 피드백 생성
def get_gpt_feedback(problem, user_solution):
    prompt = f"""
문제: {problem['question']}
학생 풀이: {user_solution}
정답: {problem['answer']}
기준 풀이 방식: {problem['method']}
피드백 기준: {problem['feedback_criteria']}

학생 풀이를 기준으로 올바른 풀이인지 판단하고, 피드백을 작성해 주세요.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 수학 풀이 피드백을 작성하는 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except (AuthenticationError, RateLimitError, APIConnectionError) as e:
        print(f"OpenAI API 오류: {e}")
    except Exception as e:
        print(f"알 수 없는 오류: {e}")
    return None

# ✅ 분석 API 엔드포인트
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # 파일과 파일명 받기
        image_file = request.files.get("file")
        filename = request.form.get("filename")  # 예: "2022_6월_공통_1.png"

        if not image_file or not filename:
            return jsonify({"error": "파일 또는 파일명이 없습니다."}), 400

        # 파일 저장
        safe_name = secure_filename(filename)
        save_path = os.path.join(UPLOAD_FOLDER, safe_name)
        image_file.save(save_path)

        # 파일명 파싱
        parts = safe_name.replace(".png", "").split("_")
        if len(parts) < 4:
            return jsonify({"error": "파일명 형식 오류"}), 400

        json_path = f"{parts[0]}_{parts[1]}.json"  # 예: "2022_6월.json"
        subject = parts[2]
        problem_number = int(parts[3])


        json_full_path = json_path


        problem = load_problem_data(json_full_path, problem_number)

        print("⬛ [DEBUG] json_path =", json_full_path)
        print("⬛ [DEBUG] problem_number =", problem_number)
        print("⬛ [DEBUG] subject (from filename) =", repr(subject))
        print("⬛ [DEBUG] loaded problem =", problem)
        if problem:
            print("⬛ [DEBUG] problem['subject'] =", repr(problem["subject"]))

        # OCR 처리
        user_solution = mathpix_ocr(save_path)

        # 문제 불러오기
        problem = load_problem_data(json_full_path, problem_number)
        if not problem or problem["subject"] != subject:
            return jsonify({"error": "문제 데이터를 찾을 수 없습니다."}), 404
        

        # GPT 피드백
        feedback = get_gpt_feedback(problem, user_solution)
        if not feedback:
            return jsonify({"error": "GPT 피드백 실패"}), 500

        return jsonify({
            "user_solution": user_solution,
            "feedback": feedback
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ 로컬 실행용 (Render에서는 무시됨)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 호환용
    app.run(host="0.0.0.0", port=port)
