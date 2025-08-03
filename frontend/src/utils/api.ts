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