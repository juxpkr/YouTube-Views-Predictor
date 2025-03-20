import pandas as pd

# 저장된 CSV 파일 불러오기
df = pd.read_csv('./data/youtube_trending_data.csv')

# 데이터의 상위 5개 행 확인
print("Top 5 rows of the dataset:")
print(df.head())

# 데이터의 기본 통계 확인 (null 값, 통계량 등)
print("Basic information about the dataset:")
print(df.info())

# 기초 통계 분석 (숫자형 데이터에 대한 요약 통계)
print("Summary statistics of the dataset:")
print(df.describe())
