import os
import pandas as pd

# 📌 데이터 불러오기 (경로 설정)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")  # 🔥 backend/data 폴더 지정
os.makedirs(DATA_DIR, exist_ok=True)  # ✅ 폴더 없으면 생성

# 📌 CSV 파일 경로 설정
input_file = os.path.join(DATA_DIR, "youtube_trending_kr.csv")  # 원본 데이터 파일
output_file = os.path.join(DATA_DIR, "processed_youtube_data.csv")  # 저장할 파일

# 📌 데이터 불러오기
df = pd.read_csv(input_file)

# 📌 1. 날짜 데이터 변환
df["published_at"] = pd.to_datetime(df["published_at"])  # 날짜 변환
df["day_of_week"] = df["published_at"].dt.dayofweek  # 월(0)~일(6)
df["hour"] = df["published_at"].dt.hour  # 업로드 시간대

# 📌 2. 텍스트 데이터 처리 (제목 길이 추가)
df["title_length"] = df["title"].apply(len)  # 제목 길이 계산

# 📌 3. 사용하지 않는 컬럼 삭제 (video_id, channel, published_at)
df = df.drop(columns=["video_id", "channel", "published_at", "title"])

# 📌 4. 최종 데이터 저장 (backend/data/ 폴더에 저장)
df.to_csv(output_file, index=False)

# 📌 데이터 확인
print(f"✅ 전처리 완료! 저장된 파일: {output_file}")
print(df.head())
