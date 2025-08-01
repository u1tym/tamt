// 活動区分の色を取得する関数
export function getCategoryColor(categoryId: number, activityCategories: any[]): string {
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

  const categoryIndex = activityCategories.findIndex(cat => cat.id === categoryId)
  if (categoryIndex >= 0) {
    return colors[categoryIndex % colors.length]
  }
  return '#2196F3' // デフォルト色
}

// 活動区分の背景色を取得する関数
export function getCategoryBackgroundColor(categoryId: number, activityCategories: any[]): string {
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

  const categoryIndex = activityCategories.findIndex(cat => cat.id === categoryId)
  if (categoryIndex >= 0) {
    return backgroundColors[categoryIndex % backgroundColors.length]
  }
  return '#E3F2FD' // デフォルト背景色
}

// 時間フォーマット関数
export function formatTime(datetime: string): string {
  const date = new Date(datetime)
  return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

// 休日判定関数
export function isHoliday(date: Date, holidays: any[]): boolean {
  return holidays.some(holiday => {
    const holidayDate = new Date(holiday.date)
    return holidayDate.getFullYear() === date.getFullYear() &&
           holidayDate.getMonth() === date.getMonth() &&
           holidayDate.getDate() === date.getDate()
  })
}

// 休日名称取得関数
export function getHolidayName(date: Date, holidays: any[]): string | null {
  const holiday = holidays.find(h => {
    const holidayDate = new Date(h.date)
    return holidayDate.getFullYear() === date.getFullYear() &&
           holidayDate.getMonth() === date.getMonth() &&
           holidayDate.getDate() === date.getDate()
  })
  return holiday ? holiday.name : null
}

// スケジュールクラス取得関数
export function getScheduleClass(schedule: any, date: Date): string {
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

// 複数日中間判定関数
export function isMultiDayMiddle(schedule: any, date: Date): boolean {
  if (!schedule.is_all_day || schedule.duration <= 1) return false

  const scheduleDate = new Date(schedule.start_datetime)
  const endDate = new Date(scheduleDate)
  endDate.setDate(endDate.getDate() + schedule.duration - 1)

  // 開始日以外（中間日と終了日）はタイトルを非表示
  return date.getTime() !== scheduleDate.getTime()
}

// 矢印クラス取得関数
export function getArrowClass(schedule: any, date: Date): string {
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

// 矢印位置取得関数
export function getArrowPosition(schedule: any, date: Date, schedules: any[]): number {
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
    return getArrowPosition(schedule, sch_st, schedules)
  }

  const st = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const ed = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1)

  // 複数日スケジュールを開始日順にソートして、何番目かを計算
  const multiDaySchedules = schedules
    .filter((s) => {
      let ist = new Date(s.start_datetime)
      let ied = new Date(s.start_datetime)
      if (s.is_all_day) {
        // 終日
        ied = new Date(ist.getFullYear(), ist.getMonth(), ist.getDate() + s.duration - 1, 23, 59, 59)
      } else {
        // 当日内
        ied = new Date(ist.getFullYear(), ist.getMonth(), ist.getDate(), ist.getHours(), ist.getMinutes() + s.duration, 0)
      }

      let res = false
      if(ist < ed && st < ied) {
        res = true
      }

      return res
    })
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

  // 各スケジュールの矢印を20pxずつずらして表示
  return scheduleIndex * 20
}

// 指定日のスケジュール取得関数
export function getSchedulesForDate(date: Date | null, schedules: any[], selectedCategories: number[]): any[] {
  if (!date) return []

  const schedulesForDate = schedules.filter(schedule => {
    const scheduleDate = new Date(schedule.start_datetime)
    const scheduleDay = scheduleDate.getDate()
    const scheduleMonth = scheduleDate.getMonth()
    const scheduleYear = scheduleDate.getFullYear()

    // 終日で複数日のスケジュールの場合は開始日のみ表示
    if (schedule.is_all_day && schedule.duration > 1) {
      return date.getTime() === scheduleDate.getTime() &&
             selectedCategories.includes(schedule.activity_category_id)
    }

    // 通常のスケジュール（開始日のみ）
    return scheduleDay === date.getDate() &&
           scheduleMonth === date.getMonth() &&
           scheduleYear === date.getFullYear() &&
           selectedCategories.includes(schedule.activity_category_id)
  })

  // 複数日に跨るスケジュールを開始日順にソート
  return schedulesForDate.sort((a, b) => {
    const aDate = new Date(a.start_datetime)
    const bDate = new Date(b.start_datetime)
    return aDate.getTime() - bDate.getTime()
  })
}

// 複数日スケジュールの矢印表示用の関数
export function getMultiDaySchedulesForDate(date: Date | null, schedules: any[], selectedCategories: number[]): any[] {
  if (!date) return []

  return schedules.filter(schedule => {
    if (!schedule.is_all_day || schedule.duration <= 1) return false

    const scheduleDate = new Date(schedule.start_datetime)
    const endDate = new Date(scheduleDate)
    endDate.setDate(endDate.getDate() + schedule.duration - 1)

    // 開始日から終了日までの期間に含まれるかチェック
    return date >= scheduleDate && date <= endDate &&
           selectedCategories.includes(schedule.activity_category_id)
  })
} 