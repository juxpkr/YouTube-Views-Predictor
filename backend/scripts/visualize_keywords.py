import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ✅ 데이터 파일 경로
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend 폴더 경로
DATA_DIR = os.path.join(BASE_DIR, "data")  # backend/data 폴더
csv_path = os.path.join(DATA_DIR, "youtube_trending_keywords.csv")  # 키워드 빈도 CSV

# ✅ 데이터 로드
df = pd.read_csv(csv_path)

# ✅ 상위 20개 키워드만 사용
df = df.head(20)

# ✅ 🔥 한글 폰트 설정 추가 🔥
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows의 경우 'Malgun Gothic', Mac은 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False  # 음수 부호 깨짐 방지

# ✅ 그래프 스타일 설정
plt.figure(figsize=(12, 6))
sns.barplot(x="Count", y="Keyword", data=df, palette="viridis")

# ✅ 그래프 제목 & 라벨 설정
plt.title("📌 유튜브 트렌드 키워드 TOP 20", fontsize=14)
plt.xlabel("빈도수", fontsize=12)
plt.ylabel("키워드", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.7)

# ✅ 그래프 저장
plot_path = os.path.join(DATA_DIR, "youtube_trending_keywords.png")
plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"✅ 키워드 시각화 완료! 그래프 저장됨: {plot_path}")
