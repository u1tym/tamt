<template>
  <div class="goods-management">
    <div class="header">
      <div class="header-left">
        <img src="/images/GOODS.png" alt="GOODS" class="header-icon" />
        <h1>GOODS</h1>
      </div>
      <div class="header-right">
                 <img 
           src="/images/CONFIG.png" 
           alt="CONFIG" 
           class="config-icon" 
           @click="toggleTabs"
           title="設定"
         />
        <img 
          src="/images/PORTAL.png" 
          alt="PORTAL" 
          class="portal-icon" 
          @click="goToTopMenu"
          title="トップメニューに戻る"
        />
      </div>
    </div>

         <!-- タブナビゲーション -->
     <div class="tab-navigation" v-if="showTabs">
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
       <!-- アーティスト管理 -->
       <div v-if="activeTab === 'artists'" class="tab-panel">
         <ArtistManagement />
       </div>

       <!-- パーソン管理 -->
       <div v-if="activeTab === 'persons'" class="tab-panel">
         <PersonManagement />
       </div>

       <!-- メディア管理 -->
       <div v-if="activeTab === 'media'" class="tab-panel">
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
const showConfigModal = ref(false)
const showTabs = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// タブ設定
const tabs = [
  { id: 'artists', name: 'アーティスト管理' },
  { id: 'persons', name: 'パーソン管理' },
  { id: 'media', name: 'メディア管理' }
]

const activeTab = ref('goods')

// タブの表示/非表示を切り替える
const toggleTabs = () => {
  showTabs.value = !showTabs.value
  if (showTabs.value) {
    // タブが表示されたらアーティスト管理を選択
    activeTab.value = 'artists'
  } else {
    // タブが非表示になったらアイテム管理を選択
    activeTab.value = 'goods'
  }
}

// トップメニューへ戻る
const goToTopMenu = () => {
  router.push('/')
}

// ライフサイクル
onMounted(() => {
  checkMobile()
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.header-left h1 {
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