import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 한글 폰트 적용 (윈도우)
plt.rc("font", family="Malgun Gothic")
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# 📌 CSV 파일 불러오기
df = pd.read_csv("youtube_trending.csv")

# 📌 데이터 출력 (터미널에서 확인)
print(df.head())

# 📌 1. 조회수 vs 좋아요 수 관계 분석
plt.figure(figsize=(10, 5))
sns.scatterplot(x=df["likes"], y=df["views"])
plt.xscale("log")
plt.yscale("log")
plt.title("좋아요 수 vs 조회수 (로그 스케일)")
plt.xlabel("Likes")
plt.ylabel("Views")
plt.show()

# 📌 2. 조회수 vs 댓글 수 관계 분석
plt.figure(figsize=(10, 5))
sns.scatterplot(x=df["comments"], y=df["views"])
plt.xscale("log")
plt.yscale("log")
plt.title("댓글 수 vs 조회수 (로그 스케일)")
plt.xlabel("Comments")
plt.ylabel("Views")
plt.show()

# 📌 3. 요일별 조회수 분석 (날짜 데이터 변환)
df["published_at"] = pd.to_datetime(df["published_at"])  # 날짜 데이터 변환
df["day_of_week"] = df["published_at"].dt.day_name()  # 요일 추출

plt.figure(figsize=(10, 5))
sns.boxplot(x=df["day_of_week"], y=df["views"])
plt.yscale("log")
plt.title("요일별 조회수 분포")
plt.xlabel("Day of Week")
plt.ylabel("Views")
plt.show()

# 📌 4. 영상 제목 길이 vs 조회수 분석
df["title_length"] = df["title"].apply(len)  # 제목 길이 계산

plt.figure(figsize=(10, 5))
sns.scatterplot(x=df["title_length"], y=df["views"])
plt.xscale("log")
plt.yscale("log")
plt.title("제목 길이 vs 조회수")
plt.xlabel("Title Length")
plt.ylabel("Views")
plt.show()
