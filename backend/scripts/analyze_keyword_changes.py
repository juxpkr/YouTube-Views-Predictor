import pandas as pd
import os
import psycopg2
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import db, YouTubeTrending 
from flask import Flask  
from config import DB_CONFIG


# Flask 앱 설정 (DB 연결)
app = Flask(__name__)

# PostgreSQL 데이터베이스 연결 설정
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
DATA_DIR = os.path.join(BASE_DIR, "data")  
changes_csv_path = os.path.join(DATA_DIR, "youtube_trending_keyword_changes.csv")  

# PostgreSQL에서 기존 & 최신 키워드 데이터 불러오기
def fetch_keywords_from_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 기존 키워드 가져오기
    cur.execute("SELECT Keyword, Count FROM youtube_trending_keywords_old;")
    old_keywords = pd.DataFrame(cur.fetchall(), columns=["Keyword", "OldCount"])

    # 최신 키워드 가져오기
    cur.execute("SELECT Keyword, Count FROM youtube_trending_keywords;")
    current_keywords = pd.DataFrame(cur.fetchall(), columns=["Keyword", "NewCount"])

    conn.close()
    return old_keywords, current_keywords

# 기존 & 최신 키워드 데이터 가져오기
old_df, current_df = fetch_keywords_from_db()

print(f"현재 키워드 수: {len(current_df)}개, 이전 키워드 수: {len(old_df)}개")

# Outer Join (합집합)
merged_df = pd.merge(old_df, current_df, on="Keyword", how="outer")

# 결측치(NaN) → 0으로 대체
merged_df["OldCount"] = merged_df["OldCount"].fillna(0)
merged_df["NewCount"] = merged_df["NewCount"].fillna(0)

# 차이 계산
merged_df["Difference"] = merged_df["NewCount"] - merged_df["OldCount"]

# 변화 유형 분류 함수
def classify_change(row):
    old_c = row["OldCount"]
    new_c = row["NewCount"]
    diff = row["Difference"]
    
    if old_c == 0 and new_c > 0:
        return "NEW"  
    elif old_c > 0 and new_c == 0:
        return "DISAPPEARED"  
    elif diff > 0:
        return "INCREASED"  
    elif diff < 0:
        return "DECREASED"  
    else:
        return "NO_CHANGE"  

merged_df["ChangeType"] = merged_df.apply(classify_change, axis=1)

# 절대값 기준 정렬
merged_df["AbsDiff"] = merged_df["Difference"].abs()
merged_df = merged_df.sort_values(by="AbsDiff", ascending=False)

# 중복된 Keyword 행 제거 (첫 번째 행만 남김)
merged_df.drop_duplicates(subset=["Keyword"], inplace=True)

# 상위 30개 출력
top_30 = merged_df.head(30)

print("**상위 30개 키워드 변화**")
print(top_30[["Keyword", "OldCount", "NewCount", "Difference", "ChangeType"]])

# CSV로 저장 (확인용)
merged_df.to_csv(changes_csv_path, index=False, encoding="utf-8-sig")
print(f"키워드 변화 분석 완료! 결과 저장: {changes_csv_path}")

# PostgreSQL에 분석 결과 저장
def save_changes_to_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 기존 데이터 삭제 후 새로운 데이터 삽입
    cur.execute("DELETE FROM youtube_trending_keyword_changes;")
    for _, row in merged_df.iterrows():
        query = """
        INSERT INTO youtube_trending_keyword_changes (Keyword, OldCount, NewCount, Difference, ChangeType, AbsDiff) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (row["Keyword"], row["OldCount"], row["NewCount"], row["Difference"], row["ChangeType"], row["AbsDiff"]))

    conn.commit()
    conn.close()
    print("키워드 변화 데이터를 PostgreSQL youtube_trending_keyword_changes 테이블에 저장 완료!")

# DB 저장 실행
save_changes_to_db()
