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

// APIクライアントの設定
const api = {
  get: async (endpoint: string) => {
    const { username, sessionToken } = getSessionInfo()
    const response = await fetch(buildApiUrl(endpoint), {
      headers: {
        'X-Username': username,
        'X-Session-Token': sessionToken,
      },
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  post: async (endpoint: string, data: any) => {
    const { username, sessionToken } = getSessionInfo()
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Username': username,
        'X-Session-Token': sessionToken,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  put: async (endpoint: string, data: any) => {
    const { username, sessionToken } = getSessionInfo()
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Username': username,
        'X-Session-Token': sessionToken,
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  },
  delete: async (endpoint: string) => {
    const { username, sessionToken } = getSessionInfo()
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'DELETE',
      headers: {
        'X-Username': username,
        'X-Session-Token': sessionToken,
      },
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return response.json()
  }
}

// アカウント管理用のAPI
export const getAccounts = () => api.get('/accounts')
export const getAccount = (id: number) => api.get(`/accounts/${id}`)
export const createAccount = (data: any) => api.post('/accounts', data)
export const updateAccount = (id: number, data: any) => api.put(`/accounts/${id}`, data)
export const deleteAccount = (id: number) => api.delete(`/accounts/${id}`)

// ログイン用のAPI
export const requestRandomNumber = (data: any) => api.post('/login/request-random', data)
export const verifyLogin = (data: any) => api.post('/login/verify', data)

// 予算管理用のAPI
export const getBudgets = (year: number, month: number) => api.get(`/budgets/${year}/${month}`)
export const getBudgetSummaries = (year: number, month: number) => api.get(`/budgets/${year}/${month}/summary`)
export const createBudget = (data: any) => api.post('/budgets', data)
export const updateBudget = (id: number, data: any) => api.put(`/budgets/${id}`, data)
export const deleteBudget = (id: number) => api.delete(`/budgets/${id}`)
export const moveBudgetUp = (id: number) => api.post(`/budgets/${id}/move-up`, {})
export const moveBudgetDown = (id: number) => api.post(`/budgets/${id}/move-down`, {})
export const copyBudgets = (sourceYear: number, sourceMonth: number, targetYear: number, targetMonth: number) => 
  api.post(`/budgets/copy?source_year=${sourceYear}&source_month=${sourceMonth}&target_year=${targetYear}&target_month=${targetMonth}`, {})

// 取引管理用のAPI
export const getTransactions = (skip: number = 0, limit: number = 100) => api.get(`/transactions?skip=${skip}&limit=${limit}`)
export const createTransaction = (data: any) => api.post('/transactions', data)
export const updateTransaction = (id: number, data: any) => api.put(`/transactions/${id}`, data)
export const deleteTransaction = (id: number) => api.delete(`/transactions/${id}`)
export const getPaymentSources = () => api.get('/payment_sources')
export const createPaymentSource = (data: any) => api.post('/payment_sources', data)
export const updatePaymentSource = (id: number, data: any) => api.put(`/payment_sources/${id}`, data)
export const deletePaymentSource = (id: number) => api.delete(`/payment_sources/${id}`)
export const getDebitSummary = () => api.get('/debit-summary')
export const getPaymentSummary = () => api.get('/payment-summary')
export const calculatePaymentDate = (data: any) => api.post('/calculate-payment-date', data)
export const getBudgetNames = (dateStr: string) => api.get(`/budget-names?date_str=${dateStr}`)

// 商品管理用のAPI
export const getGoods = (skip: number = 0, limit: number = 100) => api.get(`/goods?skip=${skip}&limit=${limit}`)
export const getGoodsWithDetails = (id: number) => api.get(`/goods/${id}/with-details`)
export const createGoods = (data: any) => api.post('/goods', data)
export const updateGoods = (id: number, data: any) => api.put(`/goods/${id}`, data)
export const deleteGoods = (id: number) => api.delete(`/goods/${id}`)
export const getArtists = (skip: number = 0, limit: number = 100) => api.get(`/artists?skip=${skip}&limit=${limit}`)
export const getArtistWithPersons = (id: number) => api.get(`/artists/${id}/with-persons`)
export const createArtist = (data: any) => api.post('/artists', data)
export const updateArtist = (id: number, data: any) => api.put(`/artists/${id}`, data)
export const deleteArtist = (id: number) => api.delete(`/artists/${id}`)
export const getPersons = (skip: number = 0, limit: number = 100) => api.get(`/persons?skip=${skip}&limit=${limit}`)
export const createPerson = (data: any) => api.post('/persons', data)
export const updatePerson = (id: number, data: any) => api.put(`/persons/${id}`, data)
export const deletePerson = (id: number) => api.delete(`/persons/${id}`)
export const getMedia = (skip: number = 0, limit: number = 100) => api.get(`/media?skip=${skip}&limit=${limit}`)
export const createMedia = (data: any) => api.post('/media', data)
export const updateMedia = (id: number, data: any) => api.put(`/media/${id}`, data)
export const deleteMedia = (id: number) => api.delete(`/media/${id}`)

// 休日管理用のAPI
export const getHolidays = () => api.get('/holidays')
export const getHolidaysByMonth = (year: number, month: number) => api.get(`/holidays/month/${year}/${month}`)
export const createHoliday = (data: any) => api.post('/holidays', data)
export const updateHoliday = (id: number, data: any) => api.put(`/holidays/${id}`, data)
export const deleteHoliday = (id: number) => api.delete(`/holidays/${id}`)

// ナレッジ管理用のAPI
export const getKnowhows = (skip: number = 0, limit: number = 100) => api.get(`/knowhows?skip=${skip}&limit=${limit}`)
export const getKnowhowTree = () => api.get('/knowhows/tree')
export const getKnowhow = (id: number) => api.get(`/knowhows/${id}`)
export const createKnowhow = (data: any) => api.post('/knowhows', data)
export const updateKnowhow = (id: number, data: any) => api.put(`/knowhows/${id}`, data)
export const deleteKnowhow = (id: number) => api.delete(`/knowhows/${id}`)
export const moveKnowhowUp = (id: number) => api.post(`/knowhows/${id}/move-up`, {})
export const moveKnowhowDown = (id: number) => api.post(`/knowhows/${id}/move-down`, {})
export const getMajorCategories = (skip: number = 0, limit: number = 100) => api.get(`/major-categories?skip=${skip}&limit=${limit}`)
export const createMajorCategory = (data: any) => api.post('/major-categories', data)
export const updateMajorCategory = (id: number, data: any) => api.put(`/major-categories/${id}`, data)
export const deleteMajorCategory = (id: number) => api.delete(`/major-categories/${id}`)
export const getMiddleCategories = (skip: number = 0, limit: number = 100) => api.get(`/middle-categories?skip=${skip}&limit=${limit}`)
export const createMiddleCategory = (data: any) => api.post('/middle-categories', data)
export const updateMiddleCategory = (id: number, data: any) => api.put(`/middle-categories/${id}`, data)
export const deleteMiddleCategory = (id: number) => api.delete(`/middle-categories/${id}`)

// スケジュール管理用のAPI
export const getSchedules = (skip: number = 0, limit: number = 100) => api.get(`/schedules?skip=${skip}&limit=${limit}`)
export const getSchedulesByMonth = (year: number, month: number) => api.get(`/schedules/month/${year}/${month}`)
export const getSchedulesByWeek = (startDate: string) => api.get(`/schedules/week/${startDate}`)
export const getSchedulesByActivityCategories = (year: number, month: number, categoryIds: string) => 
  api.get(`/schedules/filtered/${year}/${month}?category_ids=${categoryIds}`)
export const createSchedule = (data: any) => api.post('/schedules', data)
export const updateSchedule = (id: number, data: any) => api.put(`/schedules/${id}`, data)
export const deleteSchedule = (id: number) => api.delete(`/schedules/${id}`)
export const getActivityCategories = (skip: number = 0, limit: number = 100) => api.get(`/activity-categories?skip=${skip}&limit=${limit}`)
export const createActivityCategory = (data: any) => api.post('/activity-categories', data)
export const updateActivityCategory = (id: number, data: any) => api.put(`/activity-categories/${id}`, data)
export const deleteActivityCategory = (id: number) => api.delete(`/activity-categories/${id}`) 