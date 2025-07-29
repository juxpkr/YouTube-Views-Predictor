import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db, Prediction  
from config import DB_CONFIG  

# 📌 Flask 앱 설정
app = Flask(__name__)
CORS(app)  # CORS 허용 (다른 도메인 요청 가능)

# PostgreSQL 데이터베이스 연결 설정
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# DB 초기화
db.init_app(app)

# 머신러닝 모델 로드
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "youtube_model.pkl")
model = joblib.load(MODEL_PATH)


# 조회수 예측 API (POST)
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        new_video = pd.DataFrame({
            "likes": [data["likes"]],
            "comments": [data["comments"]],
            "day_of_week": [data["day_of_week"]],
            "hour": [data["hour"]],
            "title_length": [data["title_length"]]
        })

        predicted_views = model.predict(new_video)

        # 예측 결과를 DB에 저장
        prediction_entry = Prediction(
            likes=data["likes"],
            comments=data["comments"],
            day_of_week=data["day_of_week"],
            hour=data["hour"],
            title_length=data["title_length"],
            predicted_view=int(predicted_views[0])
        )
        db.session.add(prediction_entry)
        db.session.commit()

        return jsonify({"predicted_views": int(predicted_views[0]), "message": "예측 결과 저장 완료!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 저장된 예측 데이터 조회 API (GET)
@app.route("/predictions", methods=["GET"])
def get_predictions():
    try:
        predictions = Prediction.query.all()
        result = [
            {
                "id": pred.id,
                "likes": pred.likes,
                "comments": pred.comments,
                "day_of_week": pred.day_of_week,
                "hour": pred.hour,
                "title_length": pred.title_length,
                "predicted_view": pred.predicted_view,
                "created_at": pred.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for pred in predictions
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
