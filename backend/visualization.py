import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import DB_CONFIG  # DB 연결 정보 가져오기


# ✅ 한글 폰트 설정
plt.rc("font", family="Malgun Gothic")  # Windows (맑은 고딕)
plt.rc("axes", unicode_minus=False)  # 마이너스 기호 깨짐 방지


# ✅ PostgreSQL 데이터베이스 연결
conn = psycopg2.connect(
    dbname=DB_CONFIG["dbname"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"]
)

# ✅ 쿼리 실행 (모든 데이터 가져오기)
query = "SELECT likes, comments, day_of_week, hour, title_length, predicted_view, created_at FROM prediction;"
df = pd.read_sql(query, conn)

#요일별 평균 조회수 계산
day_avg_views = df.groupby("day_of_week")["predicted_view"].mean().reset_index()
# ✅ 요일별 조회수 시각화
plt.figure(figsize=(8, 5))
sns.barplot(x="day_of_week", y="predicted_view", data=day_avg_views, palette="viridis")
plt.xticks(ticks=range(7), labels=["월", "화", "수", "목", "금", "토", "일"])
plt.xlabel("업로드 요일")
plt.ylabel("평균 조회수")
plt.title("📊 요일별 평균 조회수")
plt.show()



# ✅ 업로드 시간별 평균 조회수 계산
hour_avg_views = df.groupby("hour")["predicted_view"].mean().reset_index()

# ✅ 업로드 시간별 조회수 시각화
plt.figure(figsize=(10, 5))
sns.lineplot(x="hour", y="predicted_view", data=hour_avg_views, marker="o", color="b")
plt.xticks(range(0, 24))
plt.xlabel("업로드 시간")
plt.ylabel("평균 조회수")
plt.title("⏰ 업로드 시간대별 평균 조회수")
plt.show()


# ✅ 좋아요 수 vs 조회수 시각화
plt.figure(figsize=(6, 5))
sns.scatterplot(x="likes", y="predicted_view", data=df, alpha=0.5, color="r")
plt.xlabel("좋아요 수")
plt.ylabel("조회수")
plt.title("❤️ 좋아요 수 vs 조회수")
plt.show()

# ✅ 댓글 수 vs 조회수 시각화
plt.figure(figsize=(6, 5))
sns.scatterplot(x="comments", y="predicted_view", data=df, alpha=0.5, color="g")
plt.xlabel("댓글 수")
plt.ylabel("조회수")
plt.title("💬 댓글 수 vs 조회수")
plt.show()


# ✅ 연결 종료
conn.close()

# ✅ 데이터 확인
print(df.head())
