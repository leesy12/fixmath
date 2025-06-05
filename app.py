from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/check_filename", methods=["POST"])
def check_filename():
    filename = "2022_6_공통_1.png"
    
    # 한글 포함 여부 확인
    if not all(ord(c) < 128 for c in filename):  # 한글이 포함된 경우
        result = f"한글 포함: {filename}"
    else:
        result = f"한글 없음: {filename}"
    
    # secure_filename 사용
    safe_name = secure_filename(filename)
    
    # 결과를 프론트엔드에 반환
    return jsonify({
        "original_filename": filename,
        "safe_filename": safe_name,
        "result": result
    })

# 서버 시작 (로컬에서 테스트용)
if __name__ == "__main__":
    app.run(debug=True)
