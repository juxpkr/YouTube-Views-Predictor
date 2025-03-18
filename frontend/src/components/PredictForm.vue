<template>
  <div class="predict-form">
    <h2>조회수 예측</h2>
    <form @submit.prevent="predictViews">
      <label>업로드 요일 (0=월, 6=일)</label>
      <input v-model="day_of_week" type="number" min="0" max="6" required />

      <label>업로드 시간 (0~23)</label>
      <input v-model="hour" type="number" min="0" max="23" required />

      <label>제목 길이</label>
      <input v-model="title_length" type="number" min="1" required />

      <label>좋아요 수</label>
      <input v-model="likes" type="number" min="0" required />

      <label>댓글 수</label>
      <input v-model="comments" type="number" min="0" required />

      <button type="submit">예측하기</button>
    </form>

    <div v-if="loading" class="loading">⏳ 예측 중...</div>
    <div v-if="predictedViews !== null" class="result">
      <h3>📊 예상 조회수</h3>
      <p>{{ predictedViews.toLocaleString() }} 회</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      day_of_week: "",
      hour: "",
      title_length: "",
      likes: "",
      comments: "",
      predictedViews: null,
      loading: false,  // ✅ 로딩 상태 추가
    };
  },
  methods: {
    async predictViews() {
      this.loading = true;  // ✅ 로딩 시작
      try {
        const response = await axios.post("youtube-views-predictor-dafkdgc5eqamdabt.koreacentral-01.azurewebsites.net/predict", {
          day_of_week: this.day_of_week,
          hour: this.hour,
          title_length: this.title_length,
          likes: this.likes,
          comments: this.comments
        });
        this.predictedViews = response.data.predicted_views;
      } catch (error) {
        console.error("예측 요청 실패:", error);
      }
      this.loading = false;  // ✅ 로딩 완료
    },
  },
};
</script>

<style scoped>
.predict-form {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border-radius: 10px;
  background: #f9f9f9;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
}

label {
  display: block;
  font-weight: bold;
  margin-top: 10px;
}

input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 15px;
  width: 100%;
}

button:hover {
  background-color: #45a049;
}

.result {
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  margin-top: 20px;
  color: #333;
}

.loading {
  text-align: center;
  font-size: 16px;
  color: #777;
  margin-top: 10px;
}
.predict-form {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border-radius: 10px;
  background: #f9f9f9;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  color: #333; /* ✅ 추가: 기본 텍스트 색상을 어두운 회색으로 설정 */
}
</style>
