<template>
  <div>
    <h2 class="page-title">支出元管理</h2>

    <!-- 登録ボタン -->
    <div class="register-button-container">
      <button
        @click="showDialog = true"
        class="register-button"
      >
        ＋ 新規支出元登録
      </button>
    </div>

    <!-- デスクトップ用のテーブル -->
    <table v-if="!isMobile" border="1" cellspacing="0" cellpadding="4" class="payment-source-table">
      <thead>
        <tr>
          <th>名称</th>
          <th style="text-align:center;">締め日</th>
          <th style="text-align:center;">支払い月差分</th>
          <th style="text-align:center;">支払い日</th>
          <th class="action-header">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="source in paymentSources"
          :key="source.id"
          class="table-row"
          @mouseenter="hoveredRow = source.id"
          @mouseleave="hoveredRow = null"
        >
          <td>{{ source.name }}</td>
          <td style="text-align:center;">{{ source.closing_day }}日</td>
          <td style="text-align:center;">{{ source.pay_month_diff }}ヶ月</td>
          <td style="text-align:center;">{{ source.pay_day }}日</td>
                    <td class="action-cell">
            <div v-if="hoveredRow === source.id" class="action-buttons">
              <button
                @click="editPaymentSource(source)"
                class="action-btn edit-btn"
                title="編集"
              >
                ✏️
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- スマホ用のカード表示 -->
    <div v-else class="mobile-payment-sources">
      <div
        v-for="source in paymentSources"
        :key="source.id"
        class="payment-source-card"
        @click="editPaymentSource(source)"
      >
        <div class="card-header">
          <span class="name">{{ source.name }}</span>
        </div>
        <div class="card-body">
          <div class="detail-item">
            <span class="label">締め日:</span>
            <span class="value">{{ source.closing_day }}日</span>
          </div>
          <div class="detail-item">
            <span class="label">支払い月差分:</span>
            <span class="value">{{ source.pay_month_diff }}ヶ月</span>
          </div>
          <div class="detail-item">
            <span class="label">支払い日:</span>
            <span class="value">{{ source.pay_day }}日</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 全画面モーダルダイアログ（新規登録・編集共通） -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '支出元編集' : '新規支出元登録' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updatePaymentSource() : addPaymentSource()" class="modal-form">
          <div class="form-group">
            <label for="name">名称 *</label>
            <input
              id="name"
              type="text"
              v-model="form.name"
              required
              class="form-input"
              placeholder="例: クレジットカード、銀行口座など"
            />
          </div>

          <div class="form-group">
            <label for="closing_day">締め日 *</label>
            <input
              id="closing_day"
              type="number"
              v-model.number="form.closing_day"
              required
              class="form-input"
              placeholder="0"
              min="0"
              max="31"
            />
            <small class="form-help">0の場合は現金など、締め日がない場合</small>
          </div>

          <div class="form-group">
            <label for="pay_month_diff">支払い月までの差分 *</label>
            <input
              id="pay_month_diff"
              type="number"
              v-model.number="form.pay_month_diff"
              required
              class="form-input"
              placeholder="0"
              min="0"
            />
            <small class="form-help">締め日から何ヶ月後に支払いが発生するか</small>
          </div>

          <div class="form-group">
            <label for="pay_day">支払い日 *</label>
            <input
              id="pay_day"
              type="number"
              v-model.number="form.pay_day"
              required
              class="form-input"
              placeholder="0"
              min="0"
              max="31"
            />
            <small class="form-help">0の場合は使用日と同じ日に支払い</small>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { buildApiUrl } from '../utils/api'

interface PaymentSource {
  id: number
  name: string
  closing_day: number
  pay_month_diff: number
  pay_day: number
}

const paymentSources = ref<PaymentSource[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isMobile = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const hoveredRow = ref<number | null>(null)
const showDialog = ref(false)

const form = ref({
  name: '',
  closing_day: 0,
  pay_month_diff: 0,
  pay_day: 0,
})

// スマホ判定
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const fetchPaymentSources = async () => {
  try {
    const res = await fetch(buildApiUrl('/payment_sources'))
    if (!res.ok) throw new Error('支出元取得に失敗しました')
    paymentSources.value = await res.json()
  } catch (e: any) {
    error.value = e.message
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    closing_day: 0,
    pay_month_diff: 0,
    pay_day: 0,
  }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
  error.value = ''
}

const editPaymentSource = (source: PaymentSource) => {
  isEditing.value = true
  editingId.value = source.id
  form.value = {
    name: source.name,
    closing_day: source.closing_day,
    pay_month_diff: source.pay_month_diff,
    pay_day: source.pay_day,
  }
  showDialog.value = true
}



const addPaymentSource = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl('/payment_sources'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.value.name,
        closing_day: form.value.closing_day,
        pay_month_diff: form.value.pay_month_diff,
        pay_day: form.value.pay_day
      }),
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`登録に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    closeDialog()
    await fetchPaymentSources()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updatePaymentSource = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/payment_sources/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.value.name,
        closing_day: form.value.closing_day,
        pay_month_diff: form.value.pay_month_diff,
        pay_day: form.value.pay_day
      }),
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`更新に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    closeDialog()
    await fetchPaymentSources()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// コンポーネントマウント時にチェック
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchPaymentSources()
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

.payment-source-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}

.payment-source-table th,
.payment-source-table td {
  padding: 12px 8px;
  border: 1px solid #ddd;
}

.payment-source-table th {
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
.mobile-payment-sources {
  margin-bottom: 24px;
}

.payment-source-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.payment-source-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.payment-source-card:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  margin-bottom: 12px;
}

.name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
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
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
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

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-help {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #666;
  font-style: italic;
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