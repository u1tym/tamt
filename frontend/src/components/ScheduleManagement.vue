<template>
  <div class="schedule-management">
    <div class="header">
      <h1>スケジュール管理</h1>
      <button class="back-btn" @click="goBack">← 戻る</button>
    </div>

    <div class="main-content">
      <!-- 左側: 活動区分一覧 -->
      <div class="activity-categories">
        <h2>活動区分</h2>
                 <div class="category-list">
           <div v-for="category in activityCategories" :key="category.id" class="category-item">
             <input
               type="checkbox"
               :id="'category-' + category.id"
               :checked="selectedCategories.includes(category.id)"
               @change="toggleCategory(category.id)"
             />
             <div class="category-content">
               <span v-if="!category.editing" @click="startEditCategory(category)" class="category-name">
                 {{ category.name }}
               </span>
               <div v-else class="edit-category">
                 <input
                   v-model="category.editName"
                   @keyup.enter="saveCategoryName(category)"
                   @keyup.esc="cancelEditCategory(category)"
                   @blur="saveCategoryName(category)"
                   ref="categoryInput"
                   class="edit-input"
                 />
               </div>
             </div>
                           <button class="delete-btn" @click="deleteCategory(category.id)" title="削除">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
           </div>
         </div>
        <div class="add-category">
          <input v-model="newCategoryName" placeholder="新しい活動区分名" />
          <button @click="addCategory">追加</button>
        </div>
      </div>

      <!-- 右側: カレンダー -->
      <div class="calendar-section">
        <div class="calendar-header">
          <button @click="previousMonth">←</button>
          <h2>{{ currentYear }}年{{ currentMonth }}月</h2>
          <button @click="nextMonth">→</button>
        </div>

        <div class="calendar-controls">
          <label>
            <input type="checkbox" v-model="startWithMonday" />
            月曜始まり
          </label>
        </div>

        <div class="calendar">
          <!-- 曜日ヘッダー -->
          <div class="calendar-header-row">
            <div v-for="day in weekDays" :key="day" class="calendar-header-cell">
              {{ day }}
            </div>
          </div>

          <!-- カレンダー本体 -->
          <div class="calendar-body">
            <div v-for="week in calendarWeeks" :key="week[0]" class="calendar-week">
              <div
                v-for="date in week"
                :key="date ? date.toISOString() : 'empty'"
                class="calendar-day"
                :class="{ 'other-month': !date || date.getMonth() !== currentMonth - 1 }"
                @click="date ? selectDate(date) : null"
              >
                <div class="date-number">{{ date ? date.getDate() : '' }}</div>
                <div class="schedule-items">
                  <div
                    v-for="schedule in getSchedulesForDate(date)"
                    :key="schedule.id"
                    class="schedule-item"
                    :class="getScheduleClass(schedule)"
                    @click.stop="editSchedule(schedule)"
                  >
                    <div class="schedule-time" v-if="!schedule.is_all_day">
                      {{ formatTime(schedule.start_datetime) }}
                    </div>
                    <div class="schedule-title">{{ schedule.title }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- スケジュール編集モーダル -->
    <div v-if="showScheduleModal" class="modal-overlay" @click="closeScheduleModal">
      <div class="modal-content" @click.stop>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { buildApiUrl } from '../utils/api'

const router = useRouter()

// 状態管理
const activityCategories = ref<any[]>([])
const selectedCategories = ref<number[]>([])
const schedules = ref<any[]>([])
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth() + 1)
const startWithMonday = ref(true)
const showScheduleModal = ref(false)
const editingSchedule = ref<any>(null)
const newCategoryName = ref('')

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

// 曜日配列
const weekDays = computed(() => {
  if (startWithMonday.value) {
    return ['月', '火', '水', '木', '金', '土', '日']
  } else {
    return ['日', '月', '火', '水', '木', '金', '土']
  }
})

// カレンダーの週配列を生成
const calendarWeeks = computed(() => {
  const firstDay = new Date(currentYear.value, currentMonth.value - 1, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value, 0)

  // 月の最初の日の曜日を取得（0=日曜日, 1=月曜日, ...）
  let firstDayOfWeek = firstDay.getDay()
  if (startWithMonday.value) {
    firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1
  }

  const weeks: Date[][] = []
  let currentWeek: Date[] = []

  // 前月の日を追加
  for (let i = 0; i < firstDayOfWeek; i++) {
    const prevDate = new Date(firstDay)
    prevDate.setDate(prevDate.getDate() - (firstDayOfWeek - i))
    currentWeek.push(prevDate)
  }

  // 当月の日を追加
  for (let day = 1; day <= lastDay.getDate(); day++) {
    if (currentWeek.length === 7) {
      weeks.push(currentWeek)
      currentWeek = []
    }
    currentWeek.push(new Date(currentYear.value, currentMonth.value - 1, day))
  }

  // 翌月の日を追加（最後の週を7日で埋める）
  let nextDay = 1
  while (currentWeek.length < 7) {
    const nextDate = new Date(currentYear.value, currentMonth.value, nextDay)
    currentWeek.push(nextDate)
    nextDay++
  }

  if (currentWeek.length > 0) {
    weeks.push(currentWeek)
  }

  return weeks
})

// メソッド
function goBack() {
  router.push('/')
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
    const response = await fetch(buildApiUrl(`/schedules/month/${currentYear.value}/${currentMonth.value}`))
    const data = await response.json()
    schedules.value = data
  } catch (error) {
    console.error('スケジュールの読み込みに失敗しました:', error)
  }
}

function toggleCategory(categoryId: number) {
  const index = selectedCategories.value.indexOf(categoryId)
  if (index > -1) {
    selectedCategories.value.splice(index, 1)
  } else {
    selectedCategories.value.push(categoryId)
  }
}

async function addCategory() {
  if (!newCategoryName.value.trim()) return

  try {
    const response = await fetch(buildApiUrl('/activity-categories'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: newCategoryName.value.trim()
      })
    })
    const data = await response.json()
    activityCategories.value.push(data)
    selectedCategories.value.push(data.id)
    newCategoryName.value = ''
  } catch (error) {
    console.error('活動区分の追加に失敗しました:', error)
  }
}

async function deleteCategory(categoryId: number) {
  if (!confirm('この活動区分を削除しますか？関連するスケジュールも削除されます。')) return

  try {
    await fetch(buildApiUrl(`/activity-categories/${categoryId}`), {
      method: 'DELETE'
    })
    activityCategories.value = activityCategories.value.filter(cat => cat.id !== categoryId)
    selectedCategories.value = selectedCategories.value.filter(id => id !== categoryId)
    await loadSchedules() // スケジュールを再読み込み
  } catch (error) {
    console.error('活動区分の削除に失敗しました:', error)
  }
}

// 活動区分の編集機能
function startEditCategory(category: any) {
  category.editing = true
  category.editName = category.name
  // 次のティックでフォーカスを設定
  nextTick(() => {
    const input = document.querySelector('.edit-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

async function saveCategoryName(category: any) {
  if (!category.editName.trim() || category.editName === category.name) {
    category.editing = false
    return
  }

  try {
    const response = await fetch(buildApiUrl(`/activity-categories/${category.id}`), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: category.editName.trim()
      })
    })

    if (response.ok) {
      category.name = category.editName.trim()
    }
  } catch (error) {
    console.error('活動区分の更新に失敗しました:', error)
  }

  category.editing = false
}

function cancelEditCategory(category: any) {
  category.editing = false
  category.editName = category.name
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

function getSchedulesForDate(date: Date | null) {
  if (!date) return []

  return schedules.value.filter(schedule => {
    const scheduleDate = new Date(schedule.start_datetime)
    return scheduleDate.getDate() === date.getDate() &&
           scheduleDate.getMonth() === date.getMonth() &&
           scheduleDate.getFullYear() === date.getFullYear() &&
           selectedCategories.value.includes(schedule.activity_category_id)
  })
}

function getScheduleClass(schedule: any) {
  const classes = ['schedule-item']
  if (schedule.is_all_day) {
    classes.push('all-day')
  }
  if (schedule.schedule_type === 'TODO') {
    classes.push('todo')
    if (schedule.is_todo_completed) {
      classes.push('completed')
    }
  }
  return classes.join(' ')
}

function formatTime(datetime: string) {
  const date = new Date(datetime)
  return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
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

// 初期化
onMounted(() => {
  loadActivityCategories()
  loadSchedules()
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

.back-btn {
  padding: 8px 16px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.main-content {
  display: flex;
  gap: 20px;
}

.activity-categories {
  width: 250px;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  height: fit-content;
}

.category-list {
  margin-bottom: 20px;
}

.category-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.category-content {
  flex: 1;
  min-width: 0;
}

.category-name {
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.category-name:hover {
  background-color: #e0e0e0;
}

.edit-category {
  flex: 1;
}

.edit-input {
  width: 100%;
  padding: 2px 4px;
  border: 1px solid #2196f3;
  border-radius: 3px;
  font-size: inherit;
}

.delete-btn {
  background: none;
  color: #666;
  border: none;
  width: 20px;
  height: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  padding: 0;
  min-width: 20px;
  min-height: 20px;
}

.delete-btn:hover {
  color: #ff4444;
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.add-category {
  display: flex;
  gap: 8px;
}

.add-category input {
  flex: 1;
  padding: 4px 8px;
}

.add-category button {
  padding: 4px 8px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.calendar-section {
  flex: 1;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-header button {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.calendar-controls {
  margin-bottom: 20px;
}

.calendar {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-header-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f0f0f0;
}

.calendar-header-cell {
  padding: 12px;
  text-align: center;
  font-weight: bold;
  border-right: 1px solid #ddd;
}

.calendar-header-cell:last-child {
  border-right: none;
}

.calendar-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
  min-height: 120px;
  border-right: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
  padding: 8px;
  cursor: pointer;
}

.calendar-day:hover {
  background: #f9f9f9;
}

.calendar-day.other-month {
  background: #f9f9f9;
  color: #999;
}

.calendar-day:last-child {
  border-right: none;
}

.date-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.schedule-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-item {
  background: #e3f2fd;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 11px;
  cursor: pointer;
  border-left: 3px solid #2196f3;
}

.schedule-item.all-day {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.schedule-item.todo {
  background: #f3e5f5;
  border-left-color: #9c27b0;
}

.schedule-item.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.schedule-time {
  font-size: 10px;
  color: #666;
}

.schedule-title {
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
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
</style>