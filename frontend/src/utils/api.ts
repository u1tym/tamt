// APIエンドポイントのベースURLを動的に取得
export const getApiBaseUrl = (): string => {
  // 開発環境では現在のホストを使用
  if (import.meta.env.DEV) {
    const currentHost = window.location.hostname
    const currentPort = window.location.port
    const currentProtocol = window.location.protocol
    
    // フロントエンドがHTTPSの場合、バックエンドもHTTPS
    if (currentProtocol === 'https:') {
      if (currentPort === '5173') {
        return `https://${currentHost}:8001`
      }
      return `https://${currentHost}:8001`
    }
    
    // フロントエンドが5173ポートの場合、バックエンドは8000ポート
    if (currentPort === '5173') {
      return `http://${currentHost}:8001`
    }
    return `https://${currentHost}:8001`
    // その他の場合はlocalhost:8001を使用
    // return 'http://localhost:8001'
  }
  // 本番環境では相対パスを使用
  return `https://${window.location.hostname}:8001`
  //return ''
}

// APIエンドポイントを構築するヘルパー関数
export const buildApiUrl = (endpoint: string): string => {
  const baseUrl = getApiBaseUrl()
  return `${baseUrl}${endpoint}`
} 