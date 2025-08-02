<template>
  <div>
    <h2 class="page-title">予算管理</h2>

    <!-- 年月選択 -->
    <div class="year-month-selector">
      <div class="selector-group">
        <label for="target-year">対象年:</label>
        <select id="target-year" v-model.number="selectedYear" @change="fetchBudgets" class="form-select">
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}年
          </option>
        </select>
      </div>
      <div class="selector-group">
        <label for="target-month">対象月:</label>
        <select id="target-month" v-model.number="selectedMonth" @change="fetchBudgets" class="form-select">
          <option v-for="month in 12" :key="month" :value="month">
            {{ month }}月
          </option>
        </select>
      </div>
      <div class="period-display">
        対象期間：{{ formatPeriod(selectedYear, selectedMonth) }}
      </div>
    </div>

    <!-- 登録ボタン -->
    <div class="register-button-container">
      <button
        @click="showDialog = true"
        class="register-button"
      >
        ＋ 新規予算登録
      </button>
      <button
        @click="showCopyDialog = true"
        class="copy-button"
      >
        📋 他月からコピー
      </button>
    </div>

    <!-- 予算一覧テーブル -->
    <div class="table-container">
      <table border="1" cellspacing="0" cellpadding="4" class="budget-table">
        <thead>
          <tr>
            <th style="text-align:center; width: 40%;">名称</th>
            <th style="text-align:center; width: 15%;">金額</th>
            <th style="text-align:center; width: 15%;">集計金額</th>
            <th class="action-header" style="width: 15%;">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="budget in budgets"
            :key="budget.id"
            class="table-row"
            @mouseenter="hoveredRow = budget.id"
            @mouseleave="hoveredRow = null"
          >
            <td style="width: 40%;">{{ budget.name }}</td>
            <td style="text-align:right; width: 15%;">{{ formatAmount(budget.amount) }}円</td>
            <td style="text-align:right; width: 15%;">{{ formatAmount(getSummaryAmount(budget.name)) }}円</td>
            <td class="action-cell" style="width: 15%;">
              <div v-if="hoveredRow === budget.id" class="action-buttons">
                              <button
                  @click="moveBudgetUp(budget)"
                  class="action-btn move-up-btn"
                  title="上に移動"
                  :disabled="isFirstBudget(budget)"
                >
                  ⬆️
                </button>
                              <button
                  @click="moveBudgetDown(budget)"
                  class="action-btn move-down-btn"
                  title="下に移動"
                  :disabled="isLastBudget(budget)"
                >
                  ⬇️
                </button>
                <button
                  @click="editBudget(budget)"
                  class="action-btn edit-btn"
                  title="編集"
                >
                  ✏️
                </button>
                <button
                  @click="deleteBudget(budget)"
                  class="action-btn delete-btn"
                  title="削除"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
          <tr class="table-row unclassified-row">
            <td style="width: 40%;">未分類</td>
            <td style="width: 15%;"></td>
            <td style="text-align:right; width: 15%;">{{ formatAmount(getSummaryAmount('未分類')) }}円</td>
            <td class="action-cell" style="width: 15%;"></td>
          </tr>
          <tr class="table-row total-row">
            <td style="width: 40%; text-align: right; font-weight: bold;">合計</td>
            <td style="text-align:right; width: 15%; font-weight: bold;">{{ formatAmount(totalAmount) }}円</td>
            <td style="text-align:right; width: 15%; font-weight: bold;">{{ formatAmount(totalSummaryAmount + getSummaryAmount('未分類')) }}円</td>
            <td class="action-cell" style="width: 15%;"></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 予算登録・編集モーダル -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '予算編集' : '新規予算登録' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updateBudget() : addBudget()" class="modal-form">
          <div class="form-group">
            <label for="name">名称 *</label>
            <input
              id="name"
              type="text"
              v-model="form.name"
              required
              class="form-input"
              placeholder="例: 食費、交通費、雑費など"
            />
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
              @click="deleteBudgetFromDialog"
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

    <!-- コピーモーダル -->
    <div v-if="showCopyDialog" class="modal-overlay" @click="closeCopyDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>他月からコピー</h3>
          <button class="close-button" @click="closeCopyDialog">&times;</button>
        </div>

        <form @submit.prevent="copyBudgets" class="modal-form">
          <div class="form-group">
            <label>コピー元</label>
            <div class="copy-source">
              <div class="selector-group">
                <label for="source-year">年:</label>
                <select id="source-year" v-model.number="copyForm.sourceYear" class="form-select">
                  <option v-for="year in availableYears" :key="year" :value="year">
                    {{ year }}年
                  </option>
                </select>
              </div>
              <div class="selector-group">
                <label for="source-month">月:</label>
                <select id="source-month" v-model.number="copyForm.sourceMonth" class="form-select">
                  <option v-for="month in 12" :key="month" :value="month">
                    {{ month }}月
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>コピー先</label>
            <div class="copy-target">
              <div class="selector-group">
                <label for="target-year-copy">年:</label>
                <select id="target-year-copy" v-model.number="copyForm.targetYear" class="form-select">
                  <option v-for="year in availableYears" :key="year" :value="year">
                    {{ year }}年
                  </option>
                </select>
              </div>
              <div class="selector-group">
                <label for="target-month-copy">月:</label>
                <select id="target-month-copy" v-model.number="copyForm.targetMonth" class="form-select">
                  <option v-for="month in 12" :key="month" :value="month">
                    {{ month }}月
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button
              type="button"
              @click="closeCopyDialog"
              class="btn btn-secondary"
            >
              キャンセル
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'コピー中...' : 'コピー実行' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { buildApiUrl } from '../../utils/api'

interface Budget {
  id: number
  target_year: number
  target_month: number
  name: string
  amount: number
  created_at: string
  updated_at: string
  order_index: number
}

const budgets = ref<Budget[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const hoveredRow = ref<number | null>(null)
const showDialog = ref(false)
const showCopyDialog = ref(false)
const budgetSummaries = ref<{ [name: string]: number }>({})

// 現在の年月を初期値に設定
const currentDate = new Date()
const selectedYear = ref(currentDate.getFullYear())
const selectedMonth = ref(currentDate.getMonth() + 1)

// 利用可能な年（現在年から前後5年）
const availableYears = computed(() => {
  const currentYear = currentDate.getFullYear()
  const years = []
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    years.push(i)
  }
  return years
})

const form = ref({
  name: '',
  amount: 0,
})

const copyForm = ref({
  sourceYear: currentDate.getFullYear(),
  sourceMonth: currentDate.getMonth() + 1,
  targetYear: currentDate.getFullYear(),
  targetMonth: currentDate.getMonth() + 1,
})

const fetchBudgetSummaries = async () => {
  try {
    const res = await fetch(buildApiUrl(`/budgets/${selectedYear.value}/${selectedMonth.value}/summary`))
    if (!res.ok) throw new Error('集計取得に失敗')
    const data = await res.json()
    const map: { [name: string]: number } = {}
    for (const item of data) {
      map[item.name] = item.total
    }
    budgetSummaries.value = map
  } catch {
    budgetSummaries.value = {}
  }
}

const getSummaryAmount = (name: string) => {
  return budgetSummaries.value[name] || 0
}

// fetchBudgetsの後にfetchBudgetSummariesも呼ぶ
const fetchBudgets = async () => {
  try {
    const res = await fetch(buildApiUrl(`/budgets/${selectedYear.value}/${selectedMonth.value}`))
    if (!res.ok) throw new Error('予算取得に失敗しました')
    budgets.value = await res.json()
    await fetchBudgetSummaries()
  } catch (e: any) {
    error.value = e.message
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    amount: 0,
  }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
  error.value = ''
}

const closeCopyDialog = () => {
  showCopyDialog.value = false
  error.value = ''
}

const editBudget = (budget: Budget) => {
  isEditing.value = true
  editingId.value = budget.id
  form.value = {
    name: budget.name,
    amount: budget.amount,
  }
  showDialog.value = true
}

const deleteBudget = async (budget: Budget) => {
  if (!confirm(`「${budget.name}」を削除しますか？`)) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/budgets/${budget.id}`), {
      method: 'DELETE',
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`削除に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const deleteBudgetFromDialog = async () => {
  if (!editingId.value) return

  if (!confirm('この予算を削除しますか？')) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/budgets/${editingId.value}`), {
      method: 'DELETE',
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`削除に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    closeDialog()
    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const isFirstBudget = (budget: Budget) => {
  // order_indexが最小のものを最初の予算とする
  const minOrderIndex = Math.min(...budgets.value.map(b => b.order_index))
  return budget.order_index === minOrderIndex
}

const moveBudgetUp = async (budget: Budget) => {
  if (isFirstBudget(budget)) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/budgets/${budget.id}/move-up`), {
      method: 'POST',
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`上移動に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const isLastBudget = (budget: Budget) => {
  // order_indexが最大のものを最後の予算とする
  const maxOrderIndex = Math.max(...budgets.value.map(b => b.order_index))
  return budget.order_index === maxOrderIndex
}

const moveBudgetDown = async (budget: Budget) => {
  if (isLastBudget(budget)) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/budgets/${budget.id}/move-down`), {
      method: 'POST',
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`下移動に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const addBudget = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl('/budgets'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_year: selectedYear.value,
        target_month: selectedMonth.value,
        name: form.value.name,
        amount: form.value.amount
      }),
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`登録に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    closeDialog()
    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateBudget = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/budgets/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.value.name,
        amount: form.value.amount
      }),
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`更新に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    closeDialog()
    await fetchBudgets()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const copyBudgets = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const params = new URLSearchParams({
      source_year: copyForm.value.sourceYear.toString(),
      source_month: copyForm.value.sourceMonth.toString(),
      target_year: copyForm.value.targetYear.toString(),
      target_month: copyForm.value.targetMonth.toString(),
    })

    const res = await fetch(buildApiUrl(`/budgets/copy?${params}`), {
      method: 'POST',
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`コピーに失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    const result = await res.json()
    alert(result.message)

    // コピー先の年月に切り替えて予算を表示
    selectedYear.value = copyForm.value.targetYear
    selectedMonth.value = copyForm.value.targetMonth
    await fetchBudgets()

    closeCopyDialog()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const formatAmount = (amount: number) => {
  return amount.toLocaleString()
}

const formatPeriod = (year: number, month: number) => {
  // 対象月の23日から翌月の22日まで
  const startDate = new Date(year, month - 1, 23) // monthは0ベースなので-1
  const endDate = new Date(year, month, 22) // 翌月の22日

  const startYear = startDate.getFullYear()
  const startMonth = startDate.getMonth() + 1
  const startDay = startDate.getDate()

  const endYear = endDate.getFullYear()
  const endMonth = endDate.getMonth() + 1
  const endDay = endDate.getDate()

  return `${startYear}年${startMonth}月${startDay}日～${endYear}年${endMonth}月${endDay}日`
}

const totalAmount = computed(() => {
  return budgets.value.reduce((sum, budget) => sum + budget.amount, 0)
})

const totalSummaryAmount = computed(() => {
  // 予算名ごとの集計金額の合計（未分類は除く）
  return Object.entries(budgetSummaries.value)
    .filter(([name]) => name !== '未分類')
    .reduce((sum, [, value]) => sum + value, 0)
})

onMounted(() => {
  fetchBudgets()
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

.year-month-selector {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.selector-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-group label {
  font-weight: 500;
  color: #333;
  min-width: 60px;
}

.period-display {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background: #e8f5e8;
  border: 1px solid #4CAF50;
  border-radius: 4px;
  color: #2e7d32;
  font-weight: 500;
  font-size: 14px;
  white-space: nowrap;
}

.form-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.form-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.table-container {
  margin-bottom: 24px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.table-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.budget-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 0;
}

.budget-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f5f5f5;
}

.budget-table th,
.budget-table td {
  padding: 12px 8px;
  border: 1px solid #ddd;
}

.budget-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.action-header {
  width: 15%;
  text-align: center;
}

.action-cell {
  width: 15%;
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

.move-up-btn:hover {
  background-color: #e8f5e8;
  transform: scale(1.1);
}

.move-up-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.move-down-btn:hover {
  background-color: #e8f5e8;
  transform: scale(1.1);
}

.move-down-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
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
  display: flex;
  gap: 12px;
  justify-content: center;
}

.register-button,
.copy-button {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.register-button {
  background-color: #4CAF50;
  color: white;
}

.register-button:hover {
  background-color: #45a049;
}

.copy-button {
  background-color: #2196F3;
  color: white;
}

.copy-button:hover {
  background-color: #1976D2;
}

.total-section {
  text-align: right;
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.total-amount {
  font-size: 18px;
  font-weight: bold;
  color: #333;
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

.copy-source,
.copy-target {
  display: flex;
  gap: 16px;
  margin-top: 8px;
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

.unclassified-row td {
  background: #f8f9fa;
  font-weight: 600;
}

.total-row td {
  background: #f8f9fa;
  font-weight: 600;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.2rem;
    margin: 12px 0 20px 0;
  }

  .year-month-selector {
    flex-direction: column;
    gap: 12px;
  }

  .register-button-container {
    flex-direction: column;
    align-items: center;
  }

  .register-button,
  .copy-button {
    width: 100%;
    max-width: 300px;
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

  .copy-source,
  .copy-target {
    flex-direction: column;
    gap: 8px;
  }
}
</style>