<template>
  <div class="calendar">
    <!-- 年月表示とナビゲーションボタン -->
    <div class="calendar-header">
      <button @click="previousMonth">←</button>
      <h2>{{ currentYear }}年{{ currentMonth }}月</h2>
      <button @click="nextMonth">→</button>
    </div>

    <!-- 月曜始まり設定 -->
    <div class="calendar-controls">
      <label>
        <input type="checkbox" :checked="startWithMonday" @change="toggleMondayStart" />
        月曜始まり
      </label>
    </div>

    <!-- 曜日ヘッダー -->
    <div class="calendar-header-row">
      <div v-for="day in weekDays" :key="day" class="calendar-header-cell">
        {{ day }}
      </div>
    </div>

    <!-- カレンダー本体 -->
    <div class="calendar-body">
      <div v-for="week in calendarWeeks" :key="week[0] ? week[0].toISOString() : 'empty'" class="calendar-week">
        <div
          v-for="date in week"
          :key="date ? date.toISOString() : 'empty'"
          class="calendar-day"
                      :class="{ 
              'other-month': !date || date.getMonth() !== currentMonth - 1,
              'sunday': date && date.getDay() === 0,
              'saturday': date && date.getDay() === 6,
              'holiday': date && isHoliday(date, props.holidays)
            }"
          @click="date ? selectDate(date) : null"
        >
          <div class="date-number" :class="{ 'today': date && isToday(date) }">{{ date ? date.getDate() : '' }}</div>
                          <!-- 休日名称表示 -->
                <div v-if="date && getHolidayName(date, props.holidays)" class="holiday-label">
                  {{ getHolidayName(date, props.holidays) }}
                </div>
                <div class="schedule-items" style="position: relative">
                  <div
                    v-for="schedule in getSchedulesForDate(date, props.schedules, props.selectedCategories)"
                    :key="schedule.id"
                    class="schedule-item"
                    :class="getScheduleClass(schedule, date)"
                    :style="{
                      position: 'absolute',
                      width: '95%',
                      top: (getArrowPosition(schedule, date, props.schedules)) + 'px',
                      borderLeftColor: getCategoryColor(schedule.activity_category_id, props.activityCategories),
                      backgroundColor: getCategoryBackgroundColor(schedule.activity_category_id, props.activityCategories)
                    }"
                    @click.stop="editSchedule(schedule)"
                  >
                    <div class="schedule-content">
                      <span class="schedule-time" v-if="!schedule.is_all_day">
                        {{ formatTime(schedule.start_datetime) }}
                      </span>
                      <!-- TODOタイプの場合はチェックボックスを表示 -->
                      <span v-if="schedule.schedule_type === 'TODO'" class="todo-checkbox">
                        <input 
                          type="checkbox" 
                          :checked="schedule.is_todo_completed" 
                          disabled 
                          class="todo-checkbox-input"
                        />
                      </span>
                      <span class="schedule-title" v-if="!isMultiDayMiddle(schedule, date)">{{ schedule.title }}</span>
                    </div>
                  </div>
                </div>

                <!-- 複数日スケジュールの矢印表示（期間全体） -->
                <div class="multi-day-arrows">
                  <div
                    v-for="schedule in getMultiDaySchedulesForDate(date, props.schedules, props.selectedCategories)"
                    :key="`arrow-${schedule.id}`"
                    class="schedule-arrow"
                    :class="getArrowClass(schedule, date)"
                    :style="{
                      top: (getArrowPosition(schedule, date, props.schedules) + 42) + 'px',
                      '--arrow-color': getCategoryColor(schedule.activity_category_id, props.activityCategories)
                    }"
                  >
                    <div class="arrow-line" :style="{ backgroundColor: getCategoryColor(schedule.activity_category_id, props.activityCategories) }"></div>
                  </div>
                </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  getCategoryColor,
  getCategoryBackgroundColor,
  formatTime,
  isHoliday,
  getHolidayName,
  getScheduleClass,
  isMultiDayMiddle,
  getArrowClass,
  getArrowPosition,
  getSchedulesForDate,
  getMultiDaySchedulesForDate
} from './ScheduleCommon'

// Props
interface Props {
  currentYear: number
  currentMonth: number
  startWithMonday: boolean
  schedules: any[]
  selectedCategories: number[]
  activityCategories: any[]
  holidays: any[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  selectDate: [date: Date]
  editSchedule: [schedule: any]
  previousMonth: []
  nextMonth: []
  toggleMondayStart: [value: boolean]
}>()

// Navigation functions
function previousMonth() {
  emit('previousMonth')
}

function nextMonth() {
  emit('nextMonth')
}

function toggleMondayStart(event: Event) {
  const target = event.target as HTMLInputElement
  emit('toggleMondayStart', target.checked)
}

// 曜日配列
const weekDays = computed(() => {
  if (props.startWithMonday) {
    return ['月', '火', '水', '木', '金', '土', '日']
  } else {
    return ['日', '月', '火', '水', '木', '金', '土']
  }
})

// カレンダーの週配列を生成
const calendarWeeks = computed(() => {
  const firstDay = new Date(props.currentYear, props.currentMonth - 1, 1)
  const lastDay = new Date(props.currentYear, props.currentMonth, 0)

  // 月の最初の日の曜日を取得（0=日曜日, 1=月曜日, ...）
  let firstDayOfWeek = firstDay.getDay()
  if (props.startWithMonday) {
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
    currentWeek.push(new Date(props.currentYear, props.currentMonth - 1, day))
  }

  // 翌月の日を追加（最後の週を7日で埋める）
  let nextDay = 1
  while (currentWeek.length < 7) {
    const nextDate = new Date(props.currentYear, props.currentMonth, nextDay)
    currentWeek.push(nextDate)
    nextDay++
  }

  if (currentWeek.length > 0) {
    weeks.push(currentWeek)
  }

  return weeks
})

// 今日の日付かどうかを判定する関数
function isToday(date: Date): boolean {
  const today = new Date()
  return date.getDate() === today.getDate() &&
         date.getMonth() === today.getMonth() &&
         date.getFullYear() === today.getFullYear()
}

// メソッド
function selectDate(date: Date) {
  emit('selectDate', date)
}

function editSchedule(schedule: any) {
  emit('editSchedule', schedule)
}


</script>

<style scoped>
.calendar {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.calendar-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.calendar-header button {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.calendar-header button:hover {
  background: #0056b3;
}

.calendar-controls {
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.calendar-controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.calendar-controls input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.calendar-header-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f0f0f0;
}

.calendar-body {
  overflow-y: auto;
  flex: 1;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.calendar-body::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.calendar-header-cell {
  padding: 12px;
  text-align: center;
  font-weight: bold;
  border-right: 1px solid #ddd;
}

.calendar-header-cell:last-child {
  border-right: none;
  margin-right: 0;
}

.calendar-week {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  min-height: 120px;
}

.calendar-day {
  min-height: 120px;
  height: 120px;
  border-right: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
  padding: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.calendar-day:hover {
  background: #f9f9f9;
}

.calendar-day.other-month {
  background: #f9f9f9;
  color: #999;
}

.calendar-day.sunday {
  background: #fff0f0;
  color: #ff4444;
}

.calendar-day.saturday {
  background: #f0f8ff;
  color: #0066cc;
}

.calendar-day.holiday {
  background: #ffe6e6;
}

.calendar-day:last-child {
  border-right: none;
  margin-right: 0;
}

.date-number {
  font-weight: bold;
  margin-bottom: 4px;
}

.date-number.today {
  background: #007bff;
  color: white;
  border-radius: 4px;
  padding: 2px 6px;
  display: inline-block;
  min-width: 20px;
  text-align: center;
}

.holiday-label {
  position: absolute;
  top: 4px;
  right: 4px;
  background: #ff4444;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: bold;
  z-index: 2;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.schedule-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-item {
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 11px;
  cursor: pointer;
  border-left: 3px solid;
  position: relative;
}

/* 複数日に跨る終日スケジュールのスタイル */
.schedule-item.multi-day-start {
  border-radius: 2px 0 0 2px;
  margin-right: -8px;
  padding-right: 8px;
  padding-top: 1px;
  padding-bottom: 1px;
  position: relative;
}

.schedule-item.multi-day-middle {
  border-left: none;
  border-radius: 0;
  margin-right: -8px;
  padding-right: 8px;
  padding-left: 8px;
  padding-top: 1px;
  padding-bottom: 1px;
  position: relative;
}

.schedule-item.multi-day-end {
  border-left: none;
  border-radius: 0 2px 2px 0;
  padding-left: 8px;
  padding-top: 1px;
  padding-bottom: 1px;
  position: relative;
}

/* 複数日に跨るスケジュールの位置を統一 */
.schedule-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
  position: relative;
}

/* 複数日に跨るスケジュールの位置を統一するためのスタイル */
.schedule-item[class*="multi-day"] {
  order: 0;
  min-height: 16px;
  display: flex;
  align-items: center;
}

/* 通常のスケジュールは後ろに配置 */
.schedule-item:not([class*="multi-day"]) {
  order: 1;
}

/* 複数日スケジュールの矢印表示 */
.multi-day-arrows {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.schedule-arrow {
  position: absolute;
  left: 0;
  right: 0;
  height: 20px;
  pointer-events: none;
}

.arrow-text {
  position: absolute;
  top: -2px;
  right: 4px;
  background: #fff3e0;
  padding: 1px 4px;
  border-radius: 2px;
  font-size: 9px;
  color: #ff9800;
  font-weight: bold;
  border: 1px solid #ff9800;
  z-index: 2;
}

.arrow-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: #ff9800;
  transform: translateY(-50%);
}

/* 矢印の開始日 */
.schedule-arrow.arrow-start .arrow-line {
  border-radius: 2px 0 0 2px;
}

.schedule-arrow.arrow-start .arrow-line::before {
  content: '';
  position: absolute;
  left: -4px;
  top: -3px;
  width: 0;
  height: 0;
  border-right: 8px solid var(--arrow-color, #ff9800);
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}

/* 矢印の中間日 */
.schedule-arrow.arrow-middle .arrow-line {
  border-radius: 0;
}

/* 矢印の終了日 */
.schedule-arrow.arrow-end .arrow-line {
  border-radius: 0 2px 2px 0;
}

.schedule-arrow.arrow-end .arrow-line::after {
  content: '';
  position: absolute;
  right: -4px;
  top: -3px;
  width: 0;
  height: 0;
  border-left: 8px solid var(--arrow-color, #ff9800);
  border-top: 4px solid transparent;
  border-bottom: 4px solid transparent;
}

.schedule-item.todo {
  /* 背景色は動的に設定されるため、ここでは設定しない */
}

.schedule-item.completed {
  opacity: 0.6;
  text-decoration: line-through;
}

.schedule-content {
  display: flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
  white-space: nowrap;
}

.schedule-time {
  font-size: 10px;
  color: #666;
  flex-shrink: 0;
}

.schedule-title {
  font-weight: bold;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.todo-checkbox {
  display: flex;
  align-items: center;
  margin-right: 4px;
  flex-shrink: 0;
}

.todo-checkbox-input {
  margin: 0;
  cursor: default;
  pointer-events: none;
  width: 12px;
  height: 12px;
  accent-color: #4CAF50;
}

.todo-checkbox-input:checked {
  background-color: #4CAF50;
  border-color: #4CAF50;
}
</style> 