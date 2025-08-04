<template>
  <div class="holiday-management">
    <div class="header">
      <h1>休日管理</h1>
      <button class="back-btn" @click="goBack">← 戻る</button>
    </div>

    <div class="main-content">
      <div class="holiday-controls">
        <button class="add-holiday-btn" @click="showHolidayModal = true">休日を追加</button>
      </div>

      <div class="holiday-list-container">
        <div class="holiday-list">
          <div v-for="holiday in holidays" :key="holiday.id" class="holiday-item">
            <span class="holiday-date">{{ formatHolidayDate(holiday.date) }}</span>
            <span class="holiday-name">{{ holiday.name }}</span>
            <button class="delete-btn" @click="deleteHoliday(holiday.id)" title="削除">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 休日追加モーダル -->
    <div v-if="showHolidayModal" class="modal-overlay" @wheel.prevent>
      <div class="modal-content" @click.stop @wheel.stop>
        <h3>休日を追加</h3>
        <form @submit.prevent="saveHoliday">
          <div class="form-group">
            <label>日付:</label>
            <input type="date" v-model="holidayForm.date" required />
          </div>

          <div class="form-group">
            <label>休日名称:</label>
            <input v-model="holidayForm.name" required />
          </div>

          <div class="form-actions">
            <button type="button" @click="closeHolidayModal">キャンセル</button>
            <button type="submit">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHolidays, createHoliday, deleteHoliday as apiDeleteHoliday } from '../../utils/api'

const router = useRouter()

// 状態管理
const holidays = ref<any[]>([])
const showHolidayModal = ref(false)
const holidayForm = ref({
  date: '',
  name: ''
})

function goBack() {
  router.push('/menu')
}

async function loadHolidays() {
  try {
    const response = await getHolidays()
    holidays.value = response.data
  } catch (error) {
    console.error('休日の読み込みに失敗しました:', error)
  }
}

function formatHolidayDate(dateString: string): string {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`
}

async function saveHoliday() {
  if (!holidayForm.value.date || !holidayForm.value.name) return

  try {
    const response = await createHoliday({
      date: holidayForm.value.date,
      name: holidayForm.value.name
    })
    holidays.value.push(response.data)
    closeHolidayModal()
    await loadHolidays()
  } catch (error) {
    console.error('休日の追加に失敗しました:', error)
  }
}

async function deleteHoliday(holidayId: number) {
  if (!confirm('この休日を削除しますか？')) return

  try {
    await apiDeleteHoliday(holidayId)
    holidays.value = holidays.value.filter(h => h.id !== holidayId)
    await loadHolidays()
  } catch (error) {
    console.error('休日の削除に失敗しました:', error)
  }
}

function closeHolidayModal() {
  showHolidayModal.value = false
  holidayForm.value = {
    date: '',
    name: ''
  }
}

// 初期化
onMounted(() => {
  loadHolidays()
})
</script>

<style scoped>
.holiday-management {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.back-btn {
  padding: 8px 16px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.back-btn:hover {
  background: #555;
}

.main-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.holiday-controls {
  padding: 20px 20px 0 20px;
  flex-shrink: 0;
}

.add-holiday-btn {
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.add-holiday-btn:hover {
  background: #388e3c;
}

.holiday-list-container {
  flex: 1;
  overflow: hidden;
  padding: 20px;
  padding-top: 10px;
}

.holiday-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
  padding-right: 10px;
}

.holiday-list::-webkit-scrollbar {
  width: 8px;
}

.holiday-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.holiday-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.holiday-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.holiday-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #eee;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.holiday-item:hover {
  background: #f0f0f0;
}

.holiday-date {
  font-weight: bold;
  color: #333;
  flex-shrink: 0;
  min-width: 120px;
}

.holiday-name {
  font-weight: bold;
  color: #ff4444;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-btn {
  padding: 6px;
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background: #cc0000;
}

/* モーダルスタイル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  min-width: 400px;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
}

.form-group label {
  min-width: 120px;
  padding-top: 8px;
  flex-shrink: 0;
  font-weight: bold;
  color: #333;
}

.form-group input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.form-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.form-actions button[type="submit"] {
  background: #4CAF50;
  color: white;
}

.form-actions button[type="submit"]:hover {
  background: #388e3c;
}

.form-actions button[type="button"] {
  background: #666;
  color: white;
}

.form-actions button[type="button"]:hover {
  background: #555;
}
</style> 