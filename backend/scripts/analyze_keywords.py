import os
import sys
import requests
import pandas as pd
import psycopg2
from collections import Counter
from konlpy.tag import Okt
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, YouTubeTrending  # ✅ DB 연동을 위해 가져옴
from flask import Flask  # ✅ DB 연동을 위한 Flask 앱 생성
from config import DB_CONFIG

# ✅ Flask 앱 설정 (DB 연결)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ✅ PostgreSQL 연결 설정
def connect_db():
    return psycopg2.connect(**DB_CONFIG)

# ✅ 불용어 리스트 불러오기
def load_stopwords():
    stopwords_path = os.path.join(os.path.dirname(__file__), "stopwords.txt")
    if os.path.exists(stopwords_path):
        with open(stopwords_path, "r", encoding="utf-8") as f:
            stopwords = [line.strip() for line in f.readlines()]
    else:
        stopwords = []
    return stopwords

stopwords = load_stopwords()
print(f"✅ 불용어 리스트 로드 완료! {len(stopwords)}개 단어 필터링 예정")

# ✅ 형태소 분석기 초기화
okt = Okt()

# ✅ 특정 날짜의 유튜브 제목 불러오기 (오늘, 어제)
def fetch_titles_from_db(days_ago=0):
    conn = connect_db()
    cur = conn.cursor()

    query = """
    SELECT title FROM youtube_trending
    WHERE fetched_at::DATE = NOW()::DATE - INTERVAL '%s days';
    """
    cur.execute(query, (days_ago,))
    titles = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return titles

# ✅ 키워드 추출 함수
def extract_keywords(titles):
    keywords = []
    for title in titles:
        nouns = okt.nouns(title)  # 명사 추출
        keywords.extend([word for word in nouns if word not in stopwords and len(word) > 1])
    return Counter(keywords)

# ✅ 오늘과 어제 키워드 추출
today_titles = fetch_titles_from_db(0)  # 오늘 데이터
yesterday_titles = fetch_titles_from_db(1)  # 어제 데이터

today_keywords = extract_keywords(today_titles)
yesterday_keywords = extract_keywords(yesterday_titles)

# ✅ 데이터프레임 변환
df_today = pd.DataFrame(today_keywords.items(), columns=["Keyword", "TodayCount"])
df_yesterday = pd.DataFrame(yesterday_keywords.items(), columns=["Keyword", "YesterdayCount"])

# ✅ 키워드 변화 분석 (합집합 후 비교)
df_merge = pd.merge(df_today, df_yesterday, on="Keyword", how="outer")

# ✅ fillna(0) 후 자동 다운캐스팅 방지
df_merge = df_merge.infer_objects(copy=False)

# ✅ 안전하게 숫자로 변환
df_merge["TodayCount"] = pd.to_numeric(df_merge["TodayCount"].fillna(0))
df_merge["YesterdayCount"] = pd.to_numeric(df_merge["YesterdayCount"].fillna(0))
df_merge["Difference"] = df_merge["TodayCount"] - df_merge["YesterdayCount"]


# ✅ 변화 유형 분류
def classify_change(row):
    if row["YesterdayCount"] == 0:
        return "NEW"
    elif row["TodayCount"] == 0:
        return "DISAPPEARED"
    elif row["Difference"] > 0:
        return "INCREASED"
    elif row["Difference"] < 0:
        return "DECREASED"
    else:
        return "NO_CHANGE"

df_merge["ChangeType"] = df_merge.apply(classify_change, axis=1)

# ✅ 기존 키워드 백업 (fetched_at 추가하여 유지)
def backup_old_keywords():
    conn = connect_db()
    cur = conn.cursor()
    
    query = """
    INSERT INTO youtube_trending_keywords_old (Keyword, Count, fetched_at)
    SELECT Keyword, Count, NOW() FROM youtube_trending_keywords;
    """
    cur.execute(query)
    conn.commit()
    conn.close()
    print("✅ 기존 키워드 데이터를 youtube_trending_keywords_old 테이블에 백업 완료!")

# ✅ PostgreSQL에 새로운 키워드 데이터 저장
def save_keywords_to_db():
    conn = connect_db()
    cur = conn.cursor()

    # ✅ 새로운 키워드 데이터 삽입 (중복 저장 허용)
    for _, row in df_today.iterrows():
        query = """
        INSERT INTO youtube_trending_keywords (Keyword, Count, fetched_at) 
        VALUES (%s, %s, NOW());
        """
        cur.execute(query, (row["Keyword"], row["TodayCount"]))

    conn.commit()
    conn.close()
    print("✅ 새로운 키워드 데이터를 PostgreSQL에 저장 완료!")

# ✅ 키워드 변화 데이터 저장 (fetched_at 추가)
def save_keyword_changes():
    conn = connect_db()
    cur = conn.cursor()

    for _, row in df_merge.iterrows():
        query = """
        INSERT INTO youtube_trending_keyword_changes (Keyword, OldCount, NewCount, Difference, ChangeType, fetched_at) 
        VALUES (%s, %s, %s, %s, %s, NOW());
        """
        cur.execute(query, (row["Keyword"], row["YesterdayCount"], row["TodayCount"], row["Difference"], row["ChangeType"]))

    conn.commit()
    conn.close()
    print("✅ 키워드 변화 데이터를 PostgreSQL에 저장 완료!")

# ✅ 기존 키워드 데이터 백업 & 최신 키워드 저장
backup_old_keywords()
save_keywords_to_db()
save_keyword_changes()

# ✅ CSV 파일 저장 (확인용)
csv_path = os.path.join(os.path.dirname(__file__), "youtube_trending_keywords.csv")
df_merge.to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"✅ CSV 저장 완료 (확인용): {csv_path}")

# ✅ 상위 변화 키워드 출력
top_keywords = df_merge.sort_values(by="Difference", ascending=False).head(20)

print("\n📌 **유튜브 트렌드 키워드 TOP 20**")
for idx, row in top_keywords.iterrows():
    print(f"{row['Keyword']}: {row['Difference']}회 ({row['ChangeType']})")

print("\n✅ 키워드 분석 및 저장 완료!")
