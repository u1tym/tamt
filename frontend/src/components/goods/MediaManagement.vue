<template>
  <div class="media-management">
    <div class="section-header">
      <h2>メディア管理</h2>
      <button @click="showAddDialog = true" class="add-button">
        ＋ 新規メディア追加
      </button>
    </div>

    <!-- メディア一覧 -->
    <div class="media-list-container">
      <div class="media-list">
        <div
          v-for="media in mediaList"
          :key="media.id"
          class="media-item"
          @click="editMedia(media)"
        >
          <div class="media-name">{{ media.name }}</div>
          <div class="media-actions">
            <button @click.stop="editMedia(media)" class="edit-btn" title="編集">
              ✏️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新規追加・編集ダイアログ -->
    <div v-if="showAddDialog || showEditDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'メディア編集' : '新規メディア追加' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updateMedia() : addMedia()" class="modal-form">
          <div class="form-group">
            <label for="media_name">メディア名称 *</label>
            <input
              id="media_name"
              v-model="form.name"
              type="text"
              required
              class="form-input"
              placeholder="メディア名称を入力してください"
            />
          </div>

          <div class="form-actions">
            <button type="button" @click="closeDialog" class="btn btn-secondary">
              キャンセル
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? (isEditing ? '更新中...' : '登録中...') : (isEditing ? '更新' : '登録') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { buildApiUrl } from '../../utils/api'

interface Media {
  id: number
  name: string
  created_at: string
  updated_at: string
}

const mediaList = ref<Media[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const form = ref({
  name: ''
})

// データ取得
const fetchMedia = async () => {
  try {
    const response = await fetch(buildApiUrl('/media'))
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    mediaList.value = data
  } catch (e: any) {
    console.error('メディアデータ取得エラー:', e)
    error.value = `メディアデータの取得に失敗しました: ${e.message}`
  }
}

const resetForm = () => {
  form.value = { name: '' }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  resetForm()
  error.value = ''
}

const editMedia = (media: Media) => {
  isEditing.value = true
  editingId.value = media.id
  form.value.name = media.name
  showEditDialog.value = true
}

const addMedia = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const response = await fetch(buildApiUrl('/media'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    if (!response.ok) {
      throw new Error('登録に失敗しました')
    }

    closeDialog()
    await fetchMedia()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateMedia = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    const response = await fetch(buildApiUrl(`/media/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    
    if (!response.ok) {
      throw new Error('更新に失敗しました')
    }

    closeDialog()
    await fetchMedia()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchMedia()
})
</script>

<style scoped>
.media-management {
  max-width: 800px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.add-button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.add-button:hover {
  background-color: #45a049;
}

.media-list-container {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.media-list-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.media-list {
  display: grid;
  gap: 0;
}

.media-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s;
}

.media-item:last-child {
  border-bottom: none;
}

.media-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.media-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.media-actions {
  display: flex;
  gap: 8px;
}

.edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  font-size: 16px;
  transition: all 0.2s;
}

.edit-btn:hover {
  background-color: #e3f2fd;
  transform: scale(1.1);
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

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
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

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border: 1px solid #ffcdd2;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .add-button {
    width: 100%;
  }

  .media-list-container {
    max-height: calc(100vh - 250px);
  }

  .media-item {
    padding: 12px;
  }

  .modal-content {
    width: 95%;
    margin: 10px;
  }

  .modal-header,
  .modal-form {
    padding-left: 16px;
    padding-right: 16px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style> 