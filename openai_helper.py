import os
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def get_gpt_feedback(problem, user_solution):
    prompt = f"""
문제: {problem['question']}
학생 풀이: {user_solution}
정답: {problem['answer']}
기준 풀이 방식: {problem['solution_steps']}
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
