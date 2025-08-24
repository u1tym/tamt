// APIエンドポイントのベースURLを動的に取得
export const getApiBaseUrl = (): string => {
  // 開発環境では現在のホストを使用
  if (import.meta.env.DEV) {
    const currentHost = window.location.hostname
    const currentPort = window.location.port

    // フロントエンドが5901ポートの場合、バックエンドは5902ポート
    if (currentPort === '5901') {
      return `http://${currentHost}:5902`
    }
    return `http://${currentHost}:5902`
  }
  // 本番環境では相対パスを使用
  return `http://${window.location.hostname}:5902`
}

// APIエンドポイントを構築するヘルパー関数
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl()
  return `${baseUrl}${endpoint}`
}

// セッション情報を取得する関数
const getSessionInfo = () => {
  const username = localStorage.getItem('username') || ''
  const sessionToken = localStorage.getItem('sessionToken') || ''
  return { username, sessionToken }
}

// APIリクエストの設定
const API_CONFIG = {
  timeout: 30000, // 30秒
  maxRetries: 3,
  retryDelay: 1000, // 1秒
  enableLogging: import.meta.env.DEV
}

// ログ機能
const log = (level: 'info' | 'warn' | 'error', message: string, data?: any) => {
  if (!API_CONFIG.enableLogging) return

  const timestamp = new Date().toISOString()
  const logMessage = `[API ${level.toUpperCase()}] ${timestamp}: ${message}`

  switch (level) {
    case 'info':
      console.log(logMessage, data)
      break
    case 'warn':
      console.warn(logMessage, data)
      break
    case 'error':
      console.error(logMessage, data)
      break
  }
}

// タイムアウト付きfetch
const fetchWithTimeout = async (url: string, options: RequestInit, timeout: number): Promise<Response> => {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeout)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    })
    clearTimeout(timeoutId)
    return response
  } catch (error) {
    clearTimeout(timeoutId)
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`)
    }
    throw error
  }
}

// リトライ機能付きタスク実行
const executeWithRetry = async <T>(
  task: () => Promise<T>,
  maxRetries: number = API_CONFIG.maxRetries,
  retryDelay: number = API_CONFIG.retryDelay
): Promise<T> => {
  let lastError: Error

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await task()
    } catch (error) {
      lastError = error as Error

      if (attempt === maxRetries) {
        log('error', `Task failed after ${maxRetries} attempts`, { error: lastError.message })
        throw lastError
      }

      log('warn', `Task failed (attempt ${attempt}/${maxRetries}), retrying in ${retryDelay}ms`, { error: lastError.message })
      await new Promise(resolve => setTimeout(resolve, retryDelay))

      // 指数バックオフ（リトライ間隔を徐々に増加）
      retryDelay *= 1.5
    }
  }

  throw lastError!
}

// シーケンシャル実行のためのキューシステム（強化版）
class ApiQueue {
  private queue: Array<{
    id: string
    task: () => Promise<any>
    resolve: (value: any) => void
    reject: (error: any) => void
    timestamp: number
  }> = []
  private isProcessing = false
  private requestId = 0

  async add<T>(task: () => Promise<T>): Promise<T> {
    const id = `req_${++this.requestId}`
    const timestamp = Date.now()

    log('info', `Adding request to queue`, { id, queueLength: this.queue.length })

    return new Promise((resolve, reject) => {
      this.queue.push({
        id,
        task,
        resolve,
        reject,
        timestamp
      })
      this.processQueue()
    })
  }

  private async processQueue() {
    if (this.isProcessing || this.queue.length === 0) {
      return
    }

    this.isProcessing = true
    log('info', `Starting queue processing`, { queueLength: this.queue.length })

    while (this.queue.length > 0) {
      const request = this.queue.shift()
      if (request) {
        const { id, task, resolve, reject, timestamp } = request
        const processingTime = Date.now() - timestamp

        log('info', `Processing request`, { id, processingTime, queueLength: this.queue.length })

        try {
          const result = await executeWithRetry(task)
          log('info', `Request completed successfully`, { id })
          resolve(result)
        } catch (error) {
          log('error', `Request failed`, { id, error: (error as Error).message })
          reject(error)
        }
      }
    }

    this.isProcessing = false
    log('info', `Queue processing completed`)
  }

  // キューの状態を取得
  getStatus() {
    return {
      isProcessing: this.isProcessing,
      queueLength: this.queue.length,
      totalRequests: this.requestId
    }
  }

  // キューをクリア（緊急時用）
  clear() {
    const clearedCount = this.queue.length
    this.queue.forEach(request => {
      request.reject(new Error('Queue cleared'))
    })
    this.queue = []
    log('warn', `Queue cleared`, { clearedCount })
  }
}

// グローバルAPIキューインスタンス
const apiQueue = new ApiQueue()

// APIクライアントの設定（シーケンシャル実行）
const api = {
  get: async (endpoint: string) => {
    return apiQueue.add(async () => {
      const { username, sessionToken } = getSessionInfo()
      log('info', `GET request`, { endpoint })

      const response = await fetchWithTimeout(
        buildApiUrl(endpoint),
        {
          headers: {
            'X-Username': username,
            'X-Session-Token': sessionToken,
          },
        },
        API_CONFIG.timeout
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      log('info', `GET request completed`, { endpoint, status: response.status })
      return result
    })
  },

  post: async (endpoint: string, data: any) => {
    return apiQueue.add(async () => {
      const { username, sessionToken } = getSessionInfo()
      log('info', `POST request`, { endpoint, dataSize: JSON.stringify(data).length })

      const response = await fetchWithTimeout(
        buildApiUrl(endpoint),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Username': username,
            'X-Session-Token': sessionToken,
          },
          body: JSON.stringify(data),
        },
        API_CONFIG.timeout
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      log('info', `POST request completed`, { endpoint, status: response.status })
      return result
    })
  },

  put: async (endpoint: string, data: any) => {
    return apiQueue.add(async () => {
      const { username, sessionToken } = getSessionInfo()
      log('info', `PUT request`, { endpoint, dataSize: JSON.stringify(data).length })

      const response = await fetchWithTimeout(
        buildApiUrl(endpoint),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'X-Username': username,
            'X-Session-Token': sessionToken,
          },
          body: JSON.stringify(data),
        },
        API_CONFIG.timeout
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      log('info', `PUT request completed`, { endpoint, status: response.status })
      return result
    })
  },

  delete: async (endpoint: string) => {
    return apiQueue.add(async () => {
      const { username, sessionToken } = getSessionInfo()
      log('info', `DELETE request`, { endpoint })

      const response = await fetchWithTimeout(
        buildApiUrl(endpoint),
        {
          method: 'DELETE',
          headers: {
            'X-Username': username,
            'X-Session-Token': sessionToken,
          },
        },
        API_CONFIG.timeout
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      log('info', `DELETE request completed`, { endpoint, status: response.status })
      return result
    })
  }
}

// キュー状態を監視する関数（デバッグ用）
export const getApiQueueStatus = () => {
  return apiQueue.getStatus()
}

// キューをクリアする関数（緊急時用）
export const clearApiQueue = () => {
  apiQueue.clear()
}

// バッチ処理用のヘルパー関数
export const batchApiCalls = async <T>(
  calls: Array<() => Promise<T>>,
  onProgress?: (completed: number, total: number) => void
): Promise<T[]> => {
  const results: T[] = []
  const total = calls.length

  for (let i = 0; i < calls.length; i++) {
    try {
      const result = await calls[i]()
      results.push(result)
      onProgress?.(i + 1, total)
    } catch (error) {
      log('error', `Batch call failed at index ${i}`, { error: (error as Error).message })
      throw error
    }
  }

  return results
}

// プログレス監視付きAPI呼び出し
export const createProgressMonitor = () => {
  let completed = 0
  let total = 0
  let startTime = 0

  return {
    start: (totalCalls: number) => {
      completed = 0
      total = totalCalls
      startTime = Date.now()
      log('info', `Progress monitor started`, { total: totalCalls })
    },

    increment: () => {
      completed++
      const progress = (completed / total) * 100
      const elapsed = Date.now() - startTime
      const estimatedTotal = elapsed * (total / completed)
      const remaining = estimatedTotal - elapsed

      log('info', `Progress update`, {
        completed,
        total,
        progress: `${progress.toFixed(1)}%`,
        elapsed: `${(elapsed / 1000).toFixed(1)}s`,
        remaining: `${(remaining / 1000).toFixed(1)}s`
      })

      return { completed, total, progress, elapsed, remaining }
    },

    getStatus: () => ({
      completed,
      total,
      progress: total > 0 ? (completed / total) * 100 : 0,
      elapsed: Date.now() - startTime,
      isComplete: completed >= total
    })
  }
}

// アカウント管理用のAPI
export const getAccounts = () => api.get('/account/accounts')
export const getAccount = (id: number) => api.get(`/account/accounts/${id}`)
export const createAccount = (data: any) => api.post('/account/accounts', data)
export const updateAccount = (id: number, data: any) => api.put(`/account/accounts/${id}`, data)
export const deleteAccount = (id: number) => api.delete(`/account/accounts/${id}`)

// ログイン用のAPI
export const requestRandomNumber = (data: any) => api.post('/login/request-random', data)
export const verifyLogin = (data: any) => api.post('/login/verify', data)

// 予算管理用のAPI
export const getBudgets = (year: number, month: number) => api.get(`/cash/budgets/${year}/${month}`)
export const getBudgetSummaries = (year: number, month: number) => api.get(`/cash/budgets/${year}/${month}/summary`)
export const createBudget = (data: any) => api.post('/cash/budgets', data)
export const updateBudget = (id: number, data: any) => api.put(`/cash/budgets/${id}`, data)
export const deleteBudget = (id: number) => api.delete(`/cash/budgets/${id}`)
export const moveBudgetUp = (id: number) => api.post(`/cash/budgets/${id}/move-up`, {})
export const moveBudgetDown = (id: number) => api.post(`/cash/budgets/${id}/move-down`, {})
export const copyBudgets = (sourceYear: number, sourceMonth: number, targetYear: number, targetMonth: number) =>
  api.post(`/cash/budgets/copy?source_year=${sourceYear}&source_month=${sourceMonth}&target_year=${targetYear}&target_month=${targetMonth}`, {})

// 取引管理用のAPI
export const getTransactions = (skip: number = 0, limit: number = 100) => api.get(`/cash/transactions?skip=${skip}&limit=${limit}`)
export const createTransaction = (data: any) => api.post('/cash/transactions', data)
export const updateTransaction = (id: number, data: any) => api.put(`/cash/transactions/${id}`, data)
export const deleteTransaction = (id: number) => api.delete(`/cash/transactions/${id}`)
export const getPaymentSources = () => api.get('/cash/payment_sources')
export const createPaymentSource = (data: any) => api.post('/cash/payment_sources', data)
export const updatePaymentSource = (id: number, data: any) => api.put(`/cash/payment_sources/${id}`, data)
export const deletePaymentSource = (id: number) => api.delete(`/cash/payment_sources/${id}`)
export const getDebitSummary = () => api.get('/cash/debit-summary')
export const getPaymentSummary = () => api.get('/cash/payment-summary')
export const calculatePaymentDate = (data: any) => api.post('/cash/calculate-payment-date', data)
export const getBudgetNames = (dateStr: string) => api.get(`/cash/budget-names?date_str=${dateStr}`)

// 商品管理用のAPI
export const getGoods = (skip: number = 0, limit: number = 1000) => api.get(`/goods/goods?skip=${skip}&limit=${limit}`)
export const getGoodsWithDetails = (id: number) => api.get(`/goods/goods/${id}/with-details`)
export const createGoods = (data: any) => api.post('/goods/goods', data)
export const updateGoods = (id: number, data: any) => api.put(`/goods/goods/${id}`, data)
export const deleteGoods = (id: number) => api.delete(`/goods/goods/${id}`)
export const getArtists = (skip: number = 0, limit: number = 100) => api.get(`/goods/artists?skip=${skip}&limit=${limit}`)
export const getArtistWithPersons = (id: number) => api.get(`/goods/artists/${id}/with-persons`)
export const createArtist = (data: any) => api.post('/goods/artists', data)
export const updateArtist = (id: number, data: any) => api.put(`/goods/artists/${id}`, data)
export const deleteArtist = (id: number) => api.delete(`/goods/artists/${id}`)
export const getPersons = (skip: number = 0, limit: number = 100) => api.get(`/goods/persons?skip=${skip}&limit=${limit}`)
export const createPerson = (data: any) => api.post('/goods/persons', data)
export const updatePerson = (id: number, data: any) => api.put(`/goods/persons/${id}`, data)
export const deletePerson = (id: number) => api.delete(`/goods/persons/${id}`)
export const getMedia = (skip: number = 0, limit: number = 100) => api.get(`/goods/media?skip=${skip}&limit=${limit}`)
export const createMedia = (data: any) => api.post('/goods/media', data)
export const updateMedia = (id: number, data: any) => api.put(`/goods/media/${id}`, data)
export const deleteMedia = (id: number) => api.delete(`/goods/media/${id}`)

// 休日管理用のAPI
export const getHolidays = () => api.get('/holiday/holidays')
export const getHolidaysByMonth = (year: number, month: number) => api.get(`/holiday/holidays/month/${year}/${month}`)
export const createHoliday = (data: any) => api.post('/holiday/holidays', data)
export const updateHoliday = (id: number, data: any) => api.put(`/holiday/holidays/${id}`, data)
export const deleteHoliday = (id: number) => api.delete(`/holiday/holidays/${id}`)

// ナレッジ管理用のAPI
export const getKnowhows = (skip: number = 0, limit: number = 100) => api.get(`/knowhow/knowhows?skip=${skip}&limit=${limit}`)
export const getKnowhowTree = () => api.get('/knowhow/knowhows/tree')
export const getKnowhow = (id: number) => api.get(`/knowhow/knowhows/${id}`)
export const createKnowhow = (data: any) => api.post('/knowhow/knowhows', data)
export const updateKnowhow = (id: number, data: any) => api.put(`/knowhow/knowhows/${id}`, data)
export const deleteKnowhow = (id: number) => api.delete(`/knowhow/knowhows/${id}`)
export const moveKnowhowUp = (id: number) => api.post(`/knowhow/knowhows/${id}/move-up`, {})
export const moveKnowhowDown = (id: number) => api.post(`/knowhow/knowhows/${id}/move-down`, {})
export const getMajorCategories = (skip: number = 0, limit: number = 100) => api.get(`/knowhow/major-categories?skip=${skip}&limit=${limit}`)
export const createMajorCategory = (data: any) => api.post('/knowhow/major-categories', data)
export const updateMajorCategory = (id: number, data: any) => api.put(`/knowhow/major-categories/${id}`, data)
export const deleteMajorCategory = (id: number) => api.delete(`/knowhow/major-categories/${id}`)
export const getMiddleCategories = (skip: number = 0, limit: number = 100) => api.get(`/knowhow/middle-categories?skip=${skip}&limit=${limit}`)
export const createMiddleCategory = (data: any) => api.post('/knowhow/middle-categories', data)
export const updateMiddleCategory = (id: number, data: any) => api.put(`/knowhow/middle-categories/${id}`, data)
export const deleteMiddleCategory = (id: number) => api.delete(`/knowhow/middle-categories/${id}`)

// スケジュール管理用のAPI
export const getSchedules = (skip: number = 0, limit: number = 100) => api.get(`/schedule/schedules?skip=${skip}&limit=${limit}`)
export const getSchedulesByMonth = (year: number, month: number) => api.get(`/schedule/schedules/month/${year}/${month}`)
export const getSchedulesByWeek = (startDate: string) => api.get(`/schedule/schedules/week/${startDate}`)
export const getSchedulesByActivityCategories = (year: number, month: number, categoryIds: string) =>
  api.get(`/schedule/schedules/filtered/${year}/${month}?category_ids=${categoryIds}`)
export const createSchedule = (data: any) => api.post('/schedule/schedules', data)
export const updateSchedule = (id: number, data: any) => api.put(`/schedule/schedules/${id}`, data)
export const deleteSchedule = (id: number) => api.delete(`/schedule/schedules/${id}`)
export const getActivityCategories = (skip: number = 0, limit: number = 100) => api.get(`/schedule/activity-categories?skip=${skip}&limit=${limit}`)
export const createActivityCategory = (data: any) => api.post('/schedule/activity-categories', data)
export const updateActivityCategory = (id: number, data: any) => api.put(`/schedule/activity-categories/${id}`, data)
export const deleteActivityCategory = (id: number) => api.delete(`/schedule/activity-categories/${id}`)
