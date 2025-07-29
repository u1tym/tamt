<template>
  <div>
    <button class="back-btn" @click="goHome">トップメニューに戻る</button>
    <h2 class="page-title">出納管理</h2>

    <!-- PC用のタブ表示 -->
    <div v-if="!isMobile" class="tab-container">
      <button
        @click="currentTab = 'payment'"
        :class="['tab-button', { active: currentTab === 'payment' }]"
      >
        支出元管理
      </button>
      <button
        @click="currentTab = 'transaction'"
        :class="['tab-button', { active: currentTab === 'transaction' }]"
      >
        取引管理
      </button>
      <button
        @click="currentTab = 'budget'"
        :class="['tab-button', { active: currentTab === 'budget' }]"
      >
        予算管理
      </button>
    </div>

    <!-- コンポーネント表示 -->
    <PaymentSourceList v-if="!isMobile && currentTab === 'payment'" />
    <TransactionList v-else-if="!isMobile && currentTab === 'transaction'" />
    <BudgetList v-else-if="!isMobile && currentTab === 'budget'" />
    <TransactionList v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import PaymentSourceList from './PaymentSourceList.vue'
import TransactionList from './TransactionList.vue'
import BudgetList from './BudgetList.vue'

const router = useRouter()
const currentTab = ref<'payment' | 'transaction' | 'budget'>('transaction')

// スマホ判定
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

function goHome() {
  router.push('/')
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.back-btn {
  background-color: #666;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 16px;
  font-size: 14px;
}

.back-btn:hover {
  background-color: #555;
}

.page-title {
  text-align: center;
  margin: 16px 0 24px 0;
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
  .page-title {
    font-size: 1.2rem;
    margin: 12px 0 20px 0;
  }
}
</style> 