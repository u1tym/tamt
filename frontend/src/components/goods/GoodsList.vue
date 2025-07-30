<template>
  <div class="goods-list">
    <div class="section-header">
      <h2>GOODS管理</h2>
      <button @click="showAddDialog = true" class="add-button">
        ＋ 新規GOODS登録
      </button>
    </div>

    <!-- GOODS一覧 -->
    <div class="goods-table-container">
      <table class="goods-table">
        <thead>
          <tr>
            <th>画像</th>
            <th>タイトル</th>
            <th>メディア</th>
            <th>アーティスト</th>
            <th>リリース日</th>
            <th>所持</th>
            <th>コード番号</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="goods in goodsList"
            :key="goods.id"
            class="goods-row"
            @click="editGoods(goods)"
          >
            <td class="goods-image-cell">
              <div class="goods-image">
                <img 
                  v-if="goods.images && goods.images.length > 0" 
                  :src="getImageSrc(goods.images[0])" 
                  :alt="goods.title"
                  @error="handleImageError"
                />
                <div v-else class="no-image">画像なし</div>
              </div>
            </td>
            <td class="goods-title-cell">{{ goods.title }}</td>
            <td class="goods-media-cell">{{ getMediaName(goods.media_id) }}</td>
            <td class="goods-artist-cell">{{ getArtistName(goods.artist_id) }}</td>
            <td class="goods-date-cell">{{ formatDate(goods.release_date) }}</td>
            <td class="goods-owned-cell">
              <span v-if="goods.is_owned" class="owned-badge">✓</span>
              <span v-else class="not-owned-badge">-</span>
            </td>
            <td class="goods-code-cell">{{ goods.code_number || '-' }}</td>
            <td class="goods-actions-cell">
              <button @click.stop="editGoods(goods)" class="edit-btn" title="編集">
                ✏️
              </button>
              <button @click.stop="deleteGoods(goods)" class="delete-btn" title="削除">
                🗑️
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 新規追加・編集ダイアログ -->
    <div v-if="showAddDialog || showEditDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? 'GOODS編集' : '新規GOODS登録' }}</h3>
          <button class="close-button" @click="closeDialog">&times;</button>
        </div>

        <form @submit.prevent="isEditing ? updateGoods() : addGoods()" class="modal-form">
          <div class="form-group">
            <label for="media_id">メディア名称 *</label>
            <select
              id="media_id"
              v-model.number="form.media_id"
              required
              class="form-select"
            >
              <option value="">選択してください</option>
              <option v-for="media in mediaList" :key="media.id" :value="media.id">
                {{ media.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="artist_id">アーティスト *</label>
            <select
              id="artist_id"
              v-model.number="form.artist_id"
              required
              class="form-select"
            >
              <option value="">選択してください</option>
              <option v-for="artist in artists" :key="artist.id" :value="artist.id">
                {{ artist.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="title">タイトル *</label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              class="form-input"
              placeholder="GOODSのタイトルを入力してください"
            />
          </div>

          <div class="form-group">
            <label for="release_date">リリース年月日 *</label>
            <input
              id="release_date"
              v-model="form.release_date"
              type="date"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="is_owned">所持フラグ</label>
            <div class="checkbox-group">
              <input
                id="is_owned"
                v-model="form.is_owned"
                type="checkbox"
                class="form-checkbox"
              />
              <label for="is_owned" class="checkbox-label">所持している</label>
            </div>
          </div>

          <div class="form-group">
            <label for="code_number">コード番号</label>
            <input
              id="code_number"
              v-model="form.code_number"
              type="text"
              class="form-input"
              placeholder="コード番号があれば入力してください"
            />
          </div>

          <div class="form-group">
            <label for="memo">メモ</label>
            <textarea
              id="memo"
              v-model="form.memo"
              rows="3"
              class="form-textarea"
              placeholder="メモがあれば入力してください"
            ></textarea>
          </div>

          <div class="form-group">
            <label>画像</label>
            <div class="image-upload-area">
              <div
                class="drop-zone"
                @drop="handleDrop"
                @dragover.prevent
                @dragenter.prevent
                @click="triggerFileInput"
              >
                <div v-if="form.images.length === 0" class="drop-zone-text">
                  <div class="upload-icon">📁</div>
                  <div>画像をドラッグ&ドロップまたはクリックして選択</div>
                </div>
                <div v-else class="image-preview-list">
                  <div
                    v-for="(image, index) in form.images"
                    :key="index"
                    :class="['image-preview-item', image.isExisting ? 'existing' : 'new']"
                  >
                    <img :src="image.preview" :alt="`画像${index + 1}`" />
                    <button
                      type="button"
                      @click.stop="removeImage(index)"
                      class="remove-image-btn"
                      :title="image.isExisting ? '既存画像を削除' : '新規画像を削除'"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/*"
                @change="handleFileSelect"
                style="display: none"
              />
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeDialog" class="btn btn-secondary">
              キャンセル
            </button>
            <button
              v-if="isEditing"
              type="button"
              @click="deleteGoods(currentGoods)"
              class="btn btn-danger"
              :disabled="isSubmitting"
            >
              削除
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
}

interface Artist {
  id: number
  name: string
}

interface GoodsImage {
  id: number
  image_data: string  // Base64エンコードされた文字列
  image_type: string
  display_order: number
}

interface Goods {
  id: number
  media_id: number
  artist_id: number
  title: string
  release_date: string
  memo?: string
  is_owned: boolean
  code_number?: string
  is_deleted: boolean
  created_at: string
  updated_at: string
  images?: GoodsImage[]
}

interface ImageFile {
  file: File | null
  preview: string
  image_data: string  // Base64エンコードされた文字列
  image_type: string
  isExisting?: boolean  // 既存画像フラグ
  id?: number  // 既存画像のID
}

const goodsList = ref<Goods[]>([])
const mediaList = ref<Media[]>([])
const artists = ref<Artist[]>([])
const error = ref('')
const isSubmitting = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const currentGoods = ref<Goods | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const form = ref({
  media_id: 0,
  artist_id: 0,
  title: '',
  release_date: '',
  memo: '',
  is_owned: false,
  code_number: '',
  images: [] as ImageFile[]
})

// データ取得
const fetchGoods = async () => {
  try {
    const response = await fetch(buildApiUrl('/goods'))
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    goodsList.value = data
  } catch (e: any) {
    console.error('GOODSデータ取得エラー:', e)
    error.value = `GOODSデータの取得に失敗しました: ${e.message}`
  }
}

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

const fetchArtists = async () => {
  try {
    const response = await fetch(buildApiUrl('/artists'))
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    artists.value = data
  } catch (e: any) {
    console.error('アーティストデータ取得エラー:', e)
    error.value = `アーティストデータの取得に失敗しました: ${e.message}`
  }
}

const resetForm = () => {
  form.value = {
    media_id: 0,
    artist_id: 0,
    title: '',
    release_date: '',
    memo: '',
    is_owned: false,
    code_number: '',
    images: []
  }
  isEditing.value = false
  editingId.value = null
  currentGoods.value = null
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  resetForm()
  error.value = ''
}

const editGoods = (goods: Goods) => {
  isEditing.value = true
  editingId.value = goods.id
  currentGoods.value = goods
  
  // 既存の画像を表示用に変換
  const existingImages = goods.images?.map(img => ({
    file: null as File | null,
    preview: `data:${img.image_type};base64,${img.image_data}`,
    image_data: img.image_data,
    image_type: img.image_type,
    isExisting: true,  // 既存画像フラグ
    id: img.id  // 既存画像のID
  })) || []
  
  form.value = {
    media_id: goods.media_id,
    artist_id: goods.artist_id,
    title: goods.title,
    release_date: goods.release_date,
    memo: goods.memo || '',
    is_owned: goods.is_owned,
    code_number: goods.code_number || '',
    images: existingImages
  }
  showEditDialog.value = true
}

const addGoods = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const goodsData = {
      media_id: form.value.media_id,
      artist_id: form.value.artist_id,
      title: form.value.title,
      release_date: form.value.release_date,
      memo: form.value.memo,
      is_owned: form.value.is_owned,
      code_number: form.value.code_number || null,
      images: form.value.images.map(img => ({
        image_data: img.image_data,  // 既にBase64エンコード済み
        image_type: img.image_type,
        display_order: 0
      }))
    }

    const response = await fetch(buildApiUrl('/goods'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(goodsData)
    })
    
    if (!response.ok) {
      throw new Error('登録に失敗しました')
    }

    closeDialog()
    await fetchGoods()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const updateGoods = async () => {
  if (!editingId.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    const goodsData = {
      media_id: form.value.media_id,
      artist_id: form.value.artist_id,
      title: form.value.title,
      release_date: form.value.release_date,
      memo: form.value.memo,
      is_owned: form.value.is_owned,
      code_number: form.value.code_number || null,
      images: form.value.images.map(img => ({
        image_data: img.image_data,  // 既にBase64エンコード済み
        image_type: img.image_type,
        display_order: 0
      }))
    }

    const response = await fetch(buildApiUrl(`/goods/${editingId.value}`), {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(goodsData)
    })
    
    if (!response.ok) {
      throw new Error('更新に失敗しました')
    }

    closeDialog()
    await fetchGoods()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

const deleteGoods = async (goods: Goods | null) => {
  if (!goods || !confirm(`「${goods.title}」を削除しますか？`)) return

  error.value = ''
  isSubmitting.value = true

  try {
    const response = await fetch(buildApiUrl(`/goods/${goods.id}`), {
      method: 'DELETE'
    })
    
    if (!response.ok) {
      throw new Error('削除に失敗しました')
    }

    closeDialog()
    await fetchGoods()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 画像関連の処理
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files))
  }
}

const handleFiles = async (files: File[]) => {
  for (const file of files) {
    if (file.type.startsWith('image/')) {
      try {
        const arrayBuffer = await file.arrayBuffer()
        const imageData = new Uint8Array(arrayBuffer)
        const preview = URL.createObjectURL(file)
        
        // Base64エンコード（大きなデータに対応）
        const base64 = btoa(
          Array.from(imageData)
            .map(byte => String.fromCharCode(byte))
            .join('')
        )
        
        form.value.images.push({
          file,
          preview,
          image_data: base64,
          image_type: file.type,
          isExisting: false
        })
      } catch (e) {
        console.error('画像処理エラー:', e)
        error.value = '画像の処理に失敗しました'
      }
    }
  }
}

const removeImage = (index: number) => {
  const image = form.value.images[index]
  
  // 新規画像の場合のみURL.revokeObjectURLを呼ぶ
  if (!image.isExisting && image.file) {
    URL.revokeObjectURL(image.preview)
  }
  
  form.value.images.splice(index, 1)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  img.parentElement!.innerHTML = '<div class="no-image">画像読み込みエラー</div>'
}

// ユーティリティ関数
const getMediaName = (mediaId: number) => {
  const media = mediaList.value.find(m => m.id === mediaId)
  return media ? media.name : '不明'
}

const getArtistName = (artistId: number) => {
  const artist = artists.value.find(a => a.id === artistId)
  return artist ? artist.name : '不明'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('ja-JP')
}

const getImageSrc = (image: GoodsImage) => {
  try {
    // 画像データは既にBase64エンコードされている
    return `data:${image.image_type};base64,${image.image_data}`
  } catch (e) {
    console.error('画像変換エラー:', e)
    return ''
  }
}

onMounted(() => {
  fetchGoods()
  fetchMedia()
  fetchArtists()
})
</script>

<style scoped>
.goods-list {
  max-width: 1200px;
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

.goods-table-container {
  overflow-x: auto;
  margin-top: 20px;
}

.goods-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.goods-table th {
  background-color: #f5f5f5;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.goods-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  vertical-align: middle;
}

.goods-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.goods-row:hover {
  background-color: #f8f9fa;
}

.goods-image-cell {
  width: 80px;
}

.goods-title-cell {
  font-weight: 500;
  color: #333;
}

.goods-media-cell,
.goods-artist-cell {
  color: #666;
}

.goods-date-cell {
  color: #666;
  white-space: nowrap;
}

.goods-actions-cell {
  width: 100px;
  text-align: center;
}

.goods-owned-cell {
  width: 60px;
  text-align: center;
}

.goods-code-cell {
  width: 120px;
  color: #666;
  font-family: monospace;
}

.owned-badge {
  display: inline-block;
  background-color: #4caf50;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  font-size: 12px;
  font-weight: bold;
}

.not-owned-badge {
  color: #999;
  font-size: 14px;
}



.goods-image {
  width: 60px;
  height: 60px;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 4px;
}

.goods-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: #999;
  font-size: 12px;
  text-align: center;
}

.edit-btn,
.delete-btn {
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

.delete-btn:hover {
  background-color: #ffebee;
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
  max-width: 600px;
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
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.image-upload-area {
  margin-top: 8px;
}

.drop-zone {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.drop-zone:hover {
  border-color: #4CAF50;
  background-color: #f8f9fa;
}

.drop-zone-text {
  color: #666;
}

.upload-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.image-preview-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
  width: 100%;
}

.image-preview-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-preview-item.existing {
  border: 2px solid #2196F3;
}

.image-preview-item.new {
  border: 2px solid #4CAF50;
}

.image-preview-item img {
  width: 100%;
  height: 100px;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d32f2f;
}

.remove-image-btn:hover {
  background: rgba(255, 255, 255, 1);
  color: #b71c1c;
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

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 14px;
  color: #333;
  cursor: pointer;
  user-select: none;
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

  .goods-table-container {
    margin-top: 16px;
  }
  
  .goods-table {
    font-size: 14px;
  }
  
  .goods-table th,
  .goods-table td {
    padding: 8px 12px;
  }
  
  .goods-image {
    width: 50px;
    height: 50px;
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

  .image-preview-list {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
}
</style> 