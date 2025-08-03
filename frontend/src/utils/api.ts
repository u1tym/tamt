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

// APIクライアントの設定
const api = {
  get: async (endpoint: string) => {
    const response = await fetch(buildApiUrl(endpoint))
    return response.json()
  },
  post: async (endpoint: string, data: any) => {
    const response = await fetch(buildApiUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    return response.json()
  }
}

// アカウント管理用のAPI
export const getAccounts = () => api.get('/accounts')
export const getAccount = (id: number) => api.get(`/accounts/${id}`)
export const createAccount = (data: any) => api.post('/accounts', data)
export const updateAccount = (id: number, data: any) => api.post(`/accounts/${id}`, data)
export const deleteAccount = (id: number) => api.post(`/accounts/${id}/delete`, {})

// ログイン用のAPI
export const requestRandomNumber = (data: any) => api.post('/login/request-random', data)
export const verifyLogin = (data: any) => api.post('/login/verify', data) 