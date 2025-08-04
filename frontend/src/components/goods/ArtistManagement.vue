<template>
  <div class="artist-management">
    <div class="section-header">
      <h2>アーティスト管理</h2>
      <button @click="showAddDialog = true" class="add-button">
        ＋ 新規アーティスト追加
      </button>
    </div>

    <!-- アーティスト一覧 -->
    <div class="artist-list-container">
      <div class="artist-list">
        <div
          v-for="artist in artists"
          :key="artist.id"
          class="artist-item"
          @click="editArtist(artist)"
        >
          <div class="artist-info">
            <div class="artist-name">{{ artist.name }}</div>
            <div class="artist-persons">
              <span v-if="artist.persons && artist.persons.length > 0">
                所属: {{ artist.persons.map(p => p.name).join(', ') }}
              </span>
              <span v-else class="no-persons">所属パーソンなし</span>
            </div>
          </div>
          <div class="artist-actions">
            <button @click.stop="editArtist(artist)" class="edit-btn" title="編集">
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
          <h3>{{ isEditing ? 'アーティスト編集' : '新規アーティスト追加' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updateArtist() : addArtist()" class="modal-form">
          <div class="form-group">
            <label for="artist_name">アーティスト名 *</label>
            <input
              id="artist_name"
              v-model="form.name"
              type="text"
              required
              class="form-input"
              placeholder="アーティスト名を入力してください"
            />
          </div>

          <div class="form-group">
            <label>所属パーソン</label>
            <div class="person-selection">
              <div
                v-for="person in persons"
                :key="person.id"
                class="person-checkbox"
              >
                <input
                  :id="`person_${person.id}`"
                  type="checkbox"
                  :value="person.id"
                  v-model="form.person_ids"
                  class="checkbox-input"
                />
                <label :for="`person_${person.id}`" class="checkbox-label">
                  {{ person.name }}
                </label>
              </div>
            </div>
            <div v-if="persons.length === 0" class="no-persons-message">
              パーソンが登録されていません。先にパーソンを登録してください。
            </div>
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
import { getArtists, getPersons, createArtist, updateArtist as apiUpdateArtist, getArtistWithPersons } from '../../utils/api'

interface Person {
  id: number
  name: string
  created_at: string
  updated_at: string
}

interface Artist {
  id: number
  name: string
  created_at: string
  updated_at: string
  persons?: Person[]
}

const artists = ref<Artist[]>([])
const persons = ref<Person[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const form = ref({
  name: '',
  person_ids: [] as number[]
})

// データ取得
const fetchArtists = async () => {
  try {
    const response = await getArtists()
    artists.value = response.data

    // 各アーティストのパーソン情報を取得
    for (const artist of artists.value) {
      try {
        const artistWithPersons = await getArtistWithPersons(artist.id)
        artist.persons = artistWithPersons.data.persons || []
      } catch (e) {
        console.error(`アーティスト ${artist.id} のパーソン情報取得エラー:`, e)
        artist.persons = []
      }
    }
  } catch (e: any) {
    console.error('アーティストデータ取得エラー:', e)
    error.value = `アーティストデータの取得に失敗しました: ${e.message}`
  }
}

const fetchPersons = async () => {
  try {
    const response = await getPersons()
    persons.value = response.data
  } catch (e: any) {
    console.error('パーソンデータ取得エラー:', e)
    error.value = `パーソンデータの取得に失敗しました: ${e.message}`
  }
}

const resetForm = () => {
  form.value = { name: '', person_ids: [] }
  isEditing.value = false
  editingId.value = null
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  resetForm()
  error.value = ''
}

const editArtist = (artist: Artist) => {
  isEditing.value = true
  editingId.value = artist.id
  form.value.name = artist.name
  form.value.person_ids = artist.persons?.map(p => p.id) || []
  showEditDialog.value = true
}

const addArtist = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    await createArtist(form.value)
    closeDialog()
    await fetchArtists()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateArtist = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    await apiUpdateArtist(editingId.value, form.value)
    closeDialog()
    await fetchArtists()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchArtists()
  fetchPersons()
})
</script>

<style scoped>
.artist-management {
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

.artist-list-container {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.artist-list-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.artist-list {
  display: grid;
  gap: 0;
}

.artist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s;
}

.artist-item:last-child {
  border-bottom: none;
}

.artist-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.artist-info {
  flex: 1;
}

.artist-name {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.artist-persons {
  font-size: 14px;
  color: #666;
}

.no-persons {
  color: #999;
  font-style: italic;
}

.artist-actions {
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

.person-selection {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  background-color: #f9f9f9;
}

.person-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.person-checkbox:last-child {
  margin-bottom: 0;
}

.checkbox-input {
  margin-right: 8px;
  transform: scale(1.2);
}

.checkbox-label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  user-select: none;
}

.no-persons-message {
  padding: 12px;
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  color: #856404;
  font-size: 14px;
  text-align: center;
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

  .artist-list-container {
    max-height: calc(100vh - 250px);
  }

  .artist-item {
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