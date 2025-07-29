<template>
  <div>
    <h2 class="page-title">取引一覧</h2>

    <!-- 支払い額集計表示 -->
    <div v-if="paymentSummary" class="payment-summary">
      <h3 class="summary-title">支払い額集計</h3>
      <div class="summary-grid">
        <div class="summary-card current-month">
          <div class="summary-label">当月</div>
          <div class="summary-period">{{ paymentSummary.current_month?.period }}</div>
          <div class="summary-amount">{{ formatAmount(paymentSummary.current_month?.total_amount || 0) }}円</div>
          <div class="summary-count">({{ paymentSummary.current_month?.transaction_count || 0 }}件)</div>
        </div>
        <div class="summary-card next-month">
          <div class="summary-label">翌月</div>
          <div class="summary-period">{{ paymentSummary.next_month?.period }}</div>
          <div class="summary-amount">{{ formatAmount(paymentSummary.next_month?.total_amount || 0) }}円</div>
          <div class="summary-count">({{ paymentSummary.next_month?.transaction_count || 0 }}件)</div>
        </div>
        <div class="summary-card next-next-month">
          <div class="summary-label">翌々月</div>
          <div class="summary-period">{{ paymentSummary.next_next_month?.period }}</div>
          <div class="summary-amount">{{ formatAmount(paymentSummary.next_next_month?.total_amount || 0) }}円</div>
          <div class="summary-count">({{ paymentSummary.next_next_month?.transaction_count || 0 }}件)</div>
        </div>
      </div>
    </div>

    <!-- 登録ボタン（表の上に移動） -->
    <div class="register-button-container">
      <button
        @click="showDialog = true"
        class="register-button"
      >
        ＋ 新規取引登録
      </button>
    </div>

    <!-- デスクトップ用のテーブル -->
    <table v-if="!isMobile" border="1" cellspacing="0" cellpadding="4" class="transaction-table">
      <thead>
        <tr>
          <th>使用日</th>
          <th style="text-align:center;">用途</th>
          <th style="text-align:center;">メモ</th>
          <th style="text-align:center;">金額</th>
          <th>支出元</th>
          <th>支払日</th>
          <th>予算名称</th>
          <th class="action-header">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="tx in sortedTransactions"
          :key="tx.id"
          class="table-row"
          @mouseenter="hoveredRow = tx.id"
          @mouseleave="hoveredRow = null"
        >
          <td>{{ tx.used_date }}</td>
          <td style="text-align:left;">{{ tx.purpose }}</td>
          <td style="text-align:left;"><span style="white-space: pre-line;">{{ tx.memo }}</span></td>
          <td style="text-align:right;">{{ formatAmount(tx.amount) }}円</td>
          <td>{{ getPaymentSourceName(tx.payment_source_id) }}</td>
          <td>{{ tx.paid_date }}</td>
          <td>{{ tx.budget_name || '未分類' }}</td>
          <td class="action-cell">
            <div v-if="hoveredRow === tx.id" class="action-buttons">
              <button
                @click="editTransaction(tx)"
                class="action-btn edit-btn"
                title="編集"
              >
                ✏️
              </button>
              <button
                @click="deleteTransactionDirect(tx)"
                class="action-btn delete-btn"
                title="削除"
              >
                🗑️
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- スマホ用のカード表示 -->
    <div v-else class="mobile-transactions">
      <div
        v-for="tx in sortedTransactions"
        :key="tx.id"
        class="transaction-card"
        @click="editTransaction(tx)"
      >
        <div class="card-header">
          <span class="date">{{ tx.used_date }}</span>
          <span class="amount">{{ formatAmount(tx.amount) }}円</span>
        </div>
        <div class="card-body">
          <div class="purpose">{{ tx.purpose }}</div>
          <div class="budget-name">予算: {{ tx.budget_name || '未分類' }}</div>
        </div>
        </div>
        </div>

    <!-- 全画面モーダルダイアログ（新規登録・編集共通） -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '取引編集' : '新規取引登録' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updateTransaction() : addTransaction()" class="modal-form">
          <div class="form-group">
            <label for="used_date">使用日 *</label>
            <input
              id="used_date"
              type="date"
              v-model="form.used_date"
              required
              class="form-input"
              @change="fetchPaymentDate"
            />
          </div>

          <div class="form-group">
            <label for="purpose">用途:</label>
            <div class="input-with-camera">
              <input
                id="purpose"
                v-model="form.purpose"
                type="text"
                required
                class="form-input"
                placeholder="例: 食費、交通費、雑費など"
              />
              <button
                v-if="!isEditing && isMobile && cameraSupported"
                type="button"
                @click="openCamera"
                class="camera-button"
                title="レシート撮影"
              >
                📷
              </button>
              <button
                v-if="!isEditing && isMobile && !cameraSupported"
                type="button"
                @click="showManualInputHelp"
                class="help-button"
                title="手動入力のヒント"
              >
                💡
              </button>
            </div>
            <div v-if="isMobile" class="camera-note">
              <small v-if="cameraSupported">📱 iOSの場合はSafariブラウザをご利用ください</small>
              <small v-else>📱 カメラ機能が利用できません。手動で入力してください</small>
              <button
                v-if="!cameraSupported"
                @click="forceEnableCamera"
                class="force-camera-btn"
              >
                カメラ機能を強制有効化
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="memo">メモ</label>
            <textarea
              id="memo"
              v-model="form.memo"
              rows="3"
              class="form-textarea"
              placeholder="詳細なメモがあれば入力してください"
            ></textarea>
          </div>

          <div class="form-group">
            <label for="amount">金額 *</label>
            <input
              id="amount"
              type="number"
              v-model.number="form.amount"
              required
              class="form-input"
              placeholder="0"
              min="0"
            />
          </div>

          <div class="form-group">
            <label for="payment_source">支出元 *</label>
            <select
              id="payment_source"
              v-model.number="form.payment_source_id"
              required
              class="form-select"
              @change="fetchPaymentDate"
            >
              <option value="">選択してください</option>
              <option v-for="source in paymentSources" :key="source.id" :value="source.id">
                {{ source.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="paid_date">支払日</label>
            <div class="payment-date-display">
              <span v-if="form.paid_date" class="payment-date-text">{{ form.paid_date }}</span>
              <span v-else class="payment-date-placeholder">使用日と支出元を選択すると自動計算されます</span>
            </div>
          </div>

          <div class="form-group">
            <label for="budget_name">予算名称</label>
            <select id="budget_name" v-model="form.budget_name" class="form-select">
              <option v-for="name in budgetNameOptions" :key="name" :value="name">{{ name }}</option>
            </select>
          </div>

          <div class="form-actions">
            <button
              type="button"
              @click="closeDialog"
              class="btn btn-secondary"
            >
              キャンセル
            </button>
            <button
              v-if="isEditing"
              type="button"
              @click="deleteTransaction"
              class="btn btn-danger"
              :disabled="isSubmitting"
            >
              削除
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? (isEditing ? '更新中...' : '登録中...') : (isEditing ? '更新' : '登録') }}
            </button>
        </div>
      </form>
      </div>
    </div>

    <!-- カメラモーダル -->
    <div v-if="showCamera" class="modal-overlay" @click="closeCamera">
      <div class="camera-modal" @click.stop>
        <div class="camera-header">
          <h3>レシート撮影</h3>
          <button class="close-button" @click="closeCamera">&times;</button>
        </div>

        <div class="camera-content">
          <!-- デバッグ情報表示 -->
          <div v-if="cameraDebugInfo" class="debug-info">
            <h4>デバッグ情報</h4>
            <pre>{{ cameraDebugInfo }}</pre>
            <button @click="cameraDebugInfo = ''" class="debug-close-btn">閉じる</button>
          </div>

          <div class="camera-preview">
            <video
              v-if="!capturedImage"
              ref="videoElement"
              autoplay
              playsinline
              muted
              class="camera-video"
            ></video>
            <canvas
              ref="canvasElement"
              class="camera-canvas"
              style="display: none;"
            ></canvas>
            <div v-if="capturedImage" class="captured-image">
              <img :src="capturedImage" alt="撮影画像" @load="onImageLoad" @error="onImageError" />
              <div class="image-debug">
                <p>画像サイズ: {{ capturedImage.length }} バイト</p>
                <p>画像URL: {{ capturedImage.substring(0, 50) }}...</p>
              </div>
            </div>
            <div v-if="!cameraReady && !capturedImage" class="camera-loading">
              <div class="loading-spinner"></div>
              <p>カメラを起動中...</p>
              <p v-if="cameraStatus" class="camera-status">{{ cameraStatus }}</p>
              <button @click="showDebugInfo" class="debug-btn">デバッグ情報</button>
            </div>
          </div>

          <div class="camera-controls">
            <button
              v-if="!capturedImage"
              @click="captureImage"
              class="capture-btn"
              :disabled="!cameraReady"
            >
              📸 撮影
            </button>
            <button
              v-if="capturedImage"
              @click="retakePhoto"
              class="retake-btn"
            >
              🔄 再撮影
            </button>
            <button
              v-if="capturedImage"
              @click="analyzeReceipt"
              class="analyze-btn"
              :disabled="isAnalyzing"
            >
              {{ isAnalyzing ? '解析中...' : '🔍 レシート解析' }}
            </button>
          </div>

          <!-- 解析結果表示 -->
          <div v-if="ocrResult" class="ocr-result">
            <h4>解析結果</h4>
            <div class="ocr-result-content">
              <div class="ocr-item">
                <label>使用日:</label>
                <span>{{ ocrResult.used_date || '未検出' }}</span>
              </div>
              <div class="ocr-item">
                <label>用途:</label>
                <span>{{ ocrResult.purpose || '未検出' }}</span>
              </div>
              <div class="ocr-item">
                <label>金額:</label>
                <span>{{ ocrResult.amount ? `¥${ocrResult.amount.toLocaleString()}` : '未検出' }}</span>
              </div>
              <div class="ocr-item">
                <label>信頼度:</label>
                <span>{{ Math.round(ocrResult.confidence * 100) }}%</span>
              </div>
              <div v-if="ocrResult.note" class="ocr-note">
                <label>メモ:</label>
                <span>{{ ocrResult.note }}</span>
              </div>
            </div>
            <div class="ocr-actions">
              <button @click="applyOcrResult" class="apply-btn">
                ✅ 結果を適用
              </button>
              <button @click="ocrResult = null" class="btn btn-secondary">
                ❌ 結果を破棄
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { buildApiUrl } from '../utils/api'

interface Transaction {
  id: number
  used_date: string
  purpose: string
  memo: string
  amount: number
  payment_source_id: number
  paid_date: string
  created_at: string
  updated_at: string
  budget_name?: string
}

interface PaymentSource {
  id: number
  name: string
}

interface PaymentSummary {
  current_month?: {
    period: string
    start_date: string
    end_date: string
    total_amount: number
    transaction_count: number
  }
  next_month?: {
    period: string
    start_date: string
    end_date: string
    total_amount: number
    transaction_count: number
  }
  next_next_month?: {
    period: string
    start_date: string
    end_date: string
    total_amount: number
    transaction_count: number
  }
}

interface OcrResult {
  used_date: string | null
  purpose: string | null
  amount: number | null
  raw_text: string
  confidence: number
  note?: string
}

const transactions = ref<Transaction[]>([])
const paymentSources = ref<PaymentSource[]>([])
const paymentSummary = ref<PaymentSummary | null>(null)
const error = ref('')
const isSubmitting = ref(false)
const isMobile = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const hoveredRow = ref<number | null>(null)

// カメラ関連
const showCamera = ref(false)
const cameraReady = ref(false)
const capturedImage = ref<string | null>(null)
const isAnalyzing = ref(false)
const ocrResult = ref<OcrResult | null>(null)
const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
const cameraDebugInfo = ref('')
const cameraStatus = ref('')
const cameraSupported = ref(false)
let stream: MediaStream | null = null

const form = ref({
  used_date: '',
  purpose: '',
  memo: '',
  amount: 0,
  payment_source_id: 0,
  paid_date: '',
  budget_name: '未分類',
})

const budgetNameOptions = ref<string[]>(['未分類'])

const showDialog = ref(false)

// スマホ判定
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

// データ取得
const fetchPaymentSources = async () => {
  try {
    console.log('支払い元データ取得開始')
    const response = await fetch(buildApiUrl('/payment_sources'))
    console.log('支払い元データ取得レスポンス:', response.status, response.statusText)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log('支払い元データ取得成功:', data)
    paymentSources.value = data

    // 支払い元が存在する場合、最初のものを選択
    if (paymentSources.value.length > 0 && form.value.payment_source_id === 0) {
      form.value.payment_source_id = paymentSources.value[0].id
    }
  } catch (e: any) {
    console.error('支払い元データ取得エラー:', e)
    error.value = `支払い元データの取得に失敗しました: ${e.message}`
  }
}

const fetchTransactions = async () => {
  try {
    console.log('取引データ取得開始')
    const apiUrl = buildApiUrl('/transactions')
    console.log('API URL:', apiUrl)
    console.log('現在のプロトコル:', window.location.protocol)
    console.log('現在のホスト:', window.location.host)

    const response = await fetch(apiUrl)
    console.log('取引データ取得レスポンス:', response.status, response.statusText)
    console.log('レスポンスヘッダー:', Object.fromEntries(response.headers.entries()))

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log('取引データ取得成功:', data)
    console.log('データ件数:', data.length)
    transactions.value = data
  } catch (e: any) {
    console.error('取引データ取得エラー:', e)
    console.error('エラータイプ:', e.constructor.name)
    console.error('エラーメッセージ:', e.message)
    error.value = `取引データの取得に失敗しました: ${e.message}`

    // より詳細なエラー情報を追加
    if (e.name === 'TypeError' && e.message.includes('Failed to fetch')) {
      error.value += '\n\nネットワークエラーの可能性があります：\n1. バックエンドサーバーが起動しているか確認\n2. HTTPS証明書が信頼されているか確認\n3. ネットワーク接続を確認\n4. ファイアウォールの設定を確認'
    }

    // HTTPS関連のエラー
    if (window.location.protocol === 'https:') {
      error.value += '\n\nHTTPS環境での問題の可能性：\n1. スマホの設定 > 一般 > VPNとデバイス管理 > 証明書で信頼設定\n2. Safariで「詳細設定」→「安全でないサイトにアクセス」を選択'
    }
  }
}

const fetchPaymentSummary = async () => {
  try {
    console.log('支払い額集計取得開始')
    const apiUrl = buildApiUrl('/payment-summary')
    console.log('支払い額集計API URL:', apiUrl)

    const response = await fetch(apiUrl)
    console.log('支払い額集計取得レスポンス:', response.status, response.statusText)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log('支払い額集計取得成功:', data)
    paymentSummary.value = data
  } catch (e: any) {
    console.error('支払い額集計取得エラー:', e)
    // エラーが発生しても取引一覧の表示は継続するため、エラーはログのみ
  }
}

const getPaymentSourceName = (id: number) => {
  const source = paymentSources.value.find(s => s.id === id)
  return source ? source.name : `ID:${id}`
}

const formatAmount = (amount: number) => {
  return amount.toLocaleString()
}

const fetchPaymentDate = async () => {
  // 使用日と支出元が両方選択されている場合のみ支払日を取得
  if (!form.value.used_date || !form.value.payment_source_id) {
    form.value.paid_date = ''
    return
  }

  try {
    const response = await fetch(buildApiUrl('/calculate-payment-date'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        used_date: form.value.used_date,
        payment_source_id: form.value.payment_source_id,
      }),
    })

    if (!response.ok) {
      throw new Error('支払日の計算に失敗しました')
    }

    const data = await response.json()
    form.value.paid_date = data.paid_date
  } catch (e: any) {
    console.error('支払日取得エラー:', e)
    form.value.paid_date = ''
  }
}

const resetForm = () => {
  form.value = {
    used_date: '',
    purpose: '',
    memo: '',
    amount: 0,
    payment_source_id: paymentSources.value[0]?.id || 0,
    paid_date: '',
    budget_name: '未分類',
  }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
  error.value = ''
}

const editTransaction = (transaction: Transaction) => {
  isEditing.value = true
  editingId.value = transaction.id
  form.value = {
    used_date: transaction.used_date,
    purpose: transaction.purpose,
    memo: transaction.memo || '',
    amount: transaction.amount,
    payment_source_id: transaction.payment_source_id,
    paid_date: transaction.paid_date || '',
    budget_name: transaction.budget_name || '未分類',
  }
  showDialog.value = true
}

const deleteTransactionDirect = async (transaction: Transaction) => {
  if (!confirm(`「${transaction.purpose}」を削除しますか？`)) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/transactions/${transaction.id}`), {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('削除に失敗しました')

    await fetchTransactions()
    await fetchPaymentSummary()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const addTransaction = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl('/transactions'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('登録に失敗しました')

    // 成功時の処理
    closeDialog()
    await fetchTransactions()
    await fetchPaymentSummary()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateTransaction = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/transactions/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('更新に失敗しました')

    // 成功時の処理
    closeDialog()
    await fetchTransactions()
    await fetchPaymentSummary()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const deleteTransaction = async () => {
  if (!editingId.value) return

  if (!confirm('この取引を削除しますか？')) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/transactions/${editingId.value}`), {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('削除に失敗しました')

    // 成功時の処理
    closeDialog()
    await fetchTransactions()
    await fetchPaymentSummary()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// カメラ機能
const openCamera = async () => {
  console.log('カメラ起動開始')
  console.log('isMobile:', isMobile.value)
  console.log('isEditing:', isEditing.value)

  if (!isMobile.value || isEditing.value) {
    console.log('モバイルでないか、編集中のためカメラを起動しません')
    return
  }

  // まずモーダルを表示
  showCamera.value = true
  capturedImage.value = null
  ocrResult.value = null
  error.value = ''

  // 少し待ってからカメラを初期化（DOMの準備を待つ）
  await new Promise(resolve => setTimeout(resolve, 100))

  try {
    console.log('カメラAPIサポート確認中...')

    // ブラウザ検出
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
    const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)
    const isIOSSafari = isIOS && isSafari
    const isIOSChrome = isIOS && /Chrome/.test(navigator.userAgent)

    console.log('ブラウザ情報:', { isIOS, isSafari, isIOSSafari, isIOSChrome })

    if (isIOSChrome) {
      error.value = 'お使いのブラウザはカメラ機能をサポートしていません。iOSの場合はSafariブラウザをご利用ください。'
      return
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      error.value = 'お使いのブラウザはカメラ機能をサポートしていません。iOSの場合はSafariブラウザをご利用ください。'
      return
    }

    console.log('カメラ権限確認中...')

    // Safari用の特別な処理
    if (isIOSSafari) {
      console.log('iOS Safari用のカメラ初期化')

      // 基本的な制約でカメラを取得
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // 背面カメラ
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })

      console.log('iOS Safari カメラストリーム取得完了')

      if (videoElement.value) {
        videoElement.value.srcObject = stream

        // Safari用のイベントリスナー
        videoElement.value.onloadedmetadata = () => {
          console.log('iOS Safari: onloadedmetadata')
          console.log('ビデオサイズ:', videoElement.value?.videoWidth, 'x', videoElement.value?.videoHeight)
          videoElement.value?.play()
        }

        videoElement.value.oncanplay = () => {
          console.log('iOS Safari: oncanplay')
          console.log('ビデオ再生可能, サイズ:', videoElement.value?.videoWidth, 'x', videoElement.value?.videoHeight)
          cameraReady.value = true
        }

        videoElement.value.onplay = () => {
          console.log('iOS Safari: onplay')
        }

        videoElement.value.onerror = (e) => {
          console.error('iOS Safari ビデオエラー:', e)
        }

        // 手動で再生を試行
        try {
          await videoElement.value.play()
          console.log('iOS Safari: 手動再生成功')
        } catch (iosError) {
          console.error('iOS Safari: 手動再生エラー:', iosError)
        }
      }
    } else {
      console.log('通常のカメラ初期化')

      // 通常のカメラ初期化
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })

      console.log('通常カメラストリーム取得完了')

      if (videoElement.value) {
        videoElement.value.srcObject = stream

        // ビデオ要素の準備を待つ
        videoElement.value.onloadedmetadata = () => {
          console.log('通常: onloadedmetadata')
          console.log('ビデオサイズ:', videoElement.value?.videoWidth, 'x', videoElement.value?.videoHeight)
          videoElement.value?.play()
        }

        videoElement.value.oncanplay = () => {
          console.log('通常: oncanplay')
          console.log('ビデオ再生可能, サイズ:', videoElement.value?.videoWidth, 'x', videoElement.value?.videoHeight)
          cameraReady.value = true
        }

        videoElement.value.onplay = () => {
          console.log('通常: onplay')
        }

        videoElement.value.onerror = (e) => {
          console.error('ビデオエラー:', e)
        }
      }
    }

    console.log('カメラ起動完了')

  } catch (error: any) {
    console.error('カメラ起動エラー:', error)
    error.value = `カメラの起動に失敗しました: ${error.message}`

    // Safari用の権限チェック
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
    const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)
    const isIOSSafari = isIOS && isSafari

    if (isIOSSafari) {
      try {
        await navigator.mediaDevices.getUserMedia({ video: true })
        console.log('Safari権限チェック成功')
      } catch (permError) {
        console.error('Safari権限エラー:', permError)
        error.value = 'カメラ権限が許可されていません。Safariの設定でカメラを許可してください。'
      }
    }
  }
}

const closeCamera = () => {
  showCamera.value = false
  cameraReady.value = false
  capturedImage.value = null
  ocrResult.value = null

  // カメラストリームを停止
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }

  // ビデオ要素をクリア
  if (videoElement.value) {
    videoElement.value.srcObject = null
  }
}

const captureImage = () => {
  console.log('撮影開始')
  console.log('videoElement:', videoElement.value)
  console.log('canvasElement:', canvasElement.value)

  if (!videoElement.value || !canvasElement.value) {
    console.error('ビデオまたはキャンバス要素が見つかりません')
    return
  }

  const video = videoElement.value
  const canvas = canvasElement.value
  const context = canvas.getContext('2d')

  if (!context) {
    console.error('キャンバスコンテキストが取得できません')
    return
  }

  console.log('ビデオサイズ:', video.videoWidth, 'x', video.videoHeight)
  console.log('ビデオ準備状態:', video.readyState)
  console.log('ビデオ再生状態:', !video.paused)
  console.log('ビデオの現在時刻:', video.currentTime)

  // ビデオが準備できていない場合は待機
  if (video.readyState < 2) {
    console.log('ビデオが準備できていません。待機します...')
    video.addEventListener('loadeddata', () => {
      console.log('ビデオデータ読み込み完了')
      captureImage()
    })
    return
  }

  // ビデオサイズが0の場合は待機
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    console.log('ビデオサイズが0です。待機します...')
    setTimeout(() => {
      console.log('再試行: ビデオサイズ:', video.videoWidth, 'x', video.videoHeight)
      captureImage()
    }, 500)
    return
  }

  // キャンバスサイズをビデオサイズに設定
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  console.log('キャンバスサイズ設定:', canvas.width, 'x', canvas.height)

  try {
    // ビデオフレームをキャンバスに描画
    context.drawImage(video, 0, 0, canvas.width, canvas.height)
    console.log('画像描画完了')

    // キャンバスから画像データを取得
    const imageData = canvas.toDataURL('image/jpeg', 0.8)
    console.log('画像データURL生成完了, サイズ:', imageData.length)

    // 画像データが有効かチェック（黒い画像でないか）
    if (imageData.length < 1000) {
      console.error('生成された画像データが小さすぎます')
      error.value = '画像の取得に失敗しました。もう一度お試しください。'
      return
    }

    // 画像データの内容を確認
    console.log('画像データの先頭部分:', imageData.substring(0, 100))

    // 画像データを直接設定（テストは後で行う）
    capturedImage.value = imageData
    console.log('撮影完了 - 画像データ設定済み')

    // 撮影後にカメラを停止
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      console.log('カメラストリーム停止')
    }

    // カメラ状態を更新
    cameraReady.value = false

    // 画像が実際に表示可能かテスト（非同期）
    const testImg = new Image()
    testImg.onload = () => {
      console.log('テスト画像読み込み成功, サイズ:', testImg.naturalWidth, 'x', testImg.naturalHeight)
    }
    testImg.onerror = () => {
      console.error('テスト画像読み込み失敗')
      error.value = '画像データの生成に失敗しました'
    }
    testImg.src = imageData

  } catch (error: any) {
    console.error('撮影エラー:', error)
    error.value = `撮影に失敗しました: ${error.message}`
  }
}

const retakePhoto = () => {
  capturedImage.value = null
  ocrResult.value = null

  // 再撮影時にカメラを再起動
  cameraReady.value = false
  openCamera()
}

// 画像読み込みイベントハンドラー
const onImageLoad = (event: Event) => {
  console.log('画像読み込み成功:', event)
  const img = event.target as HTMLImageElement
  console.log('画像の実際のサイズ:', img.naturalWidth, 'x', img.naturalHeight)
}

const onImageError = (event: Event) => {
  console.error('画像読み込みエラー:', event)
  error.value = '画像の表示に失敗しました'
}

// レシート解析関数
const parseReceipt = async (imageBlob: Blob) => {
  try {
    console.log('レシート解析開始')

    // FormDataを作成
    const formData = new FormData()
    formData.append('file', imageBlob, 'receipt.jpg')

    // APIに送信
    const apiUrl = buildApiUrl('/parse-receipt')
    console.log('レシート解析API URL:', apiUrl)

    const response = await fetch(apiUrl, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    console.log('OCR解析結果:', result)

    // 解析結果をocrResultに保存
    ocrResult.value = result

    // デバッグ用に生テキストも表示（開発環境のみ）
    if (import.meta.env.DEV && result.raw_text) {
      console.log('OCR生テキスト:', result.raw_text)
    }

    return result

  } catch (error: any) {
    console.error('レシート解析エラー:', error)
    alert(`レシート解析に失敗しました: ${error.message}`)
    throw error
  }
}

const analyzeReceipt = async () => {
  if (!capturedImage.value) {
    alert('先にレシートを撮影してください')
    return
  }

  isAnalyzing.value = true
  error.value = ''

  try {
    // 画像をBlobに変換
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      throw new Error('Canvas context not available')
    }

    // 画像要素を作成してサイズを取得
    const img = new Image()
    img.src = capturedImage.value
    await new Promise((resolve) => {
      img.onload = resolve
    })

    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)

    // Blobに変換して解析を実行
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((blob) => {
        if (blob) {
          resolve(blob)
        } else {
          reject(new Error('Failed to create blob from canvas'))
        }
      }, 'image/jpeg', 0.8)
    })

    // レシート解析を実行
    const result = await parseReceipt(blob)
    console.log('解析完了:', result)

  } catch (e: any) {
    console.error('レシート解析エラー:', e)
    error.value = 'レシート解析に失敗しました: ' + e.message
  } finally {
    isAnalyzing.value = false
  }
}

const applyOcrResult = () => {
  if (!ocrResult.value) return

  form.value.purpose = ocrResult.value.purpose || ''
  form.value.amount = ocrResult.value.amount || 0
  form.value.used_date = ocrResult.value.used_date || ''

  closeCamera()
}

const showManualInputHelp = () => {
  const helpText = `カメラ機能が利用できない場合の代替案：

1. 手動入力
   - 使用日: 2023-10-27
   - 用途: 食費
   - 金額: 1,200円
   - メモ: コンビニでの買い物

2. 別のブラウザでカメラ機能をテスト：
   - Chrome: http://[PCのIPアドレス]:5173
   - Firefox: http://[PCのIPアドレス]:5173
   - これらのブラウザではHTTP環境でもカメラ機能が利用可能

3. Safariでカメラ機能を使用する場合：
   - HTTPS環境が必要（本番環境でのみ利用可能）
   - 設定 > Safari > カメラで許可

現在の環境: ${window.location.protocol}${window.location.host}`

  alert(helpText)
}

const showDebugInfo = () => {
  const oldGetUserMedia = (navigator as any).getUserMedia ||
                         (navigator as any).webkitGetUserMedia ||
                         (navigator as any).mozGetUserMedia ||
                         (navigator as any).msGetUserMedia

  const debugInfo = {
    isMobile: isMobile.value,
    cameraReady: cameraReady.value,
    showCamera: showCamera.value,
    stream: stream ? 'Active' : 'None',
    videoElement: videoElement.value ? 'Found' : 'Not found',
    videoReadyState: videoElement.value?.readyState || 'N/A',
    videoWidth: videoElement.value?.videoWidth || 'N/A',
    videoHeight: videoElement.value?.videoHeight || 'N/A',
    error: error.value || 'None',
    userAgent: navigator.userAgent,
    isIOS: /iPad|iPhone|iPod/.test(navigator.userAgent),
    isSafari: /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent),
    mediaDevices: !!navigator.mediaDevices,
    getUserMedia: !!navigator.mediaDevices?.getUserMedia,
    oldGetUserMedia: !!oldGetUserMedia,
    permissions: !!navigator.permissions,
    currentUrl: window.location.href,
    protocol: window.location.protocol,
    host: window.location.host,
    cameraSupported: cameraSupported.value,
    timestamp: new Date().toISOString(),
    // ネットワーク情報
    connection: (navigator as any).connection ? {
      effectiveType: (navigator as any).connection.effectiveType,
      downlink: (navigator as any).connection.downlink,
      rtt: (navigator as any).connection.rtt
    } : 'Not supported',
    // 画面情報
    screen: {
      width: window.screen.width,
      height: window.screen.height,
      availWidth: window.screen.availWidth,
      availHeight: window.screen.availHeight
    },
    // ウィンドウ情報
    window: {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      outerWidth: window.outerWidth,
      outerHeight: window.outerHeight
    }
  }

  cameraDebugInfo.value = JSON.stringify(debugInfo, null, 2)
}

// カメラサポートの検出
const checkCameraSupport = () => {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
  const isSafari = /Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)
  const isIOSSafari = isIOS && isSafari

  // 基本的なカメラAPIのサポートチェック
  const hasMediaDevices = !!navigator.mediaDevices
  const hasGetUserMedia = !!navigator.mediaDevices?.getUserMedia

  // 古いAPIのサポートチェック
  const oldGetUserMedia = (navigator as any).getUserMedia ||
                         (navigator as any).webkitGetUserMedia ||
                         (navigator as any).mozGetUserMedia ||
                         (navigator as any).msGetUserMedia

  // HTTPS環境のチェック
  const isHTTPS = window.location.protocol === 'https:'

  // スマホのSafariでは、HTTP環境でもカメラ機能を試す
  if (isIOSSafari) {
    console.log('スマホSafari: カメラ機能を試してみます')
    // スマホSafariでは強制的に有効化を試す
    cameraSupported.value = true
    return
  }

  // カメラAPIが利用可能かチェック
  cameraSupported.value = hasMediaDevices || !!oldGetUserMedia

  console.log('カメラサポート検出:', {
    isIOS,
    isSafari,
    isIOSSafari,
    hasMediaDevices,
    hasGetUserMedia,
    oldGetUserMedia: !!oldGetUserMedia,
    isHTTPS,
    cameraSupported: cameraSupported.value
  })
}

const forceEnableCamera = () => {
  console.log('カメラ機能を強制有効化をクリックしました')
  // ブラウザの設定を開く
  const url = `https://${window.location.host}/settings/camera`
  window.open(url, '_blank')
}

// 支払日が確定したら予算名称一覧を取得
const fetchBudgetNames = async () => {
  if (!form.value.paid_date) {
    budgetNameOptions.value = ['未分類']
    form.value.budget_name = '未分類'
    return
  }
  const paid = new Date(form.value.paid_date)
  const year = paid.getFullYear()
  const month = paid.getMonth() + 1
  try {
    const res = await fetch(buildApiUrl(`/budget-names?year=${year}&month=${month}`))
    if (!res.ok) throw new Error('予算名称取得に失敗')
    const data = await res.json()
    budgetNameOptions.value = ['未分類', ...(data.names || [])]
    if (!budgetNameOptions.value.includes(form.value.budget_name)) {
      form.value.budget_name = '未分類'
    }
  } catch {
    budgetNameOptions.value = ['未分類']
    form.value.budget_name = '未分類'
  }
}

// 支払日が確定したら呼ぶ
watch(() => form.value.paid_date, fetchBudgetNames)

const sortedTransactions = computed(() => {
  return [...transactions.value].sort((a, b) => {
    if (a.used_date > b.used_date) return -1
    if (a.used_date < b.used_date) return 1
    // used_dateが同じ場合はcreated_atの降順
    if (a.created_at > b.created_at) return -1
    if (a.created_at < b.created_at) return 1
    return 0
  })
})

// コンポーネントマウント時にカメラサポートをチェック
onMounted(() => {
  checkCameraSupport()
  checkMobile()
  window.addEventListener('resize', checkMobile)
  fetchPaymentSources()
  fetchTransactions()
  fetchPaymentSummary()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
})
</script>

<style scoped>
.page-title {
  text-align: center;
  margin: 16px 0 24px 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.transaction-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}

.transaction-table th,
.transaction-table td {
  padding: 12px 8px;
  border: 1px solid #ddd;
}

.transaction-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.action-header {
  width: 80px;
  text-align: center;
}

.action-cell {
  width: 80px;
  text-align: center;
  padding: 8px 4px !important;
}

.table-row {
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #f8f9fa;
}

.action-buttons {
  display: flex;
  gap: 4px;
  justify-content: center;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 16px;
  transition: all 0.2s;
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-btn:hover {
  background-color: #e3f2fd;
  transform: scale(1.1);
}

.delete-btn:hover {
  background-color: #ffebee;
  transform: scale(1.1);
}

.register-button-container {
  text-align: center;
  margin: 20px 0;
}

.register-button {
  background-color: #4CAF50;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.2s;
}

.register-button:hover {
  background-color: #45a049;
}

/* カメラボタン */
.input-with-camera {
  display: flex;
  align-items: center;
  gap: 8px;
}

.camera-button {
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-button:hover {
  background-color: #0056b3;
}

.help-button {
  padding: 8px 12px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  min-height: 44px;
  min-width: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.help-button:hover {
  background-color: #5a6268;
}

.camera-note {
  margin-top: 4px;
  color: #666;
  font-size: 12px;
}

.camera-note small {
  color: #888;
}

.force-camera-btn {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.force-camera-btn:hover {
  background-color: #f57c00;
}

/* カメラモーダル */
.camera-modal {
  background: white;
  border-radius: 8px;
  width: 95%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.camera-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0 24px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.camera-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.camera-content {
  padding: 0 24px 24px 24px;
}

.camera-preview {
  position: relative;
  width: 100%;
  height: 300px;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.camera-video,
.camera-canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.captured-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 8px;
  position: relative;
}

.captured-image img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border: 2px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-debug {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
}

.image-debug p {
  margin: 2px 0;
}

.camera-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  z-index: 1;
}

.camera-status {
  font-size: 14px;
  margin-top: 8px;
  text-align: center;
  max-width: 90%;
  word-break: break-word;
}

.debug-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.debug-btn:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.debug-info {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.debug-info h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
}

.debug-info pre {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  font-size: 11px;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.debug-close-btn {
  margin-top: 8px;
  padding: 4px 8px;
  background-color: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.debug-close-btn:hover {
  background-color: #555;
}

.loading-spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.camera-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 20px;
}

.capture-btn,
.retake-btn,
.analyze-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.capture-btn {
  background-color: #4CAF50;
  color: white;
}

.capture-btn:hover:not(:disabled) {
  background-color: #45a049;
}

.retake-btn {
  background-color: #ff9800;
  color: white;
}

.retake-btn:hover {
  background-color: #f57c00;
}

.analyze-btn {
  background-color: #2196F3;
  color: white;
}

.analyze-btn:hover:not(:disabled) {
  background-color: #1976D2;
}

.analyze-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.apply-btn {
  padding: 12px 24px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
  flex: 1;
  min-width: 120px;
  max-width: 150px;
}

.apply-btn:hover {
  background-color: #45a049;
}

/* スマホ用のカード表示 */
.mobile-transactions {
  margin-bottom: 24px;
}

.transaction-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.transaction-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.transaction-card:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.date {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.amount {
  font-size: 16px;
  font-weight: bold;
  color: #d32f2f;
}

.card-body {
  margin-top: 8px;
}

.purpose {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  line-height: 1.4;
}

.budget-name {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

/* モーダル関連のスタイル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 0 24px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-button:hover {
  background-color: #f0f0f0;
  color: #333;
}

.modal-form {
  padding: 0 24px 24px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.payment-date-display {
  padding: 12px;
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  min-height: 20px;
  display: flex;
  align-items: center;
}

.payment-date-text {
  color: #2e7d32;
  font-weight: 500;
  font-size: 14px;
}

.payment-date-placeholder {
  color: #6c757d;
  font-style: italic;
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background-color: #e8e8e8;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

.btn-danger:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border: 1px solid #ffcdd2;
}

/* 支払い額集計のスタイル */
.payment-summary {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.summary-card.current-month {
  border-left: 4px solid #4CAF50;
  background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e8 100%);
}

.summary-card.next-month {
  border-left: 4px solid #2196F3;
  background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
}

.summary-card.next-next-month {
  border-left: 4px solid #FF9800;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff3e0 100%);
}

.summary-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-period {
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
  font-weight: 500;
}

.summary-amount {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.summary-count {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .page-title {
    font-size: 1.2rem;
    margin: 12px 0 20px 0;
  }

  .payment-summary {
    padding: 16px;
    margin-bottom: 20px;
  }

  .summary-title {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .summary-card {
    padding: 12px;
  }

  .summary-amount {
    font-size: 20px;
  }

  .modal-content,
  .camera-modal {
    width: 95%;
    margin: 10px;
  }

  .modal-header,
  .modal-form,
  .camera-header,
  .camera-content {
    padding-left: 16px;
    padding-right: 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .register-button {
    width: 100%;
    max-width: 300px;
  }

  .camera-controls {
  flex-direction: column;
}

.capture-btn,
.retake-btn,
.analyze-btn {
  width: 100%;
}

/* OCR解析結果表示 */
.ocr-result {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.ocr-result h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.ocr-result-content {
  margin-bottom: 16px;
}

.ocr-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e9ecef;
}

.ocr-item:last-child {
  border-bottom: none;
}

.ocr-item label {
  font-weight: 500;
  color: #495057;
  min-width: 80px;
}

.ocr-item span {
  color: #333;
  font-weight: 500;
}

.ocr-note {
  margin-top: 8px;
  padding: 8px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
}

.ocr-note label {
  font-weight: 500;
  color: #856404;
  display: block;
  margin-bottom: 4px;
}

.ocr-note span {
  color: #856404;
  font-size: 14px;
}

.ocr-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.ocr-actions .btn {
  flex: 1;
  min-width: 120px;
  max-width: 150px;
}
}
</style>
