<template>
  <div class="top-menu">
    <h1 class="menu-title">トップメニュー</h1>
    <div class="menu-buttons">
      <button class="menu-btn" @click="goTo('knowhow')">KNOWHOW管理</button>
      <button class="menu-btn" @click="goTo('goods')">GOODS管理</button>
      <button class="menu-btn" @click="goTo('transactions')">出納管理</button>
      <button class="menu-btn" @click="goTo('schedule')">スケジュール管理</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()

function goTo(page: string) {
  if (page === 'knowhow') {
    router.push('/knowhow')
  } else if (page === 'goods') {
    router.push('/goods')
  } else if (page === 'transactions') {
    router.push('/transactions')
  } else if (page === 'schedule') {
    router.push('/schedule')
  }
}
</script>

<style scoped>
.top-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 60px;
}
.menu-title {
  font-size: 2rem;
  margin-bottom: 40px;
  color: #333;
}
.menu-buttons {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 300px;
}
.menu-btn {
  padding: 20px 0;
  font-size: 1.2rem;
  border: none;
  border-radius: 8px;
  background: #4CAF50;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.menu-btn:hover {
  background: #388e3c;
}
</style>