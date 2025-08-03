<template>
  <div class="top-menu">
    <h1 class="menu-title">PORTAL</h1>
         <div class="menu-icons">
       <div class="icon-row">
         <div class="icon-item" @click="goTo('knowhow')" title="KNOWHOW管理">
           <div class="icon-wrapper">
             <img src="/images/KNOWHOW.jpg" alt="KNOWHOW" class="icon-image" />
           </div>
           <span class="icon-label">KNOWHOW</span>
         </div>
         
         <div class="icon-item" @click="goTo('goods')" title="GOODS管理">
           <div class="icon-wrapper">
             <img src="/images/GOODS.jpg" alt="GOODS" class="icon-image" />
           </div>
           <span class="icon-label">GOODS</span>
         </div>
       </div>
       
       <div class="icon-row">
         <div class="icon-item" @click="goTo('transactions')" title="出納管理">
           <div class="icon-wrapper">
             <img src="/images/MONEY.jpg" alt="出納" class="icon-image" />
           </div>
           <span class="icon-label">出納</span>
         </div>
         
         <div class="icon-item" @click="goTo('schedule')" title="スケジュール管理">
           <div class="icon-wrapper">
             <img src="/images/SCHEDULE.jpg" alt="スケジュール" class="icon-image" />
           </div>
           <span class="icon-label">スケジュール</span>
         </div>
         
         <div class="icon-item" @click="goTo('holidays')" title="休日管理">
           <div class="icon-wrapper">
             <img src="/images/HOLIDAY.jpg" alt="休日" class="icon-image" />
           </div>
           <span class="icon-label">休日</span>
         </div>
       </div>
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
  } else if (page === 'holidays') {
    router.push('/holidays')
  }
}
</script>

<style scoped>
.top-menu {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 60px;
  padding: 0 20px;
}

.menu-title {
  font-size: 2rem;
  margin-bottom: 40px;
  color: #333;
  font-weight: 600;
}

.menu-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  max-width: 800px;
}

.icon-row {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 16px;
  border-radius: 16px;
  transition: all 0.3s ease;
  min-width: 100px;
}

.icon-item:hover {
  background: rgba(139, 69, 19, 0.1);
  transform: translateY(-2px);
}

.icon-wrapper {
  width: 100px;
  height: 100px;
  background: white;
  border: 3px solid #8B4513;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
}

.icon-item:hover .icon-wrapper {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(139, 69, 19, 0.4);
  border-color: #A0522D;
}

.icon-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
}

.icon-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  text-align: center;
  line-height: 1.2;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .menu-icons {
    gap: 20px;
  }
  
  .icon-row {
    gap: 20px;
  }
  
  .icon-item {
    min-width: 100px;
    padding: 12px;
  }
  
  .icon-wrapper {
    width: 80px;
    height: 80px;
  }
  
  .icon-image {
    width: 80px;
    height: 80px;
    border-radius: 50%;
  }
  
  .icon-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .menu-icons {
    gap: 16px;
  }
  
  .icon-row {
    gap: 16px;
  }
  
  .icon-item {
    min-width: 80px;
    padding: 8px;
  }
  
  .icon-wrapper {
    width: 70px;
    height: 70px;
  }
  
  .icon-image {
    width: 70px;
    height: 70px;
    border-radius: 50%;
  }
  
  .icon-label {
    font-size: 11px;
  }
}
</style>