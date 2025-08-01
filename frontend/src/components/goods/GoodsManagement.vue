<template>
  <div class="goods-management">
    <!-- トップメニューへ戻るボタン -->
    <div class="back-button-container">
      <button @click="goToTopMenu" class="back-btn">
        ← トップメニューへ戻る
      </button>
    </div>

    <!-- タイトル -->
    <h1 class="page-title">{{ isMobile ? 'GOODS管理（アイテム管理）' : 'GOODS管理' }}</h1>

    <!-- タブナビゲーション -->
    <div class="tab-navigation" v-if="!isMobile">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        {{ tab.name }}
      </button>
    </div>

    <!-- タブコンテンツ -->
    <div class="tab-content">
      <!-- パーソン管理 -->
      <div v-if="!isMobile && activeTab === 'persons'" class="tab-panel">
        <PersonManagement />
      </div>

      <!-- アーティスト管理 -->
      <div v-if="!isMobile && activeTab === 'artists'" class="tab-panel">
        <ArtistManagement />
      </div>

      <!-- メディア管理 -->
      <div v-if="!isMobile && activeTab === 'media'" class="tab-panel">
        <MediaManagement />
      </div>

      <!-- アイテム管理 -->
      <div v-if="activeTab === 'goods'" class="tab-panel">
        <GoodsList />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import PersonManagement from './PersonManagement.vue'
import ArtistManagement from './ArtistManagement.vue'
import MediaManagement from './MediaManagement.vue'
import GoodsList from './GoodsList.vue'

const router = useRouter()

// モバイル判定
const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// タブ設定
const tabs = [
  { id: 'persons', name: 'パーソン管理' },
  { id: 'artists', name: 'アーティスト管理' },
  { id: 'media', name: 'メディア管理' },
  { id: 'goods', name: 'アイテム管理' }
]

const activeTab = ref('persons')

// モバイルの場合はアイテム管理タブをデフォルトに設定
const initializeActiveTab = () => {
  if (isMobile.value) {
    activeTab.value = 'goods'
  } else {
    activeTab.value = 'persons'
  }
}

// トップメニューへ戻る
const goToTopMenu = () => {
  router.push('/')
}

// ライフサイクル
onMounted(() => {
  checkMobile()
  initializeActiveTab()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.goods-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.back-button-container {
  margin-bottom: 20px;
}

.back-btn {
  padding: 12px 24px;
  font-size: 16px;
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

.page-title {
  text-align: center;
  margin: 20px 0 30px 0;
  font-size: 2rem;
  color: #333;
  font-weight: 600;
}

.tab-navigation {
  display: flex;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 30px;
  overflow-x: auto;
}

.tab-button {
  padding: 15px 25px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  color: #4CAF50;
  background-color: #f8f9fa;
}

.tab-button.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
  background-color: #f8f9fa;
}

.tab-content {
  min-height: 500px;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .goods-management {
    padding: 10px;
  }

  .page-title {
    font-size: 1.5rem;
    margin: 15px 0 20px 0;
  }

  .tab-navigation {
    margin-bottom: 20px;
  }

  .tab-button {
    padding: 12px 16px;
    font-size: 14px;
  }
}
</style> 