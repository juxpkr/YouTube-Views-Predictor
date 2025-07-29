import pandas as pd
import joblib

# 저장된 모델 불러오기
model = joblib.load("youtube_model.pkl")

# 예측할 새로운 영상 데이터 입력 (임의의 예제)
new_video = pd.DataFrame({
    "likes": [50000],        # 좋아요 수
    "comments": [2000],      # 댓글 수
    "day_of_week": [5],      # 업로드 요일 (금요일)
    "hour": [18],            # 업로드 시간 (오후 6시)
    "title_length": [35]     # 제목 길이
})

# 조회수 예측
predicted_views = model.predict(new_video)
print(f"예측된 조회수: {int(predicted_views[0]):,}회")
