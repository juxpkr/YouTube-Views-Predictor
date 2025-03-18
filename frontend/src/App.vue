<template>
  <div id="app">
    <h1>YouTube 조회수 예측기</h1>
    
  </div>
  <div>
    <PredictForm />
  </div>
</template>

<script>
import PredictForm from "./components/PredictForm.vue";  // ✅ PredictForm 불러오기

export default {
  components: {
    PredictForm,  // ✅ Vue 컴포넌트 등록
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  margin-top: 50px;
}
</style>
