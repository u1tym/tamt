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
                :style="{ accentColor: getCategoryColor(category.id) }"
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

        <div class="calendar-header">
          <button @click="previousMonth">←</button>
          <h2>{{ currentYear }}年{{ currentMonth }}月</h2>
          <button @click="nextMonth">→</button>
        </div>

        <div class="calendar-controls">
          <label v-if="viewMode === 'month'">
            <input type="checkbox" v-model="startWithMonday" />
            月曜始まり
          </label>
        </div>

        <!-- 月表示 -->
        <div v-if="viewMode === 'month'" class="calendar">
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
             'holiday': date && isHoliday(date)
           }"
           @click="date ? selectDate(date) : null"
         >
                <div class="date-number">{{ date ? date.getDate() : '' }}</div>
                <!-- 休日名称表示 -->
                <div v-if="date && getHolidayName(date)" class="holiday-label">
                  {{ getHolidayName(date) }}
                </div>
                <div class="schedule-items" style="position: relative">
                  <div
                    v-for="schedule in getSchedulesForDate(date)"
                    :key="schedule.id"
                    class="schedule-item"
                    :class="getScheduleClass(schedule, date)"
                    :style="{
                      position: 'absolute',
                      width: '95%',
                      top: (getArrowPosition(schedule, date)) + 'px',
                      borderLeftColor: getCategoryColor(schedule.activity_category_id),
                      backgroundColor: getCategoryBackgroundColor(schedule.activity_category_id)
                    }"
                    @click.stop="editSchedule(schedule)"
                  >
                    <div class="schedule-content">
                      <span class="schedule-time" v-if="!schedule.is_all_day">
                        {{ formatTime(schedule.start_datetime) }}
                      </span>
                      <span class="schedule-title" v-if="!isMultiDayMiddle(schedule, date)">{{ schedule.title }}</span>
                    </div>
                  </div>
                </div>

                <!-- 複数日スケジュールの矢印表示（期間全体） -->
                <div class="multi-day-arrows">
                  <div
                    v-for="schedule in getMultiDaySchedulesForDate(date)"
                    :key="`arrow-${schedule.id}`"
                    class="schedule-arrow"
                    :class="getArrowClass(schedule, date)"
                    :style="{
                      top: (getArrowPosition(schedule, date) + 42) + 'px',
                      '--arrow-color': getCategoryColor(schedule.activity_category_id)
                    }"
                  >

                    <div class="arrow-line" :style="{ backgroundColor: getCategoryColor(schedule.activity_category_id) }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 週間表示 -->
        <div v-else-if="viewMode === 'week'" class="weekly-view">
          <ScheduleWeekly />
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { buildApiUrl } from '../../utils/api'
import ScheduleWeekly from './ScheduleWeekly.vue'

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
    const response = await fetch(buildApiUrl(`/schedules/month/${currentYear.value}/${currentMonth.value}`))
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

  const schedulesForDate = schedules.value.filter(schedule => {
    const scheduleDate = new Date(schedule.start_datetime)
    const scheduleDay = scheduleDate.getDate()
    const scheduleMonth = scheduleDate.getMonth()
    const scheduleYear = scheduleDate.getFullYear()

    // 終日で複数日のスケジュールの場合は開始日のみ表示
    if (schedule.is_all_day && schedule.duration > 1) {
      return date.getTime() === scheduleDate.getTime() &&
             selectedCategories.value.includes(schedule.activity_category_id)
    }

    // 通常のスケジュール（開始日のみ）
    return scheduleDay === date.getDate() &&
           scheduleMonth === date.getMonth() &&
           scheduleYear === date.getFullYear() &&
           selectedCategories.value.includes(schedule.activity_category_id)
  })

  // 複数日に跨るスケジュールを開始日順にソート
  return schedulesForDate.sort((a, b) => {
    const aDate = new Date(a.start_datetime)
    const bDate = new Date(b.start_datetime)
    return aDate.getTime() - bDate.getTime()
  })
}

// 複数日スケジュールの矢印表示用の関数
function getMultiDaySchedulesForDate(date: Date | null) {
  if (!date) return []

  return schedules.value.filter(schedule => {
    if (!schedule.is_all_day || schedule.duration <= 1) return false

    const scheduleDate = new Date(schedule.start_datetime)
    const endDate = new Date(scheduleDate)
    endDate.setDate(endDate.getDate() + schedule.duration - 1)

    // 開始日から終了日までの期間に含まれるかチェック
    return date >= scheduleDate && date <= endDate &&
           selectedCategories.value.includes(schedule.activity_category_id)
  })
}

function getScheduleClass(schedule: any, date: Date) {
  const classes = ['schedule-item']
  if (schedule.is_all_day) {
    classes.push('all-day')

    // 複数日に跨る終日スケジュールの場合
    if (schedule.duration > 1) {
      const scheduleDate = new Date(schedule.start_datetime)
      const endDate = new Date(scheduleDate)
      endDate.setDate(endDate.getDate() + schedule.duration - 1)

      if (date.getTime() === scheduleDate.getTime()) {
        // 開始日
        classes.push('multi-day-start')
      } else if (date.getTime() === endDate.getTime()) {
        // 終了日
        classes.push('multi-day-end')
      } else if (date > scheduleDate && date < endDate) {
        // 中間日
        classes.push('multi-day-middle')
      }
    }
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

function isMultiDayMiddle(schedule: any, date: Date): boolean {
  if (!schedule.is_all_day || schedule.duration <= 1) return false

  const scheduleDate = new Date(schedule.start_datetime)
  const endDate = new Date(scheduleDate)
  endDate.setDate(endDate.getDate() + schedule.duration - 1)

  // 開始日以外（中間日と終了日）はタイトルを非表示
  return date.getTime() !== scheduleDate.getTime()
}

function isMultiDayStart(schedule: any, date: Date): boolean {
  if (!schedule.is_all_day || schedule.duration <= 1) return false

  const scheduleDate = new Date(schedule.start_datetime)
  return date.getTime() === scheduleDate.getTime()
}

function getScheduleDurationText(schedule: any): string {
  if (!schedule.is_all_day || schedule.duration <= 1) return ''

  const scheduleDate = new Date(schedule.start_datetime)
  const endDate = new Date(scheduleDate)
  endDate.setDate(endDate.getDate() + schedule.duration - 1)

  const startMonth = scheduleDate.getMonth() + 1
  const startDay = scheduleDate.getDate()
  const endMonth = endDate.getMonth() + 1
  const endDay = endDate.getDate()

  if (startMonth === endMonth) {
    return `${startDay}日〜${endDay}日`
  } else {
    return `${startMonth}/${startDay}〜${endMonth}/${endDay}`
  }
}

function getArrowClass(schedule: any, date: Date): string {
  const classes = ['schedule-arrow']
  const scheduleDate = new Date(schedule.start_datetime)
  const endDate = new Date(scheduleDate)
  endDate.setDate(endDate.getDate() + schedule.duration - 1)

  if (date.getTime() === scheduleDate.getTime()) {
    // 開始日
    classes.push('arrow-start')
  } else if (date.getTime() === endDate.getTime()) {
    // 終了日
    classes.push('arrow-end')
  } else if (date > scheduleDate && date < endDate) {
    // 中間日
    classes.push('arrow-middle')
  }

  return classes.join(' ')
}

/**
 *
 * @param schedule 評価対象のスケジュール
 * @param date 表示判定対象日
 */
function getArrowPosition(schedule: any, date: Date): number {
  // 評価対象スケジュールの情報
  const sch_st = new Date(schedule.start_datetime)
  const sch_st_y = sch_st.getFullYear()
  const sch_st_m = sch_st.getMonth() + 1
  const sch_st_d = sch_st.getDate()

  // 評価対象日
  const tgt_y = date.getFullYear()
  const tgt_m = date.getMonth() + 1
  const tgt_d = date.getDate()

  if(schedule.is_all_day && schedule.duration > 1
    && (sch_st_y != tgt_y || sch_st_m != tgt_m || sch_st_d != tgt_d)
  ) {
    // 複数日に跨るスケジュールの順番は、開始日での順番
    return getArrowPosition(schedule, sch_st)
  }

  //if(! schedule.is_all_day) {
  //  return 0
  //}

  const st = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const ed = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1)

  //console.log("開始 " + st)
  //console.log("終了 " + ed)
  //console.log(JSON.stringify(schedule))

  // 複数日スケジュールを開始日順にソートして、何番目かを計算
  const multiDaySchedules = schedules.value
    .filter((s) => {
      // console.log('★' + JSON.stringify(s))
      let ist = new Date(s.start_datetime)
      let ied = new Date(s.start_datetime)
      if (s.is_all_day) {
        // 終日
        ied = new Date(ist.getFullYear(), ist.getMonth(), ist.getDate() + s.duration - 1, 23, 59, 59)
      } else {
        // 当日内
        ied = new Date(ist.getFullYear(), ist.getMonth(), ist.getDate(), ist.getHours(), ist.getMinutes() + s.duration, 0)
      }

      // console.log("判断対象 " + ist + " - " + ied)

      let res = false
      if(ist < ed && st < ied) {
        res = true
      }

      return res
    })
    //.filter(s => s.is_all_day && s.duration > 1 && selectedCategories.value.includes(s.activity_category_id))
    .sort((a, b) => {

      // 終日のものが優先
      if(a.is_all_day && (!b.is_all_day)) {
        return -1
      }
      else if((!a.is_all_day) && b.is_all_day){
        return 1
      }

      // 複数期間のものが優先
      if(a.is_all_day && b.is_all_day) {
        if(a.duration == 1 && b.duration > 1) {
          return 1
        }
        else if(a.duration > 1 && b.duration == 1){
          return -1
        }
      }

      const res = new Date(a.start_datetime).getTime() - new Date(b.start_datetime).getTime()
      if(res != 0) {
        return res
      }
      if(a.title > b.title){
        return 1
      }
      return 0
    })

  // このスケジュールが何番目かを取得
  const scheduleIndex = multiDaySchedules.findIndex(s => s.id === schedule.id)
  console.log(schedule.title + " result = " + scheduleIndex)

  // 各スケジュールの矢印を20pxずつずらして表示
  return scheduleIndex * 20
}

// 活動区分の色を取得する関数
function getCategoryColor(categoryId: number): string {
  const colors = [
    '#2196F3', // 青
    '#4CAF50', // 緑
    '#FF9800', // オレンジ
    '#9C27B0', // 紫
    '#F44336', // 赤
    '#00BCD4', // シアン
    '#FF5722', // ディープオレンジ
    '#795548', // ブラウン
    '#607D8B', // ブルーグレー
    '#E91E63', // ピンク
    '#3F51B5', // インディゴ
    '#8BC34A', // ライトグリーン
    '#FFC107', // アンバー
    '#009688', // ティール
    '#673AB7'  // ディープパープル
  ]

  const categoryIndex = activityCategories.value.findIndex(cat => cat.id === categoryId)
  if (categoryIndex >= 0) {
    return colors[categoryIndex % colors.length]
  }
  return '#2196F3' // デフォルト色
}

// 活動区分の背景色を取得する関数
function getCategoryBackgroundColor(categoryId: number): string {
  const backgroundColors = [
    '#E3F2FD', // 青の背景
    '#E8F5E8', // 緑の背景
    '#FFF3E0', // オレンジの背景
    '#F3E5F5', // 紫の背景
    '#FFEBEE', // 赤の背景
    '#E0F2F1', // シアンの背景
    '#FBE9E7', // ディープオレンジの背景
    '#EFEBE9', // ブラウンの背景
    '#ECEFF1', // ブルーグレーの背景
    '#FCE4EC', // ピンクの背景
    '#E8EAF6', // インディゴの背景
    '#F1F8E9', // ライトグリーンの背景
    '#FFF8E1', // アンバーの背景
    '#E0F2F1', // ティールの背景
    '#EDE7F6'  // ディープパープルの背景
  ]

  const categoryIndex = activityCategories.value.findIndex(cat => cat.id === categoryId)
  if (categoryIndex >= 0) {
    return backgroundColors[categoryIndex % backgroundColors.length]
  }
  return '#E3F2FD' // デフォルト背景色
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

// 休日管理
function formatHolidayDate(dateString: string): string {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${String(date.getMonth() + 1).padStart(2, '0')}月${String(date.getDate()).padStart(2, '0')}日`
}

function isHoliday(date: Date): boolean {
  return holidays.value.some(holiday => {
    const holidayDate = new Date(holiday.date)
    return holidayDate.getFullYear() === date.getFullYear() &&
           holidayDate.getMonth() === date.getMonth() &&
           holidayDate.getDate() === date.getDate()
  })
}

function getHolidayName(date: Date): string | null {
  const holiday = holidays.value.find(h => {
    const holidayDate = new Date(h.date)
    return holidayDate.getFullYear() === date.getFullYear() &&
           holidayDate.getMonth() === date.getMonth() &&
           holidayDate.getDate() === date.getDate()
  })
  return holiday ? holiday.name : null
}



// 監視
watch([currentYear, currentMonth], () => {
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
  display: flex;
  align-items: center;
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

.weekly-view {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
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
  position: relative;
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
}

.date-number {
  font-weight: bold;
  margin-bottom: 4px;
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
</style>