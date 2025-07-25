<template>
  <div>
    <h2 class="page-title">取引一覧</h2>
    
    <!-- デスクトップ用のテーブル -->
    <table v-if="!isMobile" border="1" cellspacing="0" cellpadding="4" class="transaction-table">
      <thead>
        <tr>
          <th>使用日</th>
          <th style="text-align:center;">用途</th>
          <th style="text-align:center;">メモ</th>
          <th style="text-align:center;">金額</th>
          <th>支出元</th>
          <th>支払日</th>
          <th class="action-header">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="tx in sortedTransactions" 
          :key="tx.id" 
          class="table-row"
          @mouseenter="hoveredRow = tx.id"
          @mouseleave="hoveredRow = null"
        >
          <td>{{ tx.used_date }}</td>
          <td style="text-align:left;">{{ tx.purpose }}</td>
          <td style="text-align:left;"><span style="white-space: pre-line;">{{ tx.memo }}</span></td>
          <td style="text-align:right;">{{ formatAmount(tx.amount) }}円</td>
          <td>{{ getPaymentSourceName(tx.payment_source_id) }}</td>
          <td>{{ tx.paid_date }}</td>
          <td class="action-cell">
            <div v-if="hoveredRow === tx.id" class="action-buttons">
              <button 
                @click="editTransaction(tx)"
                class="action-btn edit-btn"
                title="編集"
              >
                ✏️
              </button>
              <button 
                @click="deleteTransactionDirect(tx)"
                class="action-btn delete-btn"
                title="削除"
              >
                🗑️
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- スマホ用のカード表示 -->
    <div v-else class="mobile-transactions">
      <div 
        v-for="tx in sortedTransactions" 
        :key="tx.id" 
        class="transaction-card"
        @click="editTransaction(tx)"
      >
        <div class="card-header">
          <span class="date">{{ tx.used_date }}</span>
          <span class="amount">{{ formatAmount(tx.amount) }}円</span>
        </div>
        <div class="card-body">
          <div class="purpose">{{ tx.purpose }}</div>
        </div>
      </div>
    </div>
    
    <!-- 登録ボタン -->
    <div class="register-button-container">
      <button 
        @click="showDialog = true"
        class="register-button"
      >
        ＋ 新規取引登録
      </button>
    </div>

    <!-- 全画面モーダルダイアログ（新規登録・編集共通） -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '取引編集' : '新規取引登録' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>
        
        <form @submit.prevent="isEditing ? updateTransaction() : addTransaction()" class="modal-form">
          <div class="form-group">
            <label for="used_date">使用日 *</label>
            <input 
              id="used_date"
              type="date" 
              v-model="form.used_date" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="purpose">用途 *</label>
            <input 
              id="purpose"
              v-model="form.purpose" 
              required 
              class="form-input"
              placeholder="例: 食費、交通費、雑費など"
            />
          </div>
          
          <div class="form-group">
            <label for="memo">メモ</label>
            <textarea 
              id="memo"
              v-model="form.memo" 
              rows="3" 
              class="form-textarea"
              placeholder="詳細なメモがあれば入力してください"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="amount">金額 *</label>
            <input 
              id="amount"
              type="number" 
              v-model.number="form.amount" 
              required 
              class="form-input"
              placeholder="0"
              min="0"
            />
          </div>
          
          <div class="form-group">
            <label for="payment_source">支出元 *</label>
            <select 
              id="payment_source"
              v-model.number="form.payment_source_id" 
              required 
              class="form-select"
            >
              <option value="">選択してください</option>
              <option v-for="source in paymentSources" :key="source.id" :value="source.id">
                {{ source.name }}
              </option>
            </select>
          </div>
          
          <div class="form-actions">
            <button 
              type="button" 
              @click="closeDialog"
              class="btn btn-secondary"
            >
              キャンセル
            </button>
            <button 
              v-if="isEditing"
              type="button"
              @click="deleteTransaction"
              class="btn btn-danger"
              :disabled="isSubmitting"
            >
              削除
            </button>
            <button 
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? (isEditing ? '更新中...' : '登録中...') : (isEditing ? '更新' : '登録') }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { buildApiUrl } from '../utils/api'

interface Transaction {
  id: number
  used_date: string
  purpose: string
  memo: string
  amount: number
  payment_source_id: number
  paid_date: string
  created_at: string
  updated_at: string
}

interface PaymentSource {
  id: number
  name: string
}

const transactions = ref<Transaction[]>([])
const paymentSources = ref<PaymentSource[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isMobile = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const hoveredRow = ref<number | null>(null)

const form = ref({
  used_date: '',
  purpose: '',
  memo: '',
  amount: 0,
  payment_source_id: 0,
})

const showDialog = ref(false)

// スマホ判定
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const fetchTransactions = async () => {
  try {
    const res = await fetch(buildApiUrl('/transactions'))
    if (!res.ok) throw new Error('取引取得に失敗しました')
    transactions.value = await res.json()
  } catch (e: any) {
    error.value = e.message
  }
}

const fetchPaymentSources = async () => {
  try {
    const res = await fetch(buildApiUrl('/payment_sources'))
    if (!res.ok) throw new Error('支出元取得に失敗しました')
    paymentSources.value = await res.json()
    if (paymentSources.value.length > 0 && form.value.payment_source_id === 0) {
      form.value.payment_source_id = paymentSources.value[0].id
    }
  } catch (e: any) {
    error.value = e.message
  }
}

const getPaymentSourceName = (id: number) => {
  const source = paymentSources.value.find(s => s.id === id)
  return source ? source.name : `ID:${id}`
}

const formatAmount = (amount: number) => {
  return amount.toLocaleString()
}

const resetForm = () => {
  form.value = { 
    used_date: '', 
    purpose: '', 
    memo: '', 
    amount: 0, 
    payment_source_id: paymentSources.value[0]?.id || 0 
  }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
  error.value = ''
}

const editTransaction = (transaction: Transaction) => {
  isEditing.value = true
  editingId.value = transaction.id
  form.value = {
    used_date: transaction.used_date,
    purpose: transaction.purpose,
    memo: transaction.memo || '',
    amount: transaction.amount,
    payment_source_id: transaction.payment_source_id,
  }
  showDialog.value = true
}

const deleteTransactionDirect = async (transaction: Transaction) => {
  if (!confirm(`「${transaction.purpose}」を削除しますか？`)) return
  
  error.value = ''
  isSubmitting.value = true
  
  try {
    const res = await fetch(buildApiUrl(`/transactions/${transaction.id}`), {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('削除に失敗しました')
    
    await fetchTransactions()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const addTransaction = async () => {
  error.value = ''
  isSubmitting.value = true
  
  try {
    const res = await fetch(buildApiUrl('/transactions'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('登録に失敗しました')
    
    // 成功時の処理
    closeDialog()
    await fetchTransactions()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateTransaction = async () => {
  if (!editingId.value) return
  
  error.value = ''
  isSubmitting.value = true
  
  try {
    const res = await fetch(buildApiUrl(`/transactions/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('更新に失敗しました')
    
    // 成功時の処理
    closeDialog()
    await fetchTransactions()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const deleteTransaction = async () => {
  if (!editingId.value) return
  
  if (!confirm('この取引を削除しますか？')) return
  
  error.value = ''
  isSubmitting.value = true
  
  try {
    const res = await fetch(buildApiUrl(`/transactions/${editingId.value}`), {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('削除に失敗しました')
    
    // 成功時の処理
    closeDialog()
    await fetchTransactions()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const sortedTransactions = computed(() => {
  return [...transactions.value].sort((a, b) => {
    if (a.used_date > b.used_date) return -1
    if (a.used_date < b.used_date) return 1
    // used_dateが同じ場合はcreated_atの降順
    if (a.created_at > b.created_at) return -1
    if (a.created_at < b.created_at) return 1
    return 0
  })
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchPaymentSources()
  fetchTransactions()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.page-title {
  text-align: center;
  margin: 16px 0 24px 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.transaction-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}

.transaction-table th,
.transaction-table td {
  padding: 12px 8px;
  border: 1px solid #ddd;
}

.transaction-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.action-header {
  width: 80px;
  text-align: center;
}

.action-cell {
  width: 80px;
  text-align: center;
  padding: 8px 4px !important;
}

.table-row {
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 16px;
  transition: all 0.2s;
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn:hover {
  background-color: #e3f2fd;
  transform: scale(1.1);
}

.delete-btn:hover {
  background-color: #ffebee;
  transform: scale(1.1);
}

.register-button-container {
  text-align: center;
  margin: 20px 0;
}

.register-button {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.register-button:hover {
  background-color: #45a049;
}

/* スマホ用のカード表示 */
.mobile-transactions {
  margin-bottom: 24px;
}

.transaction-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.transaction-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.transaction-card:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.date {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.amount {
  font-size: 16px;
  font-weight: bold;
  color: #d32f2f;
}

.card-body {
  margin-top: 8px;
}

.purpose {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  line-height: 1.4;
}

/* モーダル関連のスタイル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0 24px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-button:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-form {
  padding: 0 24px 24px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background-color: #e8e8e8;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

.btn-danger:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border: 1px solid #ffcdd2;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.2rem;
    margin: 12px 0 20px 0;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .modal-header,
  .modal-form {
    padding-left: 16px;
    padding-right: 16px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .register-button {
    width: 100%;
    max-width: 300px;
  }
}
</style>