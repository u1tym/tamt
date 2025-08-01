<template>
  <div class="schedule-weekly">
    <div class="construction-message">
      <h2>週間表示</h2>
      <div class="construction-content">
        <div class="construction-icon">🚧</div>
        <p>工事中</p>
        <p>週間表示機能は現在開発中です</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 週間表示のロジックは今後実装予定
</script>

<style scoped>
.schedule-weekly {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.construction-message {
  text-align: center;
  padding: 60px 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 2px dashed #ccc;
}

.construction-content {
  margin-top: 20px;
}

.construction-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.construction-message h2 {
  color: #333;
  margin-bottom: 10px;
}

.construction-message p {
  color: #666;
  margin: 5px 0;
  font-size: 16px;
}
</style> 