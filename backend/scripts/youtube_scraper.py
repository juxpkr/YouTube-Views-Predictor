import os
import requests
import pandas as pd

# 📌 YouTube API 설정
API_KEY = "AIzaSyD1nEO18khr0wunaEm0SogZnhU6ewNIpxE"
BASE_URL = "https://www.googleapis.com/youtube/v3/"

# 📌 데이터 저장 폴더 (`backend/data/`)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # 🔥 `backend/` 디렉토리 경로
DATA_DIR = os.path.join(BASE_DIR, "data")  # `backend/data/` 폴더
os.makedirs(DATA_DIR, exist_ok=True)  # ✅ 폴더 없으면 자동 생성

# 📌 유튜브 인기 동영상 가져오기 (국가: 한국, 최대 30개)
def get_trending_videos(region_code="KR", max_results=30):  # 🇰🇷 한국 데이터 & 30개 설정
    url = f"{BASE_URL}videos?part=snippet,statistics&chart=mostPopular&regionCode={region_code}&maxResults={max_results}&key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error:", response.json())
        return None

    data = response.json()
    
    video_data = []
    for item in data["items"]:
        video_info = {
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        }
        video_data.append(video_info)

    return pd.DataFrame(video_data)

# 📌 인기 동영상 가져오기 (한국 🇰🇷 30개)
df = get_trending_videos(region_code="KR", max_results=30)

# 📌 CSV 저장 (backend/data/에 저장)
csv_path = os.path.join(DATA_DIR, "youtube_trending_kr.csv")  # ✅ backend/data/youtube_trending_kr.csv
df.to_csv(csv_path, index=False)  # ✅ 저장

print(f"✅ 데이터가 {csv_path}에 저장되었습니다!")  # 확인 메시지 출력
