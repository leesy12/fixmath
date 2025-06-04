
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def get_gpt_feedback(problem, user_solution):
    try:
        prompt = f"""
문제: {problem['question']}
학생의 풀이: {user_solution}
정답: {problem['answer']}
모범 풀이 방법: {problem['method']}
풀이 단계: {problem['solution_steps']}
피드백 기준: {problem['feedback_criteria']}

위 정보를 바탕으로 학생 풀이에 대한 피드백을 작성해줘.
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 수학 선생님이야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT 피드백 요청 중 오류 발생: {e}")
        return None
