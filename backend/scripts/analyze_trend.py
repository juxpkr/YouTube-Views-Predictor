import os
import pandas as pd

# ✅ 데이터 폴더 경로
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # `backend/` 디렉토리 경로
DATA_DIR = os.path.join(BASE_DIR, "data")  # `backend/data/` 폴더

# ✅ 파일 경로 설정
old_csv_path = os.path.join(DATA_DIR, "youtube_trending_keywords_old.csv")  # 과거 데이터
current_csv_path = os.path.join(DATA_DIR, "youtube_trending_keywords.csv")  # 현재 데이터

# ✅ 현재 키워드 데이터 불러오기
print(f"📂 현재 키워드 파일 경로: {current_csv_path}")
if not os.path.exists(current_csv_path):
    print("❌ 현재 데이터 파일이 없습니다. 스크립트를 실행하기 전에 먼저 `analyze_trend.py`를 실행하세요.")
    exit()

current_df = pd.read_csv(current_csv_path)
print(f"✅ 현재 데이터 로드 완료! (총 {len(current_df)}개 키워드)")

# ✅ 이전 키워드 데이터가 없으면, 현재 데이터로 대체
if not os.path.exists(old_csv_path):
    print("⚠️ 이전 데이터가 없습니다. 현재 데이터를 기준으로 설정합니다.")
    current_df.to_csv(old_csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 새로운 이전 데이터 파일 생성 완료: {old_csv_path}")
    exit()

# ✅ 이전 키워드 데이터 불러오기
print(f"📂 이전 키워드 파일 경로: {old_csv_path}")
old_df = pd.read_csv(old_csv_path)
print(f"✅ 이전 데이터 로드 완료! (총 {len(old_df)}개 키워드)")

print("\n📌 현재 데이터 미리보기:")
print(current_df.head())

print("\n📌 이전 데이터 미리보기:")
print(old_df.head())
