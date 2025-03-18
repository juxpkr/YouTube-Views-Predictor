import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # ✅ CORS 라이브러리 추가
import joblib
import pandas as pd

# 여기서 Vue 빌드 결과물을 서빙하기 위해 static_folder를 지정
app = Flask(__name__, static_folder="../frontend_build", static_url_path="")
CORS(app)  # CORS 허용 (다른 도메인에서 요청 가능)

# 모델 로드(머신러닝 모델 pkl 파일일)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "youtube_model.pkl")
model = joblib.load(MODEL_PATH)  # ✅ 변경된 경로로 모델 로드

# Vue 정적 파일 서빙
# '/' 경로로 접근하면 Vue의 index.html 파일을 반환
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Vue 정적 파일(.js, .css 등) 서빙
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# 예측 API (POST)
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # 📌 필요한 값 추출 (입력 데이터)
        new_video = pd.DataFrame({
            "likes": [data["likes"]],
            "comments": [data["comments"]],
            "day_of_week": [data["day_of_week"]],
            "hour": [data["hour"]],
            "title_length": [data["title_length"]]
        })

        # 📌 조회수 예측
        predicted_views = model.predict(new_video)

        # 📌 결과 반환
        return jsonify({"predicted_views": int(predicted_views[0])})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=5000, debug=True)
