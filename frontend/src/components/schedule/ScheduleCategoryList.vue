<template>
  <div class="activity-categories">
    <h2>活動区分</h2>
    <div class="category-list">
      <div v-for="category in activityCategories" :key="category.id" class="category-item">
        <input
            type="checkbox"
            :id="'category-' + category.id"
            :checked="selectedCategories.includes(category.id)"
            @change="toggleCategory(category.id)"
            :style="{ accentColor: getCategoryColor(category.id, activityCategories) }"
        />
        <div class="category-content">
          <span v-if="!category.editing" @click="startEditCategory(category)" class="category-name" :title="category.name">
            {{ truncateCategoryName(category.name) }}
          </span>
          <div v-else class="edit-category">
             <input
               v-model="category.editName"
               @keyup.enter="saveCategoryName(category)"
               @keyup.esc="cancelEditCategory(category)"
               @blur="saveCategoryName(category)"
               ref="categoryInput"
               class="edit-input"
               maxlength="20"
             />
          </div>
        </div>
        <button class="delete-btn" @click="deleteCategory(category.id)" title="削除">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="add-category">
      <input v-model="newCategoryName" placeholder="新区分名" maxlength="20" />
      <button @click="addCategory">追加</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { createActivityCategory, deleteActivityCategory, updateActivityCategory } from '../../utils/api'
import { getCategoryColor } from './ScheduleCommon'

// Props
interface Props {
  activityCategories: any[]
  selectedCategories: number[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  updateActivityCategories: [categories: any[]]
  updateSelectedCategories: [categories: number[]]
  refreshSchedules: []
}>()

// Local state
const newCategoryName = ref('')

// Methods
function toggleCategory(categoryId: number) {
  const index = props.selectedCategories.indexOf(categoryId)
  const newSelectedCategories = [...props.selectedCategories]
  
  if (index > -1) {
    newSelectedCategories.splice(index, 1)
  } else {
    newSelectedCategories.push(categoryId)
  }
  
  emit('updateSelectedCategories', newSelectedCategories)
}

async function addCategory() {
  if (!newCategoryName.value.trim()) return

  try {
    const response = await createActivityCategory({
      name: newCategoryName.value.trim()
    })
    const newCategories = [...props.activityCategories, response.data]
    const newSelectedCategories = [...props.selectedCategories, response.data.id]
    
    emit('updateActivityCategories', newCategories)
    emit('updateSelectedCategories', newSelectedCategories)
    newCategoryName.value = ''
  } catch (error) {
    console.error('活動区分の追加に失敗しました:', error)
  }
}

async function deleteCategory(categoryId: number) {
  if (!confirm('この活動区分を削除しますか？関連するスケジュールも削除されます。')) return

  try {
    await deleteActivityCategory(categoryId)
    const newCategories = props.activityCategories.filter(cat => cat.id !== categoryId)
    const newSelectedCategories = props.selectedCategories.filter(id => id !== categoryId)
    
    emit('updateActivityCategories', newCategories)
    emit('updateSelectedCategories', newSelectedCategories)
    emit('refreshSchedules')
  } catch (error) {
    console.error('活動区分の削除に失敗しました:', error)
  }
}

// 活動区分の編集機能
function startEditCategory(category: any) {
  category.editing = true
  category.editName = category.name
  // 次のティックでフォーカスを設定
  nextTick(() => {
    const input = document.querySelector('.edit-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

async function saveCategoryName(category: any) {
  if (!category.editName.trim() || category.editName === category.name) {
    category.editing = false
    return
  }

  try {
    const response = await updateActivityCategory(category.id, {
      name: category.editName.trim()
    })
    category.name = response.data.name
  } catch (error) {
    console.error('活動区分の更新に失敗しました:', error)
  }

  category.editing = false
}

function cancelEditCategory(category: any) {
  category.editing = false
  category.editName = category.name
}

function truncateCategoryName(name: string): string {
  return name.length > 15 ? name.substring(0, 15) + '...' : name
}
</script>

<style scoped>
.activity-categories {
  width: 90%;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  height: fit-content;
}

.category-list {
  margin-bottom: 20px;
}

.category-item {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 6px;
}

.category-content {
  flex: 1;
  min-width: 0;
}

.category-name {
  cursor: pointer;
  padding: 1px 3px;
  border-radius: 3px;
  transition: background-color 0.2s;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.category-name:hover {
  background-color: #e0e0e0;
}

.edit-category {
  flex: 1;
}

.edit-input {
  width: 100%;
  padding: 2px 4px;
  border: 1px solid #2196f3;
  border-radius: 3px;
  font-size: inherit;
}

.delete-btn {
  background: none;
  color: #666;
  border: none;
  width: 20px;
  height: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  padding: 0;
  min-width: 20px;
  min-height: 20px;
}

.delete-btn:hover {
  color: #ff4444;
}

.delete-btn svg {
  width: 16px;
  height: 16px;
}

.add-category {
  display: flex;
  gap: 8px;
}

.add-category input {
  flex: 1;
  padding: 3px 6px;
  font-size: 0.9em;
}

.add-category button {
  padding: 4px 8px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style> 