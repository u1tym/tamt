<template>
  <div class="schedule-weekly">
    <!-- 表示設定 -->
    <div class="view-controls">
      <div class="view-toggle">
        <button 
          :class="{ active: viewMode === '3days' }" 
          @click="setViewMode('3days')"
        >
          3日表示
        </button>
                 <button 
           :class="{ active: viewMode === 'week' }" 
           @click="setViewMode('week')"
         >
           1週間表示
         </button>
      </div>
      
      <div class="week-start-toggle" v-if="viewMode === 'week'">
        <button 
          :class="{ active: startWithMonday }" 
          @click="toggleWeekStart(true)"
        >
          月曜始まり
        </button>
        <button 
          :class="{ active: !startWithMonday }" 
          @click="toggleWeekStart(false)"
        >
          日曜始まり
        </button>
      </div>
    </div>

    <!-- 日付ナビゲーション -->
    <div class="date-navigation">
      <button @click="previousPeriod" class="nav-btn">
        <span v-if="viewMode === 'week'">前週</span>
        <span v-else>前日</span>
      </button>
      
      <div class="current-period">
        <span v-if="viewMode === 'week'">
          {{ formatDateRange(displayDates[0], displayDates[6]) }}
        </span>
        <span v-else>
          {{ formatDateRange(displayDates[0], displayDates[2]) }}
        </span>
      </div>
      
      <button @click="nextPeriod" class="nav-btn">
        <span v-if="viewMode === 'week'">翌週</span>
        <span v-else>翌日</span>
      </button>
    </div>

    <!-- 週間カレンダー -->
    <div class="weekly-calendar">
      <!-- ヘッダー（日付） -->
      <div class="calendar-header">
        <div class="time-column-header"></div>
        <div 
          v-for="date in displayDates" 
          :key="date.toISOString()" 
          class="date-header"
          :class="{ 
            'today': isToday(date),
            'past': isPast(date),
            'future': isFuture(date),
            'saturday': isSaturday(date),
            'sunday': isSunday(date),
            'holiday': isHoliday(date)
          }"
        >
          <div class="date-day">{{ getDayOfWeek(date) }}</div>
          <div 
            class="date-number" 
            :class="{ 'today': isToday(date) }" 
            :style="isToday(date) ? { background: '#007bff', color: 'white', borderRadius: '4px', padding: '2px 6px', display: 'inline-block', minWidth: '20px', textAlign: 'center' } : {}"
          >
            {{ date.getDate() }}
          </div>
          <div v-if="getHolidayName(date)" class="holiday-name">{{ getHolidayName(date) }}</div>
        </div>
      </div>

      <!-- カレンダー本体 -->
      <div class="calendar-body">
        <!-- 終日予定エリア -->
        <div class="all-day-section">
          <div class="all-day-label">終日</div>
                     <div 
             v-for="date in displayDates" 
             :key="`all-day-${date.toISOString()}`" 
             class="all-day-cell"
             @click="createAllDaySchedule(date)"
           >
            <div 
              v-for="schedule in getAllDaySchedules(date)" 
              :key="schedule.id"
              class="schedule-item all-day-schedule"
              :style="{ 
                backgroundColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                borderColor: getCategoryColor(schedule.activity_category_id, activityCategories)
              }"
              @click.stop="editSchedule(schedule)"
              :title="`${schedule.title}${schedule.location ? ' - ' + schedule.location : ''}`"
            >
              {{ schedule.title }}
            </div>
          </div>
        </div>

        <!-- 時刻別予定エリア -->
        <div class="time-section">
          <div class="time-column">
            <div 
              v-for="time in timeSlots" 
              :key="time" 
              class="time-slot"
            >
              {{ formatTime(time) }}
            </div>
          </div>
          
          <div 
            v-for="date in displayDates" 
            :key="`time-${date.toISOString()}`" 
            class="schedule-column"
          >
                         <div 
               v-for="time in timeSlots" 
               :key="`${date.toISOString()}-${time}`" 
               class="time-cell"
               :class="{ 'dragging': isCellDragged(date, time) }"
               :data-date="date.toISOString()"
               :data-time="time"
               @mousedown="startDrag($event, date, time)"
               @mouseover="handleMouseOver($event, date, time)"
               @mouseout="handleMouseOut($event)"
             >
               <div 
                 v-for="schedule in getSchedulesAtTime(date, time)" 
                 :key="schedule.id"
                 class="schedule-item time-schedule"
                 :style="{ 
                   backgroundColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                   borderColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                   top: `${getScheduleTopOffset(schedule, time)}px`,
                   height: `${schedule.duration}px`
                 }"
                 @click.stop="editSchedule(schedule)"
                 :title="`${schedule.title}${schedule.location ? ' - ' + schedule.location : ''}`"
               >
                 <div class="schedule-time">{{ formatScheduleTime(schedule) }}</div>
                 <div class="schedule-title">{{ schedule.title }}</div>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { getCategoryColor } from './ScheduleCommon'

// Props
interface Props {
  schedules?: any[]
  activityCategories?: any[]
  selectedCategories?: number[]
  holidays?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  schedules: () => [],
  activityCategories: () => [],
  selectedCategories: () => [],
  holidays: () => []
})

// Emits
const emit = defineEmits<{
  editSchedule: [schedule: any]
  createSchedule: [date: Date, startTime: string, durationMinutes: number]
  createAllDaySchedule: [date: Date]
  weekStartChanged: [startDate: string]
}>()

// 状態管理
const viewMode = ref<'3days' | 'week'>('week')
const startWithMonday = ref(true)
const currentDate = ref(new Date())

// 時刻スロット（30分間隔）
const timeSlots = computed(() => {
  const slots = []
  for (let hour = 0; hour < 24; hour++) {
    slots.push(hour * 60) // 00:00
    slots.push(hour * 60 + 30) // 00:30
  }
  return slots
})

// 表示する日付を計算
const displayDates = computed(() => {
  const dates = []
  
  if (viewMode.value === 'week') {
    // 週間表示の場合：常に今日を含む週を表示
    const today = new Date()
    const dayOfWeek = today.getDay()
    const mondayOffset = startWithMonday.value ? 1 : 0
    const daysFromMonday = (dayOfWeek + 7 - mondayOffset) % 7
    
    // 週の開始日を計算（月曜始まりまたは日曜始まり）
    const weekStartDate = new Date(today)
    weekStartDate.setDate(today.getDate() - daysFromMonday)
    
    // ナビゲーションによる週のオフセットを適用
    const weekOffset = Math.floor((currentDate.value.getTime() - today.getTime()) / (7 * 24 * 60 * 60 * 1000))
    weekStartDate.setDate(weekStartDate.getDate() + (weekOffset * 7))
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStartDate)
      date.setDate(weekStartDate.getDate() + i)
      dates.push(date)
    }
  } else {
    // 3日表示の場合（今日、明日、明後日）
    const startDate = new Date(currentDate.value)
    for (let i = 0; i < 3; i++) {
      const date = new Date(startDate)
      date.setDate(startDate.getDate() + i)
      dates.push(date)
    }
  }
  
  return dates
})

watch(
  () => displayDates.value[0],
  (newStart) => {
    if (newStart) {
      emit('weekStartChanged', newStart.toISOString().split('T')[0])
    }
  },
  { immediate: true }
)

// フィルタリングされたスケジュール
const filteredSchedules = computed(() => {
  if (props.selectedCategories.length === 0) return props.schedules
  
  return props.schedules.filter(schedule => 
    props.selectedCategories.includes(schedule.activity_category_id)
  )
})

// Removed unused loadSchedulesFor3Days function

// メソッド
function setViewMode(mode: '3days' | 'week') {
  viewMode.value = mode
  // 週間表示に切り替えた場合は今日の日付にリセット
  if (mode === 'week') {
    currentDate.value = new Date()
  }
}

function toggleWeekStart(monday: boolean) {
  startWithMonday.value = monday
}

function previousPeriod() {
  const newDate = new Date(currentDate.value)
  if (viewMode.value === 'week') {
    // 週間表示の場合：前週に移動
    newDate.setDate(newDate.getDate() - 7)
  } else {
    // 3日表示の場合：前日から開始するように移動
    newDate.setDate(newDate.getDate() - 1)
  }
  currentDate.value = newDate
}

function nextPeriod() {
  const newDate = new Date(currentDate.value)
  if (viewMode.value === 'week') {
    // 週間表示の場合：翌週に移動
    newDate.setDate(newDate.getDate() + 7)
  } else {
    // 3日表示の場合：翌日から開始するように移動
    newDate.setDate(newDate.getDate() + 1)
  }
  currentDate.value = newDate
}

function formatDateRange(startDate: Date, endDate: Date): string {
  const start = startDate.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })
  const end = endDate.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' })
  return `${start} - ${end}`
}

function getDayOfWeek(date: Date): string {
  const dayOfWeek = date.getDay() // 0=日曜日, 1=月曜日, ..., 6=土曜日
  
  if (startWithMonday.value) {
    // 月曜始まりの場合：月曜日=0, 火曜日=1, ..., 日曜日=6
    const mondayFirstDays = ['月', '火', '水', '木', '金', '土', '日']
    const adjustedIndex = (dayOfWeek + 6) % 7 // 日曜日(0)を6に、月曜日(1)を0に変換
    return mondayFirstDays[adjustedIndex]
  } else {
    // 日曜始まりの場合：日曜日=0, 月曜日=1, ..., 土曜日=6
    const sundayFirstDays = ['日', '月', '火', '水', '木', '金', '土']
    return sundayFirstDays[dayOfWeek]
  }
}

function isToday(date: Date): boolean {
  const today = new Date()
  const result = date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
  
  // デバッグ用：今日の日付をコンソールに出力
  if (result) {
    console.log('Today found:', date.toDateString(), 'Current date:', today.toDateString())
  }
  
  return result
}

function isPast(date: Date): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date < today
}

function isFuture(date: Date): boolean {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date > today
}

function isSaturday(date: Date): boolean {
  return date.getDay() === 6 // 6=土曜日
}

function isSunday(date: Date): boolean {
  return date.getDay() === 0 // 0=日曜日
}

function isHoliday(date: Date): boolean {
  const dateStr = date.toISOString().split('T')[0]
  return props.holidays.some(holiday => holiday.date === dateStr)
}

function getHolidayName(date: Date): string | null {
  const dateStr = date.toISOString().split('T')[0]
  const holiday = props.holidays.find(holiday => holiday.date === dateStr)
  return holiday ? holiday.name : null
}

function formatTime(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
}

function getAllDaySchedules(date: Date): any[] {
  return filteredSchedules.value.filter(schedule => {
    if (!schedule.is_all_day) return false
    
    const scheduleDate = new Date(schedule.start_datetime)
    const startDate = new Date(date)
    startDate.setHours(0, 0, 0, 0)
    
    const endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 1)
    
    return scheduleDate >= startDate && scheduleDate < endDate
  })
}

function getSchedulesAtTime(date: Date, timeMinutes: number): any[] {
  return filteredSchedules.value.filter(schedule => {
    if (schedule.is_all_day) return false
    
    const scheduleDate = new Date(schedule.start_datetime)
    const scheduleStartMinutes = scheduleDate.getHours() * 60 + scheduleDate.getMinutes()
    
    const targetDate = new Date(date)
    targetDate.setHours(0, 0, 0, 0)
    
    const scheduleTargetDate = new Date(scheduleDate)
    scheduleTargetDate.setHours(0, 0, 0, 0)
    
    // 予定がその日付のものかチェック
    if (scheduleTargetDate.getTime() !== targetDate.getTime()) {
      return false
    }
    
    // 予定の開始時刻がこの時刻スロットに含まれるかチェック
    // 時刻スロットは timeMinutes から timeMinutes + 30 まで
    return scheduleStartMinutes >= timeMinutes && scheduleStartMinutes < timeMinutes + 30
  })
}

function getScheduleTopOffset(schedule: any, timeMinutes: number): number {
  const scheduleDate = new Date(schedule.start_datetime)
  const scheduleStartMinutes = scheduleDate.getHours() * 60 + scheduleDate.getMinutes()
  return (scheduleStartMinutes - timeMinutes) * 2 // 30分 = 30px
}

// Removed unused getScheduleHeight function

function formatScheduleTime(schedule: any): string {
  const startDate = new Date(schedule.start_datetime)
  const endDate = new Date(startDate.getTime() + schedule.duration * 60 * 1000)
  
  const startTime = startDate.toLocaleTimeString('ja-JP', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  })
  const endTime = endDate.toLocaleTimeString('ja-JP', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false 
  })
  
  return `${startTime}-${endTime}`
}

function editSchedule(schedule: any) {
  emit('editSchedule', schedule)
}

function createAllDaySchedule(date: Date) {
  emit('createAllDaySchedule', date)
}

// ドラッグ機能の状態管理
const isDragging = ref(false)
const dragStartTime = ref<number | null>(null)
const dragStartDate = ref<Date | null>(null)
const dragEndTime = ref<number | null>(null)
const dragEndDate = ref<Date | null>(null)
const draggedCells = ref<Set<string>>(new Set())

// ドラッグ開始
function startDrag(event: MouseEvent, date: Date, time: number) {
  // 予定がクリックされた場合はドラッグしない
  if ((event.target as HTMLElement).closest('.schedule-item')) {
    return
  }
  
  isDragging.value = true
  dragStartTime.value = time
  dragStartDate.value = date
  dragEndTime.value = time
  dragEndDate.value = date
  draggedCells.value.clear()
  
  // 開始セルをドラッグ状態に追加
  const cellKey = `${date.toISOString()}-${time}`
  draggedCells.value.add(cellKey)
  
  // ドラッグ中のイベントリスナーを追加
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
  
  // デフォルトのドラッグ動作を防ぐ
  event.preventDefault()
}

// マウスオーバー時の処理
function handleMouseOver(event: MouseEvent, date: Date, time: number) {
  if (isDragging.value) {
    // ドラッグ中の場合は視覚的フィードバックを追加
    const cellKey = `${date.toISOString()}-${time}`
    draggedCells.value.add(cellKey)
    return
  }
  
  // 予定がホバーされた場合は何もしない
  if ((event.target as HTMLElement).closest('.schedule-item')) {
    return
  }
  
  // ホバー効果を追加（必要に応じて）
  const target = event.currentTarget as HTMLElement
  target.style.backgroundColor = '#f0f8ff'
}

// マウスアウト時の処理
function handleMouseOut(event: MouseEvent) {
  if (isDragging.value) {
    return
  }
  
  const target = event.currentTarget as HTMLElement
  target.style.backgroundColor = ''
}

// マウス移動時の処理
function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return
  
  // マウス位置から日付と時刻を計算
  const target = event.target as HTMLElement
  if (target.classList.contains('time-cell')) {
    const dateAttr = target.getAttribute('data-date')
    const timeAttr = target.getAttribute('data-time')
    
    if (dateAttr && timeAttr) {
      const date = new Date(dateAttr)
      const time = parseInt(timeAttr)
      
      dragEndTime.value = time
      dragEndDate.value = date
      
      // ドラッグ範囲内のセルを視覚的にマーク
      updateDraggedCells()
    }
  }
}

// ドラッグ範囲内のセルを更新
function updateDraggedCells() {
  if (!dragStartDate.value || !dragEndDate.value || !dragStartTime.value || !dragEndTime.value) return
  
  draggedCells.value.clear()
  
  const startDate = new Date(dragStartDate.value)
  const endDate = new Date(dragEndDate.value)
  
  // 日付範囲をループ
  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    const currentDate = new Date(d)
    
    // 時刻範囲をループ（開始時刻から終了時刻まで30分間隔で）
    const startTime = d.getTime() === startDate.getTime() ? dragStartTime.value : 0
    const endTime = d.getTime() === endDate.getTime() ? dragEndTime.value : 23 * 60 + 30
    
    for (let time = startTime; time <= endTime; time += 30) {
      const cellKey = `${currentDate.toISOString()}-${time}`
      draggedCells.value.add(cellKey)
    }
  }
}

// セルがドラッグ中かどうかを判定
function isCellDragged(date: Date, time: number): boolean {
  const cellKey = `${date.toISOString()}-${time}`
  return draggedCells.value.has(cellKey)
}

// マウスアップ時の処理
function handleMouseUp() {
  if (!isDragging.value || !dragStartTime.value || !dragStartDate.value) {
    return
  }
  
  // ドラッグが完了したら新規スケジュール作成ダイアログを表示
  const startTime = formatTime(dragStartTime.value)
  
  // ドラッグ範囲の時間を計算
  let durationMinutes = 30 // デフォルト30分
  
  if (dragEndTime.value && dragEndDate.value) {
    const startDateTime = new Date(dragStartDate.value)
    startDateTime.setHours(Math.floor(dragStartTime.value / 60), dragStartTime.value % 60, 0, 0)
    
    const endDateTime = new Date(dragEndDate.value)
    endDateTime.setHours(Math.floor(dragEndTime.value / 60), dragEndTime.value % 60, 0, 0)
    
    // 30分間隔に調整（終了時刻を次の30分間隔に）
    endDateTime.setMinutes(endDateTime.getMinutes() + 30)
    
    const diffMs = endDateTime.getTime() - startDateTime.getTime()
    durationMinutes = Math.max(30, Math.floor(diffMs / (1000 * 60)))
  }
  
  emit('createSchedule', dragStartDate.value, startTime, durationMinutes)
  
  // 状態をリセット
  isDragging.value = false
  dragStartTime.value = null
  dragStartDate.value = null
  dragEndTime.value = null
  dragEndDate.value = null
  draggedCells.value.clear()
  
  // イベントリスナーを削除
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}
</script>

<style scoped>
.schedule-weekly {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
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

.week-start-toggle {
  display: flex;
  gap: 4px;
}

.week-start-toggle button {
  padding: 6px 12px;
  background: #f0f0f0;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9em;
}

.week-start-toggle button:hover {
  background: #e0e0e0;
}

.week-start-toggle button.active {
  background: #2196F3;
  color: white;
  border-color: #2196F3;
}

.date-navigation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
}

.nav-btn {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.nav-btn:hover {
  background: #45a049;
}

.current-period {
  font-weight: bold;
  font-size: 1.1em;
  color: #333;
}

.weekly-calendar {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.calendar-header {
  display: flex;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.time-column-header {
  width: 80px;
  min-width: 80px;
  border-right: 1px solid #ddd;
  background: #f9f9f9;
}

.date-header {
  flex: 1;
  padding: 10px;
  text-align: center;
  border-right: 1px solid #ddd;
  min-width: 120px;
}

.date-header:last-child {
  border-right: none;
}

.date-header.today {
  background: #e3f2fd;
  font-weight: bold;
}

.date-header.past {
  background: #f5f5f5;
  color: #999;
}

.date-header.future {
  background: #f8f8f8;
}

.date-header.saturday {
  background: #e3f2fd;
  color: #1976d2;
}

.date-header.sunday {
  background: #ffebee;
  color: #d32f2f;
}

.date-header.holiday {
  background: #ffebee;
  color: #d32f2f;
}

.date-day {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 4px;
}

.date-number {
  font-size: 1.2em;
  font-weight: bold;
}

/* より具体的なセレクターで今日の日付のスタイルを適用 */
.date-header .date-number.today,
.schedule-weekly .date-number.today {
  background: #007bff !important;
  color: white !important;
  border-radius: 4px !important;
  padding: 2px 6px !important;
  display: inline-block !important;
  min-width: 20px !important;
  text-align: center !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

.date-number.today {
  background: #007bff !important;
  color: white !important;
  border-radius: 4px !important;
  padding: 2px 6px !important;
  display: inline-block !important;
  min-width: 20px !important;
  text-align: center !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
}

.holiday-name {
  font-size: 0.7em;
  color: #d32f2f;
  margin-top: 2px;
  font-weight: bold;
  line-height: 1.2;
}

.calendar-body {
  display: flex;
  flex-direction: column;
  height: 600px;
  overflow: hidden;
}

.all-day-section {
  display: flex;
  border-bottom: 1px solid #ddd;
  min-height: 60px;
}

.all-day-label {
  width: 80px;
  min-width: 80px;
  border-right: 1px solid #ddd;
  background: #f9f9f9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #666;
}

.all-day-cell {
  flex: 1;
  border-right: 1px solid #ddd;
  padding: 5px;
  min-height: 50px;
  background: #fafafa;
  position: relative;
  display: flex;
  flex-direction: column;
}

.all-day-cell:last-child {
  border-right: none;
}

.all-day-schedule {
  display: block;
  width: 100%;
  margin-bottom: 2px;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.8em;
  cursor: pointer;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-sizing: border-box;
  position: static !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  height: auto !important;
  z-index: 1;
}

.time-section {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.time-column {
  width: 80px;
  min-width: 80px;
  border-right: 1px solid #ddd;
  background: #f9f9f9;
  position: relative;
}

.time-slot {
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  color: #666;
  border-bottom: 1px solid #eee;
}

/* XX:00の時刻スロットは濃い実線 */
.time-slot:nth-child(even) {
  border-bottom: 2px solid #ccc;
}

/* XX:30の時刻スロットは薄い点線 */
.time-slot:nth-child(odd) {
  border-bottom: 1px dotted #ddd;
}

.schedule-column {
  flex: 1;
  border-right: 1px solid #ddd;
  position: relative;
  min-width: 120px;
}

.schedule-column:last-child {
  border-right: none;
}

.time-cell {
  height: 30px;
  border-bottom: 1px solid #eee;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
}

.time-cell:hover {
  background-color: #f0f8ff;
}

          .time-cell.dragging {
            background-color: #e3f2fd !important;
          }

/* XX:00の時刻セルは濃い実線 */
.time-cell:nth-child(even) {
  border-bottom: 2px solid #ccc;
}

/* XX:30の時刻セルは薄い点線 */
.time-cell:nth-child(odd) {
  border-bottom: 1px dotted #ddd;
}

.schedule-item {
  position: absolute;
  left: 2px;
  right: 2px;
  border-radius: 3px;
  cursor: pointer;
  color: white;
  font-size: 0.8em;
  overflow: hidden;
  z-index: 10;
  transition: transform 0.2s, box-shadow 0.2s;
}

.schedule-item:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.time-schedule {
  padding: 2px 4px;
}

.schedule-time {
  font-size: 0.7em;
  opacity: 0.9;
  margin-bottom: 1px;
}

.schedule-title {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* スクロール可能なエリア */
.time-section {
  overflow-y: auto;
  max-height: 540px; /* 600px - 60px (all-day section) */
  overflow-x: hidden; /* 横スクロールを隠す */
}

.time-column {
  position: sticky;
  left: 0;
  z-index: 20;
  background: #f9f9f9;
}

/* スクロールバーの幅を考慮して終日欄と時刻欄の幅を揃える */
.all-day-section {
  display: flex;
  border-bottom: 1px solid #ddd;
  min-height: 60px;
  padding-right: 17px; /* スクロールバーの幅分を追加 */
  box-sizing: border-box;
}

/* 日付ヘッダーも同様に調整 */
.calendar-header {
  display: flex;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  padding-right: 17px; /* スクロールバーの幅分を追加 */
  box-sizing: border-box;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .view-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .date-navigation {
    flex-direction: column;
    gap: 10px;
  }
  
  .calendar-header {
    font-size: 0.9em;
  }
  
  .date-header {
    min-width: 80px;
  }
  
  .schedule-column {
    min-width: 80px;
  }
}
</style> 