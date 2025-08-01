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
            'future': isFuture(date)
          }"
        >
          <div class="date-day">{{ getDayOfWeek(date) }}</div>
          <div class="date-number">{{ date.getDate() }}</div>
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
          >
            <div 
              v-for="schedule in getAllDaySchedules(date)" 
              :key="schedule.id"
              class="schedule-item all-day-schedule"
              :style="{ 
                backgroundColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                borderColor: getCategoryColor(schedule.activity_category_id, activityCategories)
              }"
              @click="editSchedule(schedule)"
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
            >
              <div 
                v-for="schedule in getSchedulesAtTime(date, time)" 
                :key="schedule.id"
                class="schedule-item time-schedule"
                :style="{ 
                  backgroundColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                  borderColor: getCategoryColor(schedule.activity_category_id, activityCategories),
                  top: `${getScheduleTopOffset(schedule, time)}px`,
                  height: `${getScheduleHeight(schedule)}px`
                }"
                @click="editSchedule(schedule)"
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
import { ref, computed, onMounted, watch } from 'vue'
import { buildApiUrl } from '../../utils/api'
import { getCategoryColor } from './ScheduleCommon'

// Props
interface Props {
  schedules?: any[]
  activityCategories?: any[]
  selectedCategories?: number[]
}

const props = withDefaults(defineProps<Props>(), {
  schedules: () => [],
  activityCategories: () => [],
  selectedCategories: () => []
})

// Emits
const emit = defineEmits<{
  editSchedule: [schedule: any]
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

// フィルタリングされたスケジュール
const filteredSchedules = computed(() => {
  if (props.selectedCategories.length === 0) return props.schedules
  
  return props.schedules.filter(schedule => 
    props.selectedCategories.includes(schedule.activity_category_id)
  )
})

// 3日表示用のスケジュールデータを取得
async function loadSchedulesFor3Days() {
  if (viewMode.value === '3days') {
    // 3日表示の場合は、表示期間のスケジュールを取得
    const startDate = displayDates.value[0].toISOString().split('T')[0]
    const endDate = displayDates.value[2].toISOString().split('T')[0]
    
    try {
      const response = await fetch(buildApiUrl(`/schedules/week/${startDate}`))
      const data = await response.json()
      // 3日分のデータのみをフィルタリング
      const filteredData = data.filter((schedule: any) => {
        const scheduleDate = new Date(schedule.start_datetime)
        const scheduleDateStr = scheduleDate.toISOString().split('T')[0]
        return scheduleDateStr >= startDate && scheduleDateStr <= endDate
      })
      return filteredData
    } catch (error) {
      console.error('3日表示のスケジュール読み込みに失敗しました:', error)
      return []
    }
  }
  return props.schedules
}

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
  return date.toDateString() === today.toDateString()
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
    const scheduleEndMinutes = scheduleStartMinutes + schedule.duration
    
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

function getScheduleHeight(schedule: any): number {
  // durationは分単位なので、30分間隔のスロットに合わせて計算
  // 30分 = 30px なので、1分 = 1px
  return schedule.duration
}

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

.date-day {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 4px;
}

.date-number {
  font-size: 1.2em;
  font-weight: bold;
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