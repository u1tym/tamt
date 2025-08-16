<template>
  <div class="knowhow-management">
    <div class="header-container">
      <div class="header-left">
        <img src="/images/KNOWHOW.jpg" alt="KNOWHOW" class="header-icon" />
        <h2 class="page-title">KNOWHOW</h2>
      </div>
      <div class="header-right">
        <img 
          src="/images/CONFIG.jpg" 
          alt="CONFIG" 
          class="config-icon" 
          @click="toggleEditMode"
          title="編集モード切り替え"
        />
        <img 
          src="/images/PORTAL.jpg" 
          alt="PORTAL" 
          class="portal-icon" 
          @click="$router.push('/menu')"
          title="トップメニューに戻る"
        />
      </div>
    </div>

    <!-- タブ切り替え -->
    <div class="tab-container" v-if="showTabs">
      <button 
        :class="['tab-button', { active: activeTab === 'category' }]" 
        @click="activeTab = 'category'"
      >
        カテゴリ編集
      </button>
      <button 
        :class="['tab-button', { active: activeTab === 'content' }]" 
        @click="activeTab = 'content'"
      >
        本文編集
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
                :class="{ expanded: expandedMajorCategories.includes(String(majorCategory)) }"
              >
                <span class="expand-icon">{{ expandedMajorCategories.includes(String(majorCategory)) ? '▼' : '▶' }}</span>
                {{ majorCategory }}
              </div>
              <div
                v-if="expandedMajorCategories.includes(String(majorCategory))"
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
                    :class="{ expanded: expandedMiddleCategories.includes(`${String(majorCategory)}-${String(middleCategory)}`) }"
                  >
                    <span class="expand-icon">{{ expandedMiddleCategories.includes(`${String(majorCategory)}-${String(middleCategory)}`) ? '▼' : '▶' }}</span>
                    {{ middleCategory }}
                  </div>
                  <div
                    v-if="expandedMiddleCategories.includes(`${String(majorCategory)}-${String(middleCategory)}`)"
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
                <span class="category">{{ selectedKnowhow.major_category_name }} > {{ selectedKnowhow.middle_category_name }}</span>
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

    <!-- KNOWHOW編集画面 -->
    <div v-if="activeTab === 'content'" class="edit-view">
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
                :class="{ expanded: expandedMajorCategories.includes(String(majorCategory)) }"
              >
                <span class="expand-icon">{{ expandedMajorCategories.includes(String(majorCategory)) ? '▼' : '▶' }}</span>
                {{ majorCategory }}
              </div>
              <div
                v-if="expandedMajorCategories.includes(String(majorCategory))"
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
                <select
                  id="major-category"
                  v-model="form.major_category"
                  required
                  class="form-select"
                  @change="form.middle_category_id = ''"
                >
                  <option value="">大項目を選択してください</option>
                  <option
                    v-for="category in majorCategoryOptions"
                    :key="category.value"
                    :value="category.value"
                  >
                    {{ category.label }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="middle-category">中項目 *</label>
                <select
                  id="middle-category"
                  v-model="form.middle_category_id"
                  required
                  class="form-select"
                  :disabled="!form.major_category"
                >
                  <option value="">中項目を選択してください</option>
                  <option
                    v-for="category in middleCategoryOptions"
                    :key="category.value"
                    :value="category.value"
                  >
                    {{ category.label }}
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

    <!-- カテゴリ編集画面 -->
    <div v-if="activeTab === 'category'" class="category-view">
      <div class="category-layout">
        <!-- 左側：大項目管理 -->
        <div class="major-category-panel">
          <div class="panel-header">
            <h3>大項目管理</h3>
          </div>
          <div class="panel-content">
            <!-- 大項目一覧 -->
            <div class="category-list">
              <div
                v-for="majorCategory in majorCategories"
                :key="majorCategory.id"
                class="category-item"
                :class="{ selected: editingMajorCategory === majorCategory.name }"
                @click="editMajorCategory(majorCategory.name)"
              >
                <span class="category-name">{{ majorCategory.name }}</span>
                <div class="category-actions">
                  <button
                    @click.stop="editMajorCategory(majorCategory.name)"
                    class="action-btn edit-btn"
                    title="名称変更"
                  >
                    ✏️
                  </button>
                </div>
              </div>
            </div>

            <!-- 大項目新規追加 -->
            <div class="add-category-form">
              <h4>新規大項目追加</h4>
              <div class="form-group">
                <input
                  v-model="newMajorCategory"
                  type="text"
                  placeholder="大項目名を入力"
                  class="form-input"
                />
                <button
                  @click="addMajorCategory"
                  class="btn btn-primary"
                  :disabled="!newMajorCategory.trim()"
                >
                  追加
                </button>
              </div>
            </div>

            <!-- 大項目名称変更 -->
            <div v-if="editingMajorCategory" class="edit-category-form">
              <h4>大項目名称変更</h4>
              <div class="form-group">
                <input
                  v-model="editingMajorCategory"
                  type="text"
                  placeholder="新しい名称を入力"
                  class="form-input"
                />
                <div class="form-actions">
                  <button
                    @click="saveMajorCategory"
                    class="btn btn-primary"
                    :disabled="!editingMajorCategory.trim()"
                  >
                    保存
                  </button>
                  <button
                    @click="cancelEditMajorCategory"
                    class="btn btn-secondary"
                  >
                    キャンセル
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右側：中項目管理 -->
        <div class="middle-category-panel">
          <div class="panel-header">
            <h3>中項目管理</h3>
          </div>
          <div class="panel-content">
            <!-- 大項目選択 -->
            <div class="major-category-selector">
              <label for="major-category-select">大項目を選択:</label>
              <select
                id="major-category-select"
                v-model="selectedMajorCategory"
                class="form-select"
              >
                <option value="">大項目を選択してください</option>
                <option
                  v-for="majorCategory in majorCategories"
                  :key="majorCategory.id"
                  :value="majorCategory.id.toString()"
                >
                  {{ majorCategory.name }}
                </option>
              </select>
            </div>

            <!-- 中項目一覧 -->
            <div v-if="selectedMajorCategory" class="category-list">
              <div
                v-for="middleCategory in middleCategories.filter(cat => cat.major_category_id === parseInt(selectedMajorCategory))"
                :key="middleCategory.id"
                class="category-item"
                :class="{ selected: editingMiddleCategory === middleCategory.name }"
                @click="editMiddleCategory(middleCategory.name)"
              >
                <span class="category-name">{{ middleCategory.name }}</span>
                <div class="category-actions">
                  <button
                    @click.stop="editMiddleCategory(middleCategory.name)"
                    class="action-btn edit-btn"
                    title="名称変更"
                  >
                    ✏️
                  </button>
                </div>
              </div>
            </div>

            <!-- 中項目新規追加 -->
            <div v-if="selectedMajorCategory" class="add-category-form">
              <h4>新規中項目追加</h4>
              <div class="form-group">
                <input
                  v-model="newMiddleCategory"
                  type="text"
                  placeholder="中項目名を入力"
                  class="form-input"
                />
                <button
                  @click="addMiddleCategory"
                  class="btn btn-primary"
                  :disabled="!newMiddleCategory.trim()"
                >
                  追加
                </button>
              </div>
            </div>

            <!-- 中項目名称変更 -->
            <div v-if="editingMiddleCategory && selectedMajorCategory" class="edit-category-form">
              <h4>中項目名称変更</h4>
              <div class="form-group">
                <input
                  v-model="editingMiddleCategory"
                  type="text"
                  placeholder="新しい名称を入力"
                  class="form-input"
                />
                <div class="form-actions">
                  <button
                    @click="saveMiddleCategory"
                    class="btn btn-primary"
                    :disabled="!editingMiddleCategory.trim()"
                  >
                    保存
                  </button>
                  <button
                    @click="cancelEditMiddleCategory"
                    class="btn btn-secondary"
                  >
                    キャンセル
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>



    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue'
import { 
  getKnowhowTree, 
  getMajorCategories, 
  getMiddleCategories,
  createMajorCategory,
  updateMajorCategory,
  createMiddleCategory,
  updateMiddleCategory,
  buildApiUrl
} from '../../utils/api'

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
  major_category_name?: string
  middle_category_name?: string
}

interface TreeItem {
  id: number
  title: string
  keywords: string | null
  display_order: number
  middle_category_id: number
}

const activeTab = ref<'search' | 'category' | 'content'>('search')
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

// カテゴリ編集用の変数
const editingMajorCategory = ref<string>('')
const editingMiddleCategory = ref<string>('')
const newMajorCategory = ref<string>('')
const newMiddleCategory = ref<string>('')
const selectedMajorCategory = ref<string>('')

const form = ref({
  major_category: '',
  middle_category_id: '',
  title: '',
  keywords: '',
  content: ''
})

// ツリー構造を取得
const fetchKnowhowTree = async () => {
  try {
    console.log('ツリー構造を取得中...')
    const response = await getKnowhowTree()
    console.log('取得したデータ:', response)
    knowhowTree.value = response.data
    filteredTree.value = { ...response.data }
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
    const res = await fetch(buildApiUrl(`/knowhow/knowhows/${id}`))
    if (!res.ok) throw new Error('KNOWHOWの取得に失敗しました')
    const response = await res.json()
    return response.data
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
    // カテゴリ情報を追加
    const middleCategory = middleCategories.value.find(cat => cat.id === knowhow.middle_category_id)
    const majorCategory = majorCategories.value.find(cat => cat.id === (middleCategory?.major_category_id || 0))

    selectedKnowhow.value = {
      ...knowhow,
      major_category_name: majorCategory?.name || '',
      middle_category_name: middleCategory?.name || ''
    }
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

    // 中項目IDから大項目IDを取得
    const middleCategory = middleCategories.value.find(cat => cat.id === knowhow.middle_category_id)
    const majorCategoryId = middleCategory ? middleCategory.major_category_id.toString() : ''

    form.value = {
      major_category: majorCategoryId,
      middle_category_id: knowhow.middle_category_id.toString(),
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
    middle_category_id: '',
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
    middle_category_id: '',
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
      ? buildApiUrl(`/knowhow/knowhows/${editingKnowhowId.value}`)
      : buildApiUrl('/knowhow/knowhows')

    const method = isEditing.value ? 'PUT' : 'POST'
    const body = {
      middle_category_id: parseInt(form.value.middle_category_id),
      title: form.value.title,
      keywords: form.value.keywords,
      content: form.value.content
    }

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
    const res = await fetch(buildApiUrl(`/knowhow/knowhows/${id}`), {
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
    const res = await fetch(buildApiUrl(`/knowhow/knowhows/${id}/move-up`), {
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
    const res = await fetch(buildApiUrl(`/knowhow/knowhows/${id}/move-down`), {
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
const toggleMajorCategory = (majorCategory: string | number) => {
  const categoryStr = String(majorCategory)
  const index = expandedMajorCategories.value.indexOf(categoryStr)
  if (index > -1) {
    expandedMajorCategories.value.splice(index, 1)
  } else {
    expandedMajorCategories.value.push(categoryStr)
  }
}

// 中項目の展開/折りたたみ
const toggleMiddleCategory = (majorCategory: string | number, middleCategory: string | number) => {
  const key = `${String(majorCategory)}-${String(middleCategory)}`
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
  // 同じ中項目内のKNOWHOWを取得
  const sameCategoryKnowhows = Object.values(knowhowTree.value)
    .flatMap(major => Object.values(major))
    .flat()
    .filter(t => t.middle_category_id === title.middle_category_id)

  if (sameCategoryKnowhows.length === 0) return true

  const minOrder = Math.min(...sameCategoryKnowhows.map(t => t.display_order))
  return title.display_order === minOrder
}

// 最後のKNOWHOWかどうか判定
const isLastKnowhow = (title: TreeItem) => {
  // 同じ中項目内のKNOWHOWを取得
  const sameCategoryKnowhows = Object.values(knowhowTree.value)
    .flatMap(major => Object.values(major))
    .flat()
    .filter(t => t.middle_category_id === title.middle_category_id)

  if (sameCategoryKnowhows.length === 0) return true

  const maxOrder = Math.max(...sameCategoryKnowhows.map(t => t.display_order))
  return title.display_order === maxOrder
}

// カテゴリ編集用の関数
// 大項目と中項目のデータ
const majorCategories = ref<Array<{id: number, name: string}>>([])
const middleCategories = ref<Array<{id: number, name: string, major_category_id: number}>>([])

// 大項目と中項目を取得
const fetchCategories = async () => {
  try {
    // 大項目を取得
    const majorResponse = await getMajorCategories()
    majorCategories.value = majorResponse.data

    // 中項目を取得
    const middleResponse = await getMiddleCategories()
    middleCategories.value = middleResponse.data
  } catch (e: any) {
    error.value = e.message
  }
}

// 大項目編集開始
const editMajorCategory = (majorCategory: string) => {
  editingMajorCategory.value = majorCategory
}

// 大項目編集キャンセル
const cancelEditMajorCategory = () => {
  editingMajorCategory.value = ''
}

// 大項目保存
const saveMajorCategory = async () => {
  if (!editingMajorCategory.value.trim()) return

  error.value = ''
  isSubmitting.value = true

  try {
    // 編集対象の大項目を検索
    const targetMajorCategory = majorCategories.value.find(cat => cat.name === editingMajorCategory.value)
    if (!targetMajorCategory) {
      throw new Error('大項目が見つかりません')
    }

    await updateMajorCategory(targetMajorCategory.id, {
      name: editingMajorCategory.value.trim()
    })

    await fetchCategories()
    await fetchKnowhowTree()
    editingMajorCategory.value = ''
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 大項目新規追加
const addMajorCategory = async () => {
  if (!newMajorCategory.value.trim()) return

  error.value = ''
  isSubmitting.value = true

  try {
    await createMajorCategory({
      name: newMajorCategory.value.trim()
    })

    await fetchCategories()
    await fetchKnowhowTree()
    newMajorCategory.value = ''
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 中項目編集開始
const editMiddleCategory = (middleCategory: string) => {
  editingMiddleCategory.value = middleCategory
}

// 中項目編集キャンセル
const cancelEditMiddleCategory = () => {
  editingMiddleCategory.value = ''
}

// 中項目保存
const saveMiddleCategory = async () => {
  if (!editingMiddleCategory.value.trim() || !selectedMajorCategory.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    // 編集対象の中項目を検索
    const targetMiddleCategory = middleCategories.value.find(cat =>
      cat.name === editingMiddleCategory.value &&
      cat.major_category_id === parseInt(selectedMajorCategory.value)
    )
    if (!targetMiddleCategory) {
      throw new Error('中項目が見つかりません')
    }

    await updateMiddleCategory(targetMiddleCategory.id, {
      name: editingMiddleCategory.value.trim()
    })

    await fetchCategories()
    await fetchKnowhowTree()
    editingMiddleCategory.value = ''
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 中項目新規追加
const addMiddleCategory = async () => {
  if (!newMiddleCategory.value.trim() || !selectedMajorCategory.value) return

  error.value = ''
  isSubmitting.value = true

  try {
    await createMiddleCategory({
      major_category_id: parseInt(selectedMajorCategory.value),
      name: newMiddleCategory.value.trim()
    })

    await fetchCategories()
    await fetchKnowhowTree()
    newMiddleCategory.value = ''
  } catch (e: any) {
    error.value = e.message
  } finally {
    isSubmitting.value = false
  }
}

// 大項目と中項目の選択肢を取得
const majorCategoryOptions = computed(() => {
  return majorCategories.value.map(cat => ({ value: cat.id.toString(), label: cat.name }))
})

const middleCategoryOptions = computed(() => {
  if (!form.value.major_category) return []
  const majorCategoryId = parseInt(form.value.major_category)
  return middleCategories.value
    .filter(cat => cat.major_category_id === majorCategoryId)
    .map(cat => ({ value: cat.id.toString(), label: cat.name }))
})

// 編集モード切り替え
const toggleEditMode = () => {
  if (activeTab.value === 'search') {
    // 検索画面から編集モードに切り替え
    showTabs.value = true
    activeTab.value = 'category'
  } else {
    // 編集モードから検索画面に戻る
    showTabs.value = false
    activeTab.value = 'search'
  }
}

// タブの表示/非表示
const showTabs = ref(false)

onMounted(() => {
  fetchCategories()
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
  border-bottom: 2px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
}

.page-title {
  margin: 0;
  font-size: 1.8rem;
  color: #333;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
}

.config-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 2px solid transparent;
  margin-right: 10px; /* ポータルアイコンとの間隔 */
}

.config-icon:hover {
  transform: scale(1.1);
  border-color: #8B4513;
}

.portal-icon {
  width: 40px;
  height: 40px;
  object-fit: cover;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 2px solid transparent;
}

.portal-icon:hover {
  transform: scale(1.1);
  border-color: #8B4513;
}

.tab-container {
  display: flex;
  justify-content: left;
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

/* カテゴリ編集画面のスタイル */
.category-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.major-category-panel,
.middle-category-panel {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.panel-content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.category-list {
  margin-bottom: 24px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.category-item:hover {
  background: #f8f9fa;
}

.category-item.selected {
  background: #e8f5e8;
  border-color: #4CAF50;
}

.category-name {
  font-weight: 500;
  color: #333;
}

.category-actions {
  display: flex;
  gap: 4px;
}

.add-category-form,
.edit-category-form {
  margin-top: 24px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #f8f9fa;
}

.add-category-form h4,
.edit-category-form h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 16px;
}

.major-category-selector {
  margin-bottom: 24px;
}

.major-category-selector label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.form-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
  border: 1px solid #ffcdd2;
}

/* 本文編集画面のスタイル */
.content-layout {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
}

.content-view .tree-panel {
  width: 40%;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
}

.content-view .edit-panel {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
}

.edit-form {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.form-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.form-actions {
  display: flex;
  gap: 8px;
}

.form-content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 200px;
}

.form-textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .header-left {
    justify-content: center;
  }

  .header-icon,
  .portal-icon,
  .config-icon {
    width: 35px;
    height: 35px;
  }

  .page-title {
    font-size: 1.5rem;
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