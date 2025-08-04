<template>
  <div class="cash-management">

    <div class="header-container">
      <div class="header-left">
        <img src="/images/MONEY.jpg" alt="MONEY" class="header-icon" />
        <h2 class="page-title">出納</h2>
      </div>
      <div class="header-right">
        <!--<img 
          src="/images/CONFIG.jpg" 
          alt="CONFIG" 
          class="config-icon" 
          @click="toggleEditMode"
          title="編集モード切り替え"
        />-->
        <img 
          src="/images/PORTAL.jpg" 
          alt="PORTAL" 
          class="portal-icon" 
          @click="$router.push('/menu')"
          title="トップメニューに戻る"
        />
      </div>
    </div>

    <!-- PC用のタブ表示 -->
    <div v-if="!isMobile" class="tab-container">
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
      <button
        @click="currentTab = 'payment'"
        :class="['tab-button', { active: currentTab === 'payment' }]"
      >
        支出元管理
      </button>
      <button
        @click="currentTab = 'debit'"
        :class="['tab-button', { active: currentTab === 'debit' }]"
      >
        支払管理
      </button>
    </div>

    <!-- コンポーネント表示 -->
    <PaymentSourceList v-if="!isMobile && currentTab === 'payment'" />
    <TransactionList v-else-if="!isMobile && currentTab === 'transaction'" />
    <BudgetList v-else-if="!isMobile && currentTab === 'budget'" />
    <DebitList v-else-if="!isMobile && currentTab === 'debit'" />
    <TransactionList v-else />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import PaymentSourceList from './PaymentSourceList.vue'
import TransactionList from './TransactionList.vue'
import BudgetList from './BudgetList.vue'
import DebitList from './DebitList.vue'
const currentTab = ref<'payment' | 'transaction' | 'budget' | 'debit'>('transaction')

// スマホ判定
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// Removed unused goHome function

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.cash-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
  border-bottom: 2px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.config-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 2px solid transparent;
  margin-right: 10px; /* ポータルアイコンとの間隔 */
}

.config-icon:hover {
  transform: scale(1.1);
  border-color: #8B4513;
}

.portal-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 2px solid transparent;
}

.portal-icon:hover {
  transform: scale(1.1);
  border-color: #8B4513;
}

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