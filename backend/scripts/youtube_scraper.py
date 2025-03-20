import os
import sys
import requests
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, YouTubeTrending  # ✅ DB 연동을 위해 가져옴
from flask import Flask  # ✅ DB 연동을 위한 Flask 앱 생성
from config import DB_CONFIG

# 📌 Flask 앱 설정 (DB 연결)
app = Flask(__name__)

# 📌 PostgreSQL 데이터베이스 연결 설정
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# 📌 YouTube API 설정
API_KEY = "AIzaSyD1nEO18khr0wunaEm0SogZnhU6ewNIpxE"
BASE_URL = "https://www.googleapis.com/youtube/v3/"

# 📌 카테고리 ID → 이름 매핑
def get_category_mapping(region_code="KR"):
    url = f"{BASE_URL}videoCategories?part=snippet&regionCode={region_code}&key={API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Error fetching categories:", response.json())
        return {}

    data = response.json()
    category_mapping = {item["id"]: item["snippet"]["title"] for item in data["items"]}
    return category_mapping

# 📌 카테고리 매핑 가져오기
CATEGORY_MAPPING = get_category_mapping()

# 📌 데이터 저장 폴더 (`backend/data/`)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # 🔥 `backend/` 디렉토리 경로
DATA_DIR = os.path.join(BASE_DIR, "data")  # `backend/data/` 폴더
os.makedirs(DATA_DIR, exist_ok=True)  # ✅ 폴더 없으면 자동 생성


# 📌 유튜브 인기 동영상 가져오기 (최대 200개)
def get_trending_videos(region_code="KR", max_results=200):
    videos = []
    next_page_token = None
    total_fetched = 0  # ✅ 가져온 총 개수

    while total_fetched < max_results:
        fetch_size = min(50, max_results - total_fetched)  # ✅ 남은 개수만큼 요청
        url = f"{BASE_URL}videos?part=snippet,statistics&chart=mostPopular&regionCode={region_code}&maxResults={fetch_size}&key={API_KEY}"

        if next_page_token:
            url += f"&pageToken={next_page_token}"

        response = requests.get(url)
        if response.status_code != 200:
            print("❌ API 요청 실패:", response.json())
            break

        data = response.json()
        videos.extend(data["items"])  # ✅ 데이터 추가
        total_fetched += len(data["items"])  # ✅ 총 개수 업데이트

        next_page_token = data.get("nextPageToken")  # ✅ 다음 페이지 토큰 업데이트
        if not next_page_token:
            break  # ✅ 더 이상 가져올 데이터 없음

    return pd.DataFrame([{
        "video_id": item["id"],
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "category": CATEGORY_MAPPING.get(item["snippet"].get("categoryId", "Unknown"), "Unknown"),  # ✅ ID → 이름 변환
        "published_at": item["snippet"]["publishedAt"],
        "views": int(item["statistics"].get("viewCount", 0)),
        "likes": int(item["statistics"].get("likeCount", 0)),
        "comments": int(item["statistics"].get("commentCount", 0)),
        "fetched_at": datetime.utcnow()  # ✅ 데이터를 가져온 시점 기록
    } for item in videos])


# 📌 데이터 저장 함수 (중복 확인 후 저장)
def save_to_db(df):
    with app.app_context():
        for _, row in df.iterrows():
            # ✅ 중복 데이터 확인 (video_id가 DB에 이미 존재하는지 확인)
            existing_video = YouTubeTrending.query.filter_by(video_id=row["video_id"]).first()
            if not existing_video:
                new_video = YouTubeTrending(
                    video_id=row["video_id"],
                    title=row["title"],
                    channel=row["channel"],
                    category=row["category"],
                    views=row["views"],
                    likes=row["likes"],
                    comments=row["comments"],
                    published_at=datetime.strptime(row["published_at"], "%Y-%m-%dT%H:%M:%SZ"),
                    fetched_at=row["fetched_at"]
                )
                db.session.add(new_video)

        db.session.commit()  # ✅ 모든 데이터 저장 완료
        print("✅ 데이터가 DB에 저장되었습니다!")


# 📌 인기 동영상 가져오기 (최대 200개)
df = get_trending_videos(region_code="KR", max_results=200)

if df is not None:
    # ✅ CSV 저장 (백업 용도)
    csv_path = os.path.join(DATA_DIR, "youtube_trending_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ 데이터가 {csv_path}에 저장되었습니다!")

    # ✅ DB 저장 실행
    save_to_db(df)
