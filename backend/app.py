import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ CORS 라이브러리 추가
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ CORS 모든 요청 허용

# 📌 모델 파일의 올바른 경로 설정
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "youtube_model.pkl")
model = joblib.load(MODEL_PATH)  # ✅ 변경된 경로로 모델 로드

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
    app.run(debug=True)
