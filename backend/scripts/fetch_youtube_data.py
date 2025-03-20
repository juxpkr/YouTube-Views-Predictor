import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG  # ✅ DB 설정 불러오기

# ✅ DB 연결 문자열 생성
DB_URI = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# ✅ SQLAlchemy 엔진 생성
engine = create_engine(DB_URI)

# ✅ SQL 쿼리 실행하여 데이터 불러오기 (수정됨)
query = text("SELECT * FROM youtube_trending")  # ✅ 테이블 이름 확인 필요!
df = pd.read_sql(query, con=engine)

# ✅ 데이터 확인
print(df.head())  # 🎯 5개만 출력해서 확인

# ✅ CSV로 저장 (백업용)
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)
csv_path = os.path.join(data_dir, "youtube_trending_data.csv")
df.to_csv(csv_path, index=False)
print(f"✅ 데이터가 {csv_path}에 저장되었습니다!")
