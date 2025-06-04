
import os
import json

def parse_filename(image_path):
    filename = os.path.basename(image_path).replace('.png', '')
    parts = filename.split('_')

    if len(parts) != 4:
        raise ValueError("파일명 형식은 'year_month_subject_problem_number.png' 여야 합니다.")

    json_path = f"{parts[0]}_{parts[1]}.json"  # 연도, 월만 json_path로 사용
    subject = parts[2]
    problem_number = int(parts[3])
    
    

    return json_path, subject, problem_number

def load_problem_data(json_path, subject, problem_number):
    try:
        with open(f"json/{json_path}", 'r', encoding='utf-8') as file:
            data = json.load(file)
            for problem in data:
                if (problem['subject'] == subject and problem['problem_number'] == problem_number):
                    return problem
    except Exception as e:
        print(f"문제 데이터를 불러오는 중 오류 발생: {e}")
        return None
