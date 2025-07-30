<template>
  <div class="knowhow-management">
    <div class="header-container">
      <button @click="$router.push('/')" class="back-button">
        ← トップメニューに戻る
      </button>
      <h2 class="page-title">KNOWHOW管理</h2>
    </div>

    <!-- タブ切り替え -->
    <div class="tab-container">
      <button
        @click="activeTab = 'search'"
        :class="['tab-button', { active: activeTab === 'search' }]"
      >
        検索
      </button>
      <button
        @click="activeTab = 'edit'"
        :class="['tab-button', { active: activeTab === 'edit' }]"
      >
        編集
      </button>
    </div>

    <!-- 検索画面 -->
    <div v-if="activeTab === 'search'" class="search-view">
      <div class="search-layout">
        <!-- 左側：ツリー表示 -->
        <div class="tree-panel">
          <div class="tree-header">
            <h3>カテゴリ</h3>
            <div class="search-box">
              <input
                v-model="searchKeyword"
                @input="filterTree"
                type="text"
                placeholder="キーワード検索..."
                class="search-input"
              />
            </div>
          </div>
          <div class="tree-content">
            <div
              v-for="(middleCategories, majorCategory) in filteredTree"
              :key="majorCategory"
              class="major-category"
            >
              <div
                @click="toggleMajorCategory(majorCategory)"
                class="major-category-header"
                :class="{ expanded: expandedMajorCategories.includes(majorCategory) }"
              >
                <span class="expand-icon">{{ expandedMajorCategories.includes(majorCategory) ? '▼' : '▶' }}</span>
                {{ majorCategory }}
              </div>
              <div
                v-if="expandedMajorCategories.includes(majorCategory)"
                class="middle-categories"
              >
                <div
                  v-for="(titles, middleCategory) in middleCategories"
                  :key="middleCategory"
                  class="middle-category"
                >
                  <div
                    @click="toggleMiddleCategory(majorCategory, middleCategory)"
                    class="middle-category-header"
                    :class="{ expanded: expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`) }"
                  >
                    <span class="expand-icon">{{ expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`) ? '▼' : '▶' }}</span>
                    {{ middleCategory }}
                  </div>
                  <div
                    v-if="expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`)"
                    class="titles"
                  >
                    <div
                      v-for="title in titles"
                      :key="title.id"
                      @click="selectKnowhow(title.id)"
                      class="title-item"
                      :class="{ selected: selectedKnowhowId === title.id }"
                    >
                      {{ title.title }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側：内容表示 -->
        <div class="content-panel">
          <div v-if="selectedKnowhow" class="knowhow-content">
            <div class="content-header">
              <h3>{{ selectedKnowhow.title }}</h3>
              <div class="content-meta">
                <span class="category">{{ selectedKnowhow.major_category }} > {{ selectedKnowhow.middle_category }}</span>
                <span v-if="selectedKnowhow.keywords" class="keywords">キーワード: {{ selectedKnowhow.keywords }}</span>
              </div>
            </div>
            <div class="content-body">
              <pre>{{ selectedKnowhow.content }}</pre>
            </div>
          </div>
          <div v-else class="no-selection">
            <p>左側のタイトルをクリックして内容を表示してください</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 編集画面 -->
    <div v-if="activeTab === 'edit'" class="edit-view">
      <div class="edit-layout">
        <!-- 左側：ツリー表示（編集可能） -->
        <div class="tree-panel">
          <div class="tree-header">
            <h3>カテゴリ</h3>
            <button @click="startAdd" class="add-button">
              ＋ 新規追加
            </button>
          </div>
          <div class="tree-content">
            <div
              v-for="(middleCategories, majorCategory) in knowhowTree"
              :key="majorCategory"
              class="major-category"
            >
              <div
                @click="toggleMajorCategory(majorCategory)"
                class="major-category-header"
                :class="{ expanded: expandedMajorCategories.includes(majorCategory) }"
              >
                <span class="expand-icon">{{ expandedMajorCategories.includes(majorCategory) ? '▼' : '▶' }}</span>
                {{ majorCategory }}
              </div>
              <div
                v-if="expandedMajorCategories.includes(majorCategory)"
                class="middle-categories"
              >
                <div
                  v-for="(titles, middleCategory) in middleCategories"
                  :key="middleCategory"
                  class="middle-category"
                >
                  <div
                    @click="toggleMiddleCategory(majorCategory, middleCategory)"
                    class="middle-category-header"
                    :class="{ expanded: expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`) }"
                  >
                    <span class="expand-icon">{{ expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`) ? '▼' : '▶' }}</span>
                    {{ middleCategory }}
                  </div>
                  <div
                    v-if="expandedMiddleCategories.includes(`${majorCategory}-${middleCategory}`)"
                    class="titles"
                  >
                    <div
                      v-for="title in titles"
                      :key="title.id"
                      @click="editKnowhow(title.id)"
                      class="title-item"
                      :class="{ selected: editingKnowhowId === title.id }"
                    >
                      <span class="title-text">{{ title.title }}</span>
                      <div class="title-actions">
                        <button
                          @click.stop="moveKnowhowUp(title.id)"
                          class="action-btn move-up-btn"
                          title="上に移動"
                          :disabled="isFirstKnowhow(title)"
                        >
                          ⬆️
                        </button>
                        <button
                          @click.stop="moveKnowhowDown(title.id)"
                          class="action-btn move-down-btn"
                          title="下に移動"
                          :disabled="isLastKnowhow(title)"
                        >
                          ⬇️
                        </button>
                        <button
                          @click.stop="deleteKnowhow(title.id)"
                          class="action-btn delete-btn"
                          title="削除"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側：編集フォーム -->
        <div class="edit-panel">
          <div v-if="editingKnowhow || isEditing || isAdding" class="edit-form">
            <div class="form-header">
              <h3>{{ isAdding ? '新規KNOWHOW追加' : (isEditing ? 'KNOWHOW編集' : 'KNOWHOW表示') }}</h3>
            </div>
            <form @submit.prevent="saveKnowhow" class="form-content">
              <div class="form-group">
                <label for="major-category">大項目 *</label>
                <input
                  id="major-category"
                  v-model="form.major_category"
                  type="text"
                  required
                  class="form-input"
                  placeholder="例: 技術、業務、その他"
                />
              </div>

              <div class="form-group">
                <label for="middle-category">中項目 *</label>
                <input
                  id="middle-category"
                  v-model="form.middle_category"
                  type="text"
                  required
                  class="form-input"
                  placeholder="例: プログラミング、Excel、会計"
                />
              </div>

              <div class="form-group">
                <label for="title">タイトル *</label>
                <input
                  id="title"
                  v-model="form.title"
                  type="text"
                  required
                  class="form-input"
                  placeholder="例: Pythonでのファイル操作"
                />
              </div>

              <div class="form-group">
                <label for="keywords">キーワード</label>
                <input
                  id="keywords"
                  v-model="form.keywords"
                  type="text"
                  class="form-input"
                  placeholder="例: Python, ファイル, 操作"
                />
              </div>

              <div class="form-group">
                <label for="content">本文 *</label>
                <textarea
                  id="content"
                  v-model="form.content"
                  required
                  class="form-textarea"
                  placeholder="KNOWHOWの詳細内容を入力してください..."
                  rows="15"
                ></textarea>
              </div>

              <div class="form-actions">
                <button
                  type="button"
                  @click="cancelEdit"
                  class="btn btn-secondary"
                >
                  キャンセル
                </button>
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="isSubmitting"
                >
                  {{ isSubmitting ? '保存中...' : '保存' }}
                </button>
              </div>
            </form>
          </div>
          <div v-else class="no-selection">
            <p>左側のタイトルをクリックして編集してください</p>
            <button @click="startAdd" class="btn btn-primary">
              ＋ 新規追加
            </button>
          </div>
        </div>
      </div>
    </div>



    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { buildApiUrl } from '../utils/api'

interface Knowhow {
  id: number
  major_category: string
  middle_category: string
  title: string
  keywords: string | null
  content: string
  display_order: number
  is_deleted: boolean
  created_at: string
  updated_at: string
}

interface TreeItem {
  id: number
  title: string
  keywords: string | null
  display_order: number
}

const activeTab = ref<'search' | 'edit'>('search')
const knowhowTree = ref<{ [majorCategory: string]: { [middleCategory: string]: TreeItem[] } }>({})
const filteredTree = ref<{ [majorCategory: string]: { [middleCategory: string]: TreeItem[] } }>({})
const selectedKnowhow = ref<Knowhow | null>(null)
const selectedKnowhowId = ref<number | null>(null)
const editingKnowhow = ref<Knowhow | null>(null)
const editingKnowhowId = ref<number | null>(null)
const expandedMajorCategories = ref<string[]>([])
const expandedMiddleCategories = ref<string[]>([])
const searchKeyword = ref('')
const error = ref('')
const isSubmitting = ref(false)
const isEditing = ref(false)
const isAdding = ref(false)

const form = ref({
  major_category: '',
  middle_category: '',
  title: '',
  keywords: '',
  content: ''
})

// ツリー構造を取得
const fetchKnowhowTree = async () => {
  try {
    console.log('ツリー構造を取得中...')
    const res = await fetch(buildApiUrl('/knowhows/tree'))
    console.log('レスポンスステータス:', res.status)

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}))
      console.error('エラーレスポンス:', errorData)
      console.error('エラーレスポンス詳細:', JSON.stringify(errorData, null, 2))

      let errorMessage = 'ツリー構造の取得に失敗しました'
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          errorMessage += ': ' + errorData.detail.map((e: any) => e.msg || e).join(', ')
        } else {
          errorMessage += ': ' + errorData.detail
        }
      } else {
        errorMessage += ': ' + res.statusText
      }

      throw new Error(errorMessage)
    }

    const data = await res.json()
    console.log('取得したデータ:', data)
    knowhowTree.value = data
    filteredTree.value = { ...data }
    error.value = '' // エラーをクリア
  } catch (e: any) {
    console.error('ツリー構造取得エラー:', e)
    error.value = e.message
    knowhowTree.value = {}
    filteredTree.value = {}
  }
}

// 特定のKNOWHOWを取得
const fetchKnowhow = async (id: number) => {
  try {
    const res = await fetch(buildApiUrl(`/knowhows/${id}`))
    if (!res.ok) throw new Error('KNOWHOWの取得に失敗しました')
    return await res.json()
  } catch (e: any) {
    error.value = e.message
    return null
  }
}

// 検索画面でKNOWHOWを選択
const selectKnowhow = async (id: number) => {
  selectedKnowhowId.value = id
  const knowhow = await fetchKnowhow(id)
  if (knowhow) {
    selectedKnowhow.value = knowhow
  }
}

// 編集画面でKNOWHOWを選択
const editKnowhow = async (id: number) => {
  editingKnowhowId.value = id
  const knowhow = await fetchKnowhow(id)
  if (knowhow) {
    editingKnowhow.value = knowhow
    isEditing.value = true
    isAdding.value = false
    form.value = {
      major_category: knowhow.major_category,
      middle_category: knowhow.middle_category,
      title: knowhow.title,
      keywords: knowhow.keywords || '',
      content: knowhow.content
    }
  }
}

// 新規追加開始
const startAdd = () => {
  editingKnowhow.value = null
  editingKnowhowId.value = null
  isEditing.value = false
  isAdding.value = true
  form.value = {
    major_category: '',
    middle_category: '',
    title: '',
    keywords: '',
    content: ''
  }
}

// 編集キャンセル
const cancelEdit = () => {
  editingKnowhow.value = null
  editingKnowhowId.value = null
  isEditing.value = false
  isAdding.value = false
  form.value = {
    major_category: '',
    middle_category: '',
    title: '',
    keywords: '',
    content: ''
  }
}

// KNOWHOW保存
const saveKnowhow = async () => {
  error.value = ''
  isSubmitting.value = true

  try {
    const url = isEditing.value
      ? buildApiUrl(`/knowhows/${editingKnowhowId.value}`)
      : buildApiUrl('/knowhows')

    const method = isEditing.value ? 'PUT' : 'POST'
    const body = { ...form.value }

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`${isEditing.value ? '更新' : '登録'}に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchKnowhowTree()
    cancelEdit()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// KNOWHOW削除
const deleteKnowhow = async (id: number) => {
  if (!confirm('このKNOWHOWを削除しますか？')) return

  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/knowhows/${id}`), {
      method: 'DELETE'
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`削除に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchKnowhowTree()
    if (editingKnowhowId.value === id) {
      cancelEdit()
    }
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// KNOWHOWを上に移動
const moveKnowhowUp = async (id: number) => {
  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/knowhows/${id}/move-up`), {
      method: 'POST'
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`上移動に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchKnowhowTree()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// KNOWHOWを下に移動
const moveKnowhowDown = async (id: number) => {
  error.value = ''
  isSubmitting.value = true

  try {
    const res = await fetch(buildApiUrl(`/knowhows/${id}/move-down`), {
      method: 'POST'
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`下移動に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }

    await fetchKnowhowTree()
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 大項目の展開/折りたたみ
const toggleMajorCategory = (majorCategory: string) => {
  const index = expandedMajorCategories.value.indexOf(majorCategory)
  if (index > -1) {
    expandedMajorCategories.value.splice(index, 1)
  } else {
    expandedMajorCategories.value.push(majorCategory)
  }
}

// 中項目の展開/折りたたみ
const toggleMiddleCategory = (majorCategory: string, middleCategory: string) => {
  const key = `${majorCategory}-${middleCategory}`
  const index = expandedMiddleCategories.value.indexOf(key)
  if (index > -1) {
    expandedMiddleCategories.value.splice(index, 1)
  } else {
    expandedMiddleCategories.value.push(key)
  }
}

// ツリー検索フィルタリング
const filterTree = () => {
  if (!searchKeyword.value.trim()) {
    filteredTree.value = { ...knowhowTree.value }
    return
  }

  const filtered: { [majorCategory: string]: { [middleCategory: string]: TreeItem[] } } = {}
  const keyword = searchKeyword.value.toLowerCase()

  for (const [majorCategory, middleCategories] of Object.entries(knowhowTree.value)) {
    const filteredMiddleCategories: { [middleCategory: string]: TreeItem[] } = {}

    for (const [middleCategory, titles] of Object.entries(middleCategories)) {
      const filteredTitles = titles.filter(title =>
        title.title.toLowerCase().includes(keyword) ||
        (title.keywords && title.keywords.toLowerCase().includes(keyword))
      )

      if (filteredTitles.length > 0) {
        filteredMiddleCategories[middleCategory] = filteredTitles
      }
    }

    if (Object.keys(filteredMiddleCategories).length > 0) {
      filtered[majorCategory] = filteredMiddleCategories
    }
  }

  filteredTree.value = filtered
}

// 最初のKNOWHOWかどうか判定
const isFirstKnowhow = (title: TreeItem) => {
  const majorCategory = Object.keys(knowhowTree.value).find(mc =>
    Object.keys(knowhowTree.value[mc]).some(midc =>
      knowhowTree.value[mc][midc].some(t => t.id === title.id)
    )
  )

  if (!majorCategory) return true

  const middleCategory = Object.keys(knowhowTree.value[majorCategory]).find(midc =>
    knowhowTree.value[majorCategory][midc].some(t => t.id === title.id)
  )

  if (!middleCategory) return true

  const titles = knowhowTree.value[majorCategory][middleCategory]
  const minOrder = Math.min(...titles.map(t => t.display_order))
  return title.display_order === minOrder
}

// 最後のKNOWHOWかどうか判定
const isLastKnowhow = (title: TreeItem) => {
  const majorCategory = Object.keys(knowhowTree.value).find(mc =>
    Object.keys(knowhowTree.value[mc]).some(midc =>
      knowhowTree.value[mc][midc].some(t => t.id === title.id)
    )
  )

  if (!majorCategory) return true

  const middleCategory = Object.keys(knowhowTree.value[majorCategory]).find(midc =>
    knowhowTree.value[majorCategory][midc].some(t => t.id === title.id)
  )

  if (!middleCategory) return true

  const titles = knowhowTree.value[majorCategory][middleCategory]
  const maxOrder = Math.max(...titles.map(t => t.display_order))
  return title.display_order === maxOrder
}



onMounted(() => {
  fetchKnowhowTree()
})
</script>

<style scoped>
.knowhow-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-container {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  gap: 20px;
}

.back-button {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.back-button:hover {
  background: #e8e8e8;
}

.page-title {
  text-align: center;
  margin: 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
  flex: 1;
}

.tab-container {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-button {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-button:hover {
  color: #333;
}

.tab-button.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
}

.search-layout,
.edit-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.tree-panel {
  width: 35%;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
}

.tree-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.tree-header h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 18px;
}

.search-box {
  margin-bottom: 8px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.add-button {
  width: 100%;
  padding: 8px 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.add-button:hover {
  background: #45a049;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.major-category {
  margin-bottom: 8px;
}

.major-category-header {
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
}

.major-category-header:hover {
  background: #e9ecef;
}

.major-category-header.expanded {
  background: #e3f2fd;
  border-color: #2196F3;
}

.expand-icon {
  margin-right: 8px;
  font-size: 12px;
  color: #666;
}

.middle-categories {
  margin-left: 16px;
  margin-top: 4px;
}

.middle-category {
  margin-bottom: 4px;
}

.middle-category-header {
  padding: 6px 10px;
  background: #f1f3f4;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
}

.middle-category-header:hover {
  background: #e8eaed;
}

.middle-category-header.expanded {
  background: #e8f5e8;
  border-color: #4CAF50;
}

.titles {
  margin-left: 16px;
  margin-top: 4px;
}

.title-item {
  padding: 6px 10px;
  margin-bottom: 2px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s;
}

.title-item:hover {
  background: #f8f9fa;
}

.title-item.selected {
  background: #e3f2fd;
  border-color: #2196F3;
}

.title-text {
  flex: 1;
}

.title-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 2px;
  font-size: 12px;
  transition: all 0.2s;
}

.move-up-btn:hover {
  background: #e8f5e8;
}

.move-down-btn:hover {
  background: #e8f5e8;
}

.delete-btn:hover {
  background: #ffebee;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.content-panel,
.edit-panel {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
}

.knowhow-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.content-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.content-header h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 24px;
}

.content-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  color: #666;
}

.category {
  font-weight: 500;
  color: #4CAF50;
}

.keywords {
  font-style: italic;
}

.content-body {
  line-height: 1.6;
}

.content-body pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  text-align: center;
}

.no-selection p {
  margin-bottom: 16px;
}

.edit-form {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.form-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.form-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-input,
.form-textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 200px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
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
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #e8e8e8;
}



.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border: 1px solid #ffcdd2;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .back-button {
    align-self: flex-start;
  }

  .search-layout,
  .edit-layout {
    flex-direction: column;
    height: auto;
  }

  .tree-panel {
    width: 100%;
    height: 300px;
  }

  .search-input {
    font-size: 16px; /* モバイルでのズームを防ぐ */
  }

  .content-panel,
  .edit-panel {
    height: 400px;
  }

  .page-title {
    font-size: 1.2rem;
  }

  .tab-button {
    padding: 8px 16px;
    font-size: 14px;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>