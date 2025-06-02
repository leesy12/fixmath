import requests
import base64
import json
import os
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# 환경변수에서 API 키 읽기
MATHPIX_APP_ID = os.getenv('MATHPIX_APP_ID')
MATHPIX_APP_KEY = os.getenv('MATHPIX_APP_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 글로벌 OpenAI 클라이언트 객체 생성 (매번 생성 안함)
client = OpenAI(api_key=OPENAI_API_KEY)


# 1. Mathpix OCR 함수
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
    return result.get("text", "")


# 2. 문제 데이터 로드 함수
def load_problem_data(json_path, problem_number):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        problem = next((item for item in data if item['problem_number'] == problem_number), None)
        return problem


# 3. GPT 피드백 요청 함수
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
            temperature=0.7,  # 비용 절감 + 안정적 출력
            # 테스트시 제한
        )
        return response.choices[0].message.content

    except AuthenticationError:
        print("❌ API 인증 실패! OpenAI 키 확인 필요.")
    except RateLimitError:
        print("❌ API 호출 한도 초과! 사용량 확인 필요.")
    except APIConnectionError:
        print("❌ OpenAI 서버 연결 실패. 네트워크 확인 필요.")
    except Exception as e:
        print("❌ 알 수 없는 오류 발생:", e)

    return None


# 4. 전체 실행 흐름
def main():
    image_path = "handwriting04.png"
    json_path = "2022_6월.json"
    subject="공통"
    problem_number =22

    print("▶ Mathpix OCR 실행중...")
    user_solution = mathpix_ocr(image_path)
    print("▶ 추출된 수식:", user_solution)

    print("\n▶ 문제 데이터 불러오는 중...")
    problem = load_problem_data(json_path, problem_number)
    if problem is None:
        print("문제 데이터를 찾을 수 없습니다.")
        return

    print("\n▶ GPT 피드백 요청중...")
    feedback = get_gpt_feedback(problem, user_solution)
    if feedback:
        print("\n▶ GPT 피드백 결과:")
        print(feedback)
    else:
        print("GPT 피드백 생성 실패")


if __name__ == "__main__":
    main()
