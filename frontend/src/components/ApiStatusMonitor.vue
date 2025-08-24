<template>
  <div
    class="api-status-monitor"
    v-if="showMonitor"
    :style="{ left: position.x + 'px', top: position.y + 'px' }"
    @mousedown="startDrag"
    ref="monitorRef"
  >
    <div class="monitor-header" @mousedown.stop>
      <h3>API Queue Status</h3>
      <button @click="toggleMonitor" class="close-btn">×</button>
    </div>

    <div class="status-info">
      <div class="status-item">
        <span class="label">Processing:</span>
        <span class="value" :class="{ active: queueStatus.isProcessing }">
          {{ queueStatus.isProcessing ? 'Yes' : 'No' }}
        </span>
      </div>

      <div class="status-item">
        <span class="label">Queue Length:</span>
        <span class="value">{{ queueStatus.queueLength }}</span>
      </div>

      <div class="status-item">
        <span class="label">Total Requests:</span>
        <span class="value">{{ queueStatus.totalRequests }}</span>
      </div>
    </div>

    <div class="progress-section" v-if="progressMonitor">
      <div class="progress-header">
        <span>Progress: {{ progressMonitor.getStatus().progress.toFixed(1) }}%</span>
        <span>{{ progressMonitor.getStatus().completed }}/{{ progressMonitor.getStatus().total }}</span>
      </div>

      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${progressMonitor.getStatus().progress}%` }"
        ></div>
      </div>

      <div class="progress-details">
        <span>Elapsed: {{ (progressMonitor.getStatus().elapsed / 1000).toFixed(1) }}s</span>
        <span v-if="progressMonitor.getStatus().remaining > 0">
          Remaining: {{ (progressMonitor.getStatus().remaining / 1000).toFixed(1) }}s
        </span>
      </div>
    </div>

    <div class="actions">
      <button @click="clearQueue" class="action-btn clear-btn" :disabled="queueStatus.queueLength === 0">
        Clear Queue
      </button>
      <button @click="testBatchCalls" class="action-btn test-btn">
        Test Batch Calls
      </button>
    </div>

    <div class="log-section" v-if="logs.length > 0">
      <h4>Recent Logs</h4>
      <div class="log-container">
        <div
          v-for="(log, index) in logs.slice(-10)"
          :key="index"
          class="log-entry"
          :class="log.level"
        >
          <span class="log-time">{{ formatTime(log.timestamp) }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>

  <button v-else @click="toggleMonitor" class="monitor-toggle-btn">
    API Status
  </button>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  getApiQueueStatus,
  clearApiQueue,
  batchApiCalls,
  createProgressMonitor,
  getAccounts,
  getBudgets,
  getTransactions
} from '../utils/api'

interface QueueStatus {
  isProcessing: boolean
  queueLength: number
  totalRequests: number
}

interface LogEntry {
  timestamp: Date
  level: 'info' | 'warn' | 'error'
  message: string
}

interface Position {
  x: number
  y: number
}

const showMonitor = ref(false)
const queueStatus = ref<QueueStatus>({
  isProcessing: false,
  queueLength: 0,
  totalRequests: 0
})
const progressMonitor = ref<any>(null)
const logs = ref<LogEntry[]>([])
const updateInterval = ref<number | null>(null)
const monitorRef = ref<HTMLElement | null>(null)

// ドラッグ機能の状態管理
const isDragging = ref(false)
const dragOffset = ref<Position>({ x: 0, y: 0 })
const position = ref<Position>({ x: 20, y: 20 })

const toggleMonitor = () => {
  showMonitor.value = !showMonitor.value
  if (showMonitor.value) {
    startMonitoring()
  } else {
    stopMonitoring()
  }
}

const startMonitoring = () => {
  updateStatus()
  updateInterval.value = window.setInterval(updateStatus, 1000)
}

const stopMonitoring = () => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
    updateInterval.value = null
  }
}

const updateStatus = () => {
  queueStatus.value = getApiQueueStatus()
}

const clearQueue = () => {
  clearApiQueue()
  updateStatus()
  addLog('warn', 'Queue cleared manually')
}

const testBatchCalls = async () => {
  const monitor = createProgressMonitor()
  progressMonitor.value = monitor

  const testCalls = [
    () => getAccounts(),
    () => getBudgets(2024, 1),
    () => getTransactions(0, 10),
    () => getAccounts(), // 重複テスト
    () => getBudgets(2024, 2)
  ]

  monitor.start(testCalls.length)
  addLog('info', `Starting batch test with ${testCalls.length} calls`)

  try {
    const results = await batchApiCalls(testCalls, (completed, total) => {
      monitor.increment()
      addLog('info', `Batch progress: ${completed}/${total}`)
    })

    addLog('info', `Batch test completed successfully with ${results.length} results`)
  } catch (error) {
    addLog('error', `Batch test failed: ${(error as Error).message}`)
  } finally {
    progressMonitor.value = null
  }
}

const addLog = (level: 'info' | 'warn' | 'error', message: string) => {
  logs.value.push({
    timestamp: new Date(),
    level,
    message
  })

  // ログを最大50件に制限
  if (logs.value.length > 50) {
    logs.value = logs.value.slice(-50)
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

// ドラッグ機能
const startDrag = (event: MouseEvent) => {
  if (!monitorRef.value) return

  isDragging.value = true
  const rect = monitorRef.value.getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }

  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)

  // ドラッグ中のカーソルスタイル
  document.body.style.cursor = 'grabbing'
  document.body.style.userSelect = 'none'
}

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return

  const newX = event.clientX - dragOffset.value.x
  const newY = event.clientY - dragOffset.value.y

  // 画面内に制限
  const maxX = window.innerWidth - (monitorRef.value?.offsetWidth || 350)
  const maxY = window.innerHeight - (monitorRef.value?.offsetHeight || 400)

  position.value = {
    x: Math.max(0, Math.min(newX, maxX)),
    y: Math.max(0, Math.min(newY, maxY))
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)

  // カーソルスタイルを元に戻す
  document.body.style.cursor = ''
  document.body.style.userSelect = ''

  // 位置をローカルストレージに保存
  localStorage.setItem('apiMonitorPosition', JSON.stringify(position.value))
}

// 保存された位置を復元
const restorePosition = () => {
  const saved = localStorage.getItem('apiMonitorPosition')
  if (saved) {
    try {
      const savedPosition = JSON.parse(saved) as Position
      // 画面サイズをチェックして有効な位置か確認
      const maxX = window.innerWidth - 350
      const maxY = window.innerHeight - 400

      position.value = {
        x: Math.max(0, Math.min(savedPosition.x, maxX)),
        y: Math.max(0, Math.min(savedPosition.y, maxY))
      }
    } catch (error) {
      console.warn('Failed to restore API monitor position:', error)
    }
  }
}

onMounted(() => {
  // 開発環境でのみ表示
  if (import.meta.env.DEV) {
    restorePosition()
    showMonitor.value = true
    startMonitoring()
  }
})

onUnmounted(() => {
  stopMonitoring()
  // クリーンアップ
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<style scoped>
.api-status-monitor {
  position: fixed;
  width: 350px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  font-family: monospace;
  font-size: 12px;
  cursor: grab;
  user-select: none;
  transition: box-shadow 0.2s ease;
}

.api-status-monitor:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.api-status-monitor:active {
  cursor: grabbing;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
  border-radius: 8px 8px 0 0;
  cursor: grab;
}

.monitor-header:active {
  cursor: grabbing;
}

.monitor-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  cursor: grab;
}

.monitor-header:active h3 {
  cursor: grabbing;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #333;
  background: #e9ecef;
}

.status-info {
  padding: 12px 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 500;
  color: #666;
}

.value {
  font-weight: 600;
  color: #333;
}

.value.active {
  color: #28a745;
}

.progress-section {
  padding: 12px 16px;
  border-top: 1px solid #eee;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 11px;
  color: #666;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #28a745);
  transition: width 0.3s ease;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #999;
}

.actions {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #f8f9fa;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-btn {
  color: #dc3545;
  border-color: #dc3545;
}

.clear-btn:hover:not(:disabled) {
  background: #dc3545;
  color: white;
}

.test-btn {
  color: #007bff;
  border-color: #007bff;
}

.test-btn:hover:not(:disabled) {
  background: #007bff;
  color: white;
}

.log-section {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  max-height: 200px;
  overflow: hidden;
}

.log-section h4 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
}

.log-container {
  max-height: 150px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  font-size: 10px;
  line-height: 1.2;
}

.log-entry.info {
  color: #007bff;
}

.log-entry.warn {
  color: #ffc107;
}

.log-entry.error {
  color: #dc3545;
}

.log-time {
  color: #999;
  min-width: 60px;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.monitor-toggle-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 8px 12px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  z-index: 1000;
  transition: background-color 0.2s;
}

.monitor-toggle-btn:hover {
  background: #0056b3;
}

/* ドラッグ中のスタイル */
.api-status-monitor.dragging {
  opacity: 0.8;
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .api-status-monitor {
    width: 300px;
    max-width: calc(100vw - 40px);
  }

  .monitor-toggle-btn {
    top: 10px;
    right: 10px;
    padding: 6px 10px;
    font-size: 11px;
  }
}
</style>
