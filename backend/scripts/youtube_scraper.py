import os
import sys
import requests
import pandas as pd
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, YouTubeTrending  # ✅ DB 연동을 위해 가져옴
from flask import Flask  # ✅ DB 연동을 위한 Flask 앱 생성
from config import DB_CONFIG

# Flask 앱 설정 (DB 연결)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# YouTube API 설정
API_KEY = "YOUR_YOUTUBE_API_KEY"
BASE_URL = "https://www.googleapis.com/youtube/v3/"

# 카테고리 ID → 이름 매핑
def get_category_mapping(region_code="KR"):
    url = f"{BASE_URL}videoCategories?part=snippet&regionCode={region_code}&key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # API 호출 실패 시 예외 발생
        data = response.json()
        return {item["id"]: item["snippet"]["title"] for item in data.get("items", [])}
    except requests.exceptions.RequestException as e:
        print(f"❌ 카테고리 매핑 실패: {e}")
        return {}

# 카테고리 매핑 가져오기
CATEGORY_MAPPING = get_category_mapping()

# 데이터 저장 폴더 (`backend/data/`)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 유튜브 인기 동영상 가져오기 (최대 200개)
def get_trending_videos(region_code="KR", max_results=200):
    videos = []
    next_page_token = None
    total_fetched = 0

    while total_fetched < max_results:
        fetch_size = min(50, max_results - total_fetched)
        url = f"{BASE_URL}videos?part=snippet,statistics&chart=mostPopular&regionCode={region_code}&maxResults={fetch_size}&key={API_KEY}"
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f" API 요청 실패: {e}")
            break

        data = response.json()
        videos.extend(data["items"])
        total_fetched += len(data["items"])
        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return pd.DataFrame([
        {
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "category": CATEGORY_MAPPING.get(item["snippet"].get("categoryId", "Unknown"), "Unknown"),
            "published_at": item["snippet"]["publishedAt"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0)),
            "fetched_at": datetime.utcnow(),
        }
        for item in videos
    ])

# 데이터 저장 함수 (중복 저장 허용, fetched_at 기준)
def save_to_db(df):
    with app.app_context():
        saved_count = 0
        for _, row in df.iterrows():
            existing_video = YouTubeTrending.query.filter_by(video_id=row["video_id"], fetched_at=row["fetched_at"]).first()
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
                saved_count += 1

        db.session.commit()
        print(f"✅ {saved_count}개의 새로운 데이터가 DB에 저장되었습니다!")

# 인기 동영상 가져오기 (최대 200개)
df = get_trending_videos(region_code="KR", max_results=200)

if df is not None and not df.empty:
    # ✅ CSV 저장 (백업 용도)
    csv_path = os.path.join(DATA_DIR, "youtube_trending_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ 데이터가 {csv_path}에 저장되었습니다!")

    # ✅ DB 저장 실행
    save_to_db(df)
else:
    print("가져온 데이터가 없습니다. 저장을 건너뜁니다.")
