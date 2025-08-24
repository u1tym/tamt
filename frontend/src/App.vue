<script setup lang="ts">
import ApiStatusMonitor from './components/ApiStatusMonitor.vue'
// This file now only serves as a router view container
</script>

<template>
  <router-view />
  <ApiStatusMonitor />
</template>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.app-title {
  text-align: center;
  margin: 16px 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.tab-container {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  color: #666;
  border-radius: 4px;
  transition: all 0.2s;
}

.tab-button:hover {
  background-color: #f5f5f5;
  color: #333;
}

.tab-button.active {
  background-color: #4CAF50;
  color: white;
}

.tab-button.active:hover {
  background-color: #45a049;
}

/* スマホ用のスタイル */
@media (max-width: 768px) {
  .app-container {
    padding: 0 12px;
  }

  .app-title {
    font-size: 1.2rem;
    margin: 12px 0;
  }
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
