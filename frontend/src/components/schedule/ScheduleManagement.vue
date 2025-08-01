<template>
  <div class="schedule-management">
    <div class="header">
      <div class="header-left">
        <img src="/images/SCHEDULE.png" alt="SCHEDULE" class="header-icon" />
        <h1>スケジュール</h1>
      </div>
      <div class="header-right">
        <img 
          src="/images/CONFIG.png" 
          alt="CONFIG" 
          class="config-icon" 
          @click="showConfigModal = true"
          title="設定"
        />
        <img 
          src="/images/PORTAL.png" 
          alt="PORTAL" 
          class="portal-icon" 
          @click="goBack"
          title="トップメニューに戻る"
        />
      </div>
    </div>

         <div class="main-content">
       <!-- カレンダー -->
      <div class="calendar-section">
        <div class="view-toggle">
          <button 
            :class="{ active: viewMode === 'month' }" 
            @click="setViewMode('month')"
          >
            月表示
          </button>
          <button 
            :class="{ active: viewMode === 'week' }" 
            @click="setViewMode('week')"
          >
            週間表示
          </button>
        </div>





        <!-- 月表示 -->
        <div v-if="viewMode === 'month'" class="monthly-view">
          <ScheduleMonthly
            :current-year="currentYear"
            :current-month="currentMonth"
            :start-with-monday="startWithMonday"
            :schedules="schedules"
            :selected-categories="selectedCategories"
            :activity-categories="activityCategories"
            :holidays="holidays"
            @select-date="selectDate"
            @edit-schedule="editSchedule"
            @previous-month="previousMonth"
            @next-month="nextMonth"
            @toggle-monday-start="toggleMondayStart"
          />
        </div>

        <!-- 週間表示 -->
        <div v-else-if="viewMode === 'week'" class="weekly-view">
          <ScheduleWeekly
            :schedules="schedules"
            :activity-categories="activityCategories"
            :selected-categories="selectedCategories"
            @edit-schedule="editSchedule"
          />
        </div>
      </div>
    </div>

    <!-- スケジュール編集モーダル -->
    <div v-if="showScheduleModal" class="modal-overlay" @wheel.prevent>
      <div class="modal-content" @click.stop @wheel.stop>
        <h3>{{ editingSchedule ? 'スケジュール編集' : '新規スケジュール' }}</h3>
        <form @submit.prevent="saveSchedule">
          <div class="form-group">
            <label>タイトル:</label>
            <input v-model="scheduleForm.title" required />
          </div>

          <div class="form-group">
            <label>終日:</label>
            <input type="checkbox" v-model="scheduleForm.is_all_day" />
          </div>

          <div class="form-group">
            <label>開始日時:</label>
            <input
              v-if="!scheduleForm.is_all_day"
              type="datetime-local"
              v-model="scheduleForm.start_datetime_local"
              required
            />
            <input
              v-else
              type="date"
              v-model="scheduleForm.start_date"
              required
            />
          </div>

          <div class="form-group">
            <label>所要時間:</label>
            <input
              v-if="!scheduleForm.is_all_day"
              type="number"
              v-model="scheduleForm.duration_minutes"
              placeholder="分"
              required
            />
            <input
              v-else
              type="number"
              v-model="scheduleForm.duration_days"
              placeholder="日"
              required
            />
          </div>

          <div class="form-group">
            <label>活動区分:</label>
            <select v-model="scheduleForm.activity_category_id" required>
              <option value="">選択してください</option>
              <option v-for="category in activityCategories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>スケジュールタイプ:</label>
            <select v-model="scheduleForm.schedule_type" required>
              <option value="予定">予定</option>
              <option value="TODO">TODO</option>
            </select>
          </div>

          <div class="form-group">
            <label>場所:</label>
            <input v-model="scheduleForm.location" />
          </div>

          <div class="form-group">
            <label>詳細:</label>
            <textarea v-model="scheduleForm.details" rows="4"></textarea>
          </div>

          <div class="form-group" v-if="scheduleForm.schedule_type === 'TODO'">
            <label>実施済み:</label>
            <input type="checkbox" v-model="scheduleForm.is_todo_completed" />
          </div>

          <div class="form-actions">
            <button type="button" @click="closeScheduleModal">キャンセル</button>
            <button type="submit">保存</button>
            <button v-if="editingSchedule" type="button" @click="deleteSchedule" class="delete-btn">削除</button>
          </div>
                 </form>
       </div>
     </div>

     <!-- 設定モーダル -->
     <div v-if="showConfigModal" class="modal-overlay" @wheel.prevent>
       <div class="modal-content config-modal" @click.stop @wheel.stop>
         <div class="config-modal-header">
           <h3>設定</h3>
           <button class="close-btn" @click="showConfigModal = false">×</button>
         </div>
         <div class="config-modal-body">
           <ScheduleCategoryList
             :activity-categories="activityCategories"
             :selected-categories="selectedCategories"
             @update-activity-categories="updateActivityCategories"
             @update-selected-categories="updateSelectedCategories"
             @refresh-schedules="loadSchedules"
           />
         </div>
       </div>
     </div>
   </div>
 </template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { buildApiUrl } from '../../utils/api'
import ScheduleWeekly from './ScheduleWeekly.vue'
import ScheduleMonthly from './ScheduleMonthly.vue'
import ScheduleCategoryList from './ScheduleCategoryList.vue'
import { getCategoryColor } from './ScheduleCommon'

const router = useRouter()

// 状態管理
const activityCategories = ref<any[]>([])
const selectedCategories = ref<number[]>([])
const schedules = ref<any[]>([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const startWithMonday = ref(true)
const showScheduleModal = ref(false)
const showConfigModal = ref(false)
const editingSchedule = ref<any>(null)
const viewMode = ref<'month' | 'week'>('month')

// 休日管理（カレンダー表示用）
const holidays = ref<any[]>([])

// スケジュールフォーム
const scheduleForm = ref({
  title: '',
  is_all_day: false,
  start_datetime_local: '',
  start_date: '',
  duration_minutes: 60,
  duration_days: 1,
  activity_category_id: '',
  schedule_type: '予定',
  location: '',
  details: '',
  is_todo_completed: false
})



// メソッド
function goBack() {
  router.push('/')
}

function setViewMode(mode: 'month' | 'week') {
  viewMode.value = mode
}

async function loadActivityCategories() {
  try {
    const response = await fetch(buildApiUrl('/activity-categories'))
    const data = await response.json()
    activityCategories.value = data
    // 初期状態では全て選択
    selectedCategories.value = activityCategories.value.map(cat => cat.id)
  } catch (error) {
    console.error('活動区分の読み込みに失敗しました:', error)
  }
}

async function loadSchedules() {
  try {
    let response
    if (viewMode.value === 'week') {
      // 週間表示の場合は、現在の週の開始日を計算
      const today = new Date()
      const dayOfWeek = today.getDay()
      const mondayOffset = startWithMonday.value ? 1 : 0
      const daysFromMonday = (dayOfWeek + 7 - mondayOffset) % 7
      const weekStart = new Date(today)
      weekStart.setDate(today.getDate() - daysFromMonday)
      
      const startDate = weekStart.toISOString().split('T')[0] // YYYY-MM-DD形式
      response = await fetch(buildApiUrl(`/schedules/week/${startDate}`))
    } else {
      // 月表示の場合は従来通り
      response = await fetch(buildApiUrl(`/schedules/month/${currentYear.value}/${currentMonth.value}`))
    }
    const data = await response.json()
    schedules.value = data
  } catch (error) {
    console.error('スケジュールの読み込みに失敗しました:', error)
  }
}

async function loadHolidays() {
  try {
    const response = await fetch(buildApiUrl('/holidays'))
    const data = await response.json()
    holidays.value = data
  } catch (error) {
    console.error('休日の読み込みに失敗しました:', error)
  }
}



function previousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

function toggleMondayStart(value: boolean) {
  startWithMonday.value = value
}

function updateActivityCategories(categories: any[]) {
  activityCategories.value = categories
}

function updateSelectedCategories(categories: number[]) {
  selectedCategories.value = categories
}





function selectDate(date: Date) {
  editingSchedule.value = null

  // 日付をローカルタイムゾーンでフォーマット
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  scheduleForm.value = {
    title: '',
    is_all_day: false,
    start_datetime_local: `${year}-${month}-${day}T${hours}:${minutes}`,
    start_date: `${year}-${month}-${day}`,
    duration_minutes: 60,
    duration_days: 1,
    activity_category_id: '',
    schedule_type: '予定',
    location: '',
    details: '',
    is_todo_completed: false
  }
  showScheduleModal.value = true
}

function editSchedule(schedule: any) {
  editingSchedule.value = schedule

  // 日時をローカルタイムゾーンでフォーマット
  const scheduleDate = new Date(schedule.start_datetime)
  const year = scheduleDate.getFullYear()
  const month = String(scheduleDate.getMonth() + 1).padStart(2, '0')
  const day = String(scheduleDate.getDate()).padStart(2, '0')
  const hours = String(scheduleDate.getHours()).padStart(2, '0')
  const minutes = String(scheduleDate.getMinutes()).padStart(2, '0')

  scheduleForm.value = {
    title: schedule.title,
    is_all_day: schedule.is_all_day,
    start_datetime_local: schedule.is_all_day ? '' : `${year}-${month}-${day}T${hours}:${minutes}`,
    start_date: schedule.is_all_day ? `${year}-${month}-${day}` : '',
    duration_minutes: schedule.is_all_day ? 0 : schedule.duration,
    duration_days: schedule.is_all_day ? schedule.duration : 0,
    activity_category_id: schedule.activity_category_id,
    schedule_type: schedule.schedule_type,
    location: schedule.location || '',
    details: schedule.details || '',
    is_todo_completed: schedule.is_todo_completed
  }
  showScheduleModal.value = true
}

function closeScheduleModal() {
  showScheduleModal.value = false
  editingSchedule.value = null
}

async function saveSchedule() {
  try {
    const scheduleData = {
      title: scheduleForm.value.title,
      is_all_day: scheduleForm.value.is_all_day,
      start_datetime: scheduleForm.value.is_all_day
        ? new Date(scheduleForm.value.start_date + 'T00:00:00').toISOString()
        : new Date(scheduleForm.value.start_datetime_local).toISOString(),
      duration: scheduleForm.value.is_all_day
        ? scheduleForm.value.duration_days
        : scheduleForm.value.duration_minutes,
      activity_category_id: parseInt(scheduleForm.value.activity_category_id),
      schedule_type: scheduleForm.value.schedule_type,
      location: scheduleForm.value.location,
      details: scheduleForm.value.details,
      is_todo_completed: scheduleForm.value.is_todo_completed
    }

    if (editingSchedule.value) {
      await fetch(buildApiUrl(`/schedules/${editingSchedule.value.id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scheduleData)
      })
    } else {
      await fetch(buildApiUrl('/schedules'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scheduleData)
      })
    }

    closeScheduleModal()
    await loadSchedules()
  } catch (error) {
    console.error('スケジュールの保存に失敗しました:', error)
  }
}

async function deleteSchedule() {
  if (!editingSchedule.value || !confirm('このスケジュールを削除しますか？')) return

  try {
    await fetch(buildApiUrl(`/schedules/${editingSchedule.value.id}`), {
      method: 'DELETE'
    })
    closeScheduleModal()
    await loadSchedules()
  } catch (error) {
    console.error('スケジュールの削除に失敗しました:', error)
  }
}





// 監視
watch([currentYear, currentMonth], () => {
  loadSchedules()
})

watch([viewMode, startWithMonday], () => {
  loadSchedules()
})

// 初期化
onMounted(() => {
  loadActivityCategories()
  loadSchedules()
  loadHolidays()
})
</script>

<style scoped>
.schedule-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
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

.main-content {
  display: flex;
  gap: 20px;
}





.calendar-section {
  flex: 1;
}





.view-toggle {
  display: flex;
  gap: 4px;
}

.view-toggle button {
  padding: 8px 16px;
  background: #f0f0f0;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.view-toggle button:hover {
  background: #e0e0e0;
}

.view-toggle button.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.weekly-view {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.monthly-view {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.form-group label {
  min-width: 120px;
  font-weight: bold;
  margin: 0;
  padding-top: 8px;
  flex-shrink: 0;
}

.form-group input,
.form-group select,
.form-group textarea {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* チェックボックス用の特別なスタイル */
.form-group input[type="checkbox"] {
  flex: none;
  width: auto;
  margin-left: 0;
  margin-right: 8px;
}

/* チェックボックスを含むフォームグループのラベル位置調整 */
.form-group:has(input[type="checkbox"]) label {
  padding-top: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.form-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-actions button[type="submit"] {
  background: #4CAF50;
  color: white;
}

.form-actions button[type="button"] {
  background: #666;
  color: white;
}

.form-actions .delete-btn {
  background: #ff4444;
  color: white;
  height: auto;
  min-height: auto;
  width: auto;
  min-width: auto;
}

/* 設定モーダル */
.config-modal {
  max-width: 600px;
  width: 90%;
}

.config-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ddd;
}

.config-modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.config-modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
</style>