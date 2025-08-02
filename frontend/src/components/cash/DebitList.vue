<template>
  <div class="debit-list">
    <div class="under-construction">
      <h3>工事中</h3>
      <p>この機能は現在開発中です。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Component logic will be added here when needed
</script>

<style scoped>
.debit-list {
  padding: 20px;
}

.under-construction {
  text-align: center;
  padding: 60px 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.under-construction h3 {
  color: #6c757d;
  font-size: 1.5rem;
  margin-bottom: 16px;
}

.under-construction p {
  color: #6c757d;
  font-size: 1rem;
  margin: 0;
}
</style> 