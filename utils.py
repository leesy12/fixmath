import json

def load_problem_data(json_path, problem_number):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        problem = next((item for item in data if item['problem_number'] == problem_number), None)
        return problem
