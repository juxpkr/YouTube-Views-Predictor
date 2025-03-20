from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import DB_CONFIG  # ✅ 설정 파일 가져오기
from datetime import datetime  # ✅ 날짜 저장을 위해 추가

app = Flask(__name__)

# ✅ PostgreSQL 연결 설정
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ✅ 기존 예측 데이터 저장 모델
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    likes = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    title_length = db.Column(db.Integer, nullable=False)
    predicted_view = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# ✅ 새로운 유튜브 트렌드 데이터 저장 모델 추가
class YouTubeTrending(db.Model):
    __tablename__ = "youtube_trending"
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(50), unique=True, nullable=False)  # 📌 유튜브 비디오 ID (중복 방지)
    title = db.Column(db.Text, nullable=False)  # 제목
    channel = db.Column(db.String(255), nullable=False)  # 채널명
    category = db.Column(db.String(50), nullable=False)  # 카테고리 (ex. 게임, 음악)
    views = db.Column(db.BigInteger, nullable=False)  # 조회수
    likes = db.Column(db.BigInteger, nullable=False)  # 좋아요 수
    comments = db.Column(db.BigInteger, nullable=False)  # 댓글 수
    published_at = db.Column(db.DateTime, nullable=False)  # 업로드 날짜
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)  # 크롤링한 시점 저장

# ✅ DB 테이블 생성 실행
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ 테이블 생성 완료!")
