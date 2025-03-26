import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 📌 데이터 경로 설정
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")  # backend/data 폴더 지정
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")  # backend/models 폴더 지정
os.makedirs(MODEL_DIR, exist_ok=True)  # 🔥 폴더가 없으면 자동 생성
input_file = os.path.join(DATA_DIR, "processed_youtube_data.csv")  # 학습 데이터
model_file = os.path.join(MODEL_DIR, "youtube_model.pkl")  # 저장할 모델 파일

# 📌 1. 데이터 불러오기
df = pd.read_csv(input_file)

# 📌 2. 입력(X)과 출력(Y) 데이터 설정 (title 컬럼 제거)
X = df.drop(columns=["views", "category", "fetched_at"])  # 🎯 title(문자열 데이터)는 이미 제거된 상태
y = df["views"]  # 목표값 (조회수)

# 📌 3. 훈련 데이터(80%) & 테스트 데이터(20%)로 분할
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 📌 4. 랜덤포레스트 회귀 모델 생성 & 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 📌 5. 모델 평가 (테스트 데이터로 예측 & 오차 계산)
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"📢 평균 절대 오차 (MAE): {mae:.2f}") 

# 📌 6. 모델 저장 (backend/data/ 폴더에 저장)
joblib.dump(model, model_file)
print(f"✅ 모델이 {model_file}에 저장되었습니다!")
