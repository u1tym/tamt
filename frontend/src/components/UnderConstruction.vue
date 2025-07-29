<template>
  <div class="under-construction">
    <h2>工事中</h2>
    <button class="back-btn" @click="goHome">トップメニューに戻る</button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
function goHome() {
  router.push('/')
}
</script>

<style scoped>
.under-construction {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 100px;
}
.back-btn {
  margin-top: 32px;
  padding: 12px 32px;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  background: #4CAF50;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.back-btn:hover {
  background: #388e3c;
}
</style> 