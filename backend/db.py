import psycopg2
from config import DB_CONFIG

try: 
    conn = psycopg2.connect(**DB_CONFIG)
    print("PostgreSQL 연결 성공!")
    conn.close()

except Exception as e:
    print(f"PostgreSQL 연결 실패: {e}")