<template>
  <div class="debit-list">
    <h2 class="page-title">支払管理</h2>
    
    <!-- ローディング表示 -->
    <div v-if="loading" class="loading">
      <p>データを読み込み中...</p>
    </div>
    
    <!-- エラー表示 -->
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
    
    <!-- データ表示 -->
    <div v-else>
      <!-- デスクトップ用のテーブル -->
      <div v-if="!isMobile" class="table-container">
        <table class="debit-table">
          <thead>
            <tr>
              <th style="text-align:center;">支払日</th>
              <th style="text-align:center;">支払元</th>
              <th style="text-align:center;">取引件数</th>
              <th style="text-align:center;">合計金額</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in debitSummary"
              :key="`${item.payment_date}-${item.source_name}`"
              class="table-row"
            >
              <td style="text-align:center;">{{ formatDate(item.payment_date) }}</td>
              <td style="text-align:center;">{{ item.source_name }}</td>
              <td style="text-align:center;">{{ item.transaction_count }}件</td>
              <td style="text-align:right;">{{ formatAmount(item.total_amount) }}円</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- スマホ用のカード表示 -->
      <div v-else class="mobile-debit-list">
        <div
          v-for="item in debitSummary"
          :key="`${item.payment_date}-${item.source_name}`"
          class="debit-card"
        >
          <div class="card-header">
            <span class="payment-date">{{ formatDate(item.payment_date) }}</span>
            <span class="source-name">{{ item.source_name }}</span>
          </div>
          <div class="card-body">
            <div class="detail-item">
              <span class="label">取引件数:</span>
              <span class="value">{{ item.transaction_count }}件</span>
            </div>
            <div class="detail-item">
              <span class="label">合計金額:</span>
              <span class="value amount">{{ formatAmount(item.total_amount) }}円</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- データが空の場合 -->
      <div v-if="debitSummary.length === 0" class="no-data">
        <p>表示する支払データがありません。</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { buildApiUrl } from '../../utils/api'

interface DebitSummaryItem {
  payment_date: string
  source_name: string
  total_amount: number
  transaction_count: number
}

const debitSummary = ref<DebitSummaryItem[]>([])
const loading = ref(true)
const error = ref('')
const isMobile = ref(false)

// スマホ判定
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// データ取得
const fetchDebitSummary = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await fetch(buildApiUrl('/debit-summary'))
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    debitSummary.value = data
  } catch (err) {
    console.error('Error fetching debit summary:', err)
    error.value = 'データの取得に失敗しました。'
  } finally {
    loading.value = false
  }
}

// 日付フォーマット
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}/${month}/${day}`
}

// 金額フォーマット
const formatAmount = (amount: number): string => {
  return amount.toLocaleString()
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchDebitSummary()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.debit-list {
  padding: 20px;
}

.page-title {
  margin-bottom: 24px;
  font-size: 1.8rem;
  color: #333;
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  border: 1px solid #ffcdd2;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  background-color: #f5f5f5;
  border-radius: 8px;
}

/* デスクトップ用テーブル */
.table-container {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.table-container::-webkit-scrollbar {
  display: none;
}

.debit-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  margin-bottom: 0;
}

.debit-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f5f5f5;
}

.debit-table th {
  padding: 12px 8px;
  border-bottom: 2px solid #e0e0e0;
  font-weight: 600;
  color: #333;
}

.debit-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #e0e0e0;
}

.debit-table tbody tr:hover {
  background-color: #f8f9fa;
}

/* スマホ用カード */
.mobile-debit-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.debit-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e0e0e0;
}

.payment-date {
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.source-name {
  font-weight: 500;
  color: #666;
  background-color: #e3f2fd;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  color: #666;
  font-size: 0.9rem;
}

.value {
  font-weight: 500;
  color: #333;
}

.value.amount {
  font-weight: 600;
  color: #d32f2f;
  font-size: 1.1rem;
}

/* スマホ用のスタイル */
@media (max-width: 768px) {
  .debit-list {
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
    margin-bottom: 20px;
  }
  
  .debit-card {
    padding: 12px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .payment-date {
    font-size: 1rem;
  }
  
  .source-name {
    font-size: 0.8rem;
  }
}
</style> 