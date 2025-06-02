import base64 #이미지를 base64 문자열로 바꾸는 모듈
import requests #api 호출용 모듈
import json # JSON 데이터를 보기 좋게 출력하기 위해 사용

# Mathpix API 키
APP_ID = '...'
APP_KEY = '...'

# 이미지 파일 경로
IMAGE_PATH = 'handwriting02.png'


# 이미지 파일을 base64로 인코딩
def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


# Mathpix API 요청 함수
def call_mathpix(image_base64):
    url = 'https://api.mathpix.com/v3/text'

    headers = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'Content-type': 'application/json',
    }

    data = {
        'src': f'data:image/png;base64,{image_base64}',
        'formats': ['latex_simplified'],  # 수식 형태를 간단한 LaTeX로
        'ocr': ['math', 'text']  # 수식 + 일반 텍스트 모두 분석
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


# 메인 실행부
if __name__ == '__main__':
    img_base64 = image_to_base64(IMAGE_PATH)
    result = call_mathpix(img_base64)
    print(json.dumps(result, indent=2, ensure_ascii=False))
