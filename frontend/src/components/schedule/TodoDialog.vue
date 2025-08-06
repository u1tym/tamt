<template>
  <div v-if="show" class="todo-dialog-overlay" @click="closeDialog">
    <div class="todo-dialog" @click.stop>
      <div class="todo-dialog-header">
        <h3>未実施のTODO一覧</h3>
        <button class="close-button" @click="closeDialog">×</button>
      </div>
      
      <div class="todo-dialog-content">
        <!-- 過去の未実施TODO -->
        <div v-if="pastTodos.length > 0" class="todo-section">
          <h4 class="todo-section-title">過去の未実施TODO</h4>
          <div class="todo-list">
            <div 
              v-for="todo in pastTodos" 
              :key="todo.id" 
              class="todo-item"
            >
              <label class="todo-checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="getTodoStatus(todo.id)" 
                  @change="toggleTodoStatus(todo.id)"
                  class="todo-checkbox-input"
                />
                <span class="todo-title">{{ todo.title }}</span>
              </label>
              <div class="todo-date">{{ formatDate(todo.start_datetime) }}</div>
            </div>
          </div>
        </div>

        <!-- 当日から3日以内の未実施TODO -->
        <div v-if="recentTodos.length > 0" class="todo-section">
          <h4 class="todo-section-title">当日から3日以内の未実施TODO</h4>
          <div class="todo-list">
            <div 
              v-for="todo in recentTodos" 
              :key="todo.id" 
              class="todo-item"
            >
              <label class="todo-checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="getTodoStatus(todo.id)" 
                  @change="toggleTodoStatus(todo.id)"
                  class="todo-checkbox-input"
                />
                <span class="todo-title">{{ todo.title }}</span>
              </label>
              <div class="todo-date">{{ formatDate(todo.start_datetime) }}</div>
            </div>
          </div>
        </div>

        <!-- TODOがない場合 -->
        <div v-if="pastTodos.length === 0 && recentTodos.length === 0" class="no-todos">
          未実施のTODOはありません
        </div>
      </div>

      <div class="todo-dialog-footer">
        <button class="update-button" @click="updateAllTodos" :disabled="!hasChanges">更新</button>
        <button class="close-dialog-button" @click="closeDialog">閉じる</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

// Props
interface Props {
  show: boolean
  schedules: any[]
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  updateTodo: [todo: any, isCompleted: boolean]
}>()

// ローカル状態管理
const todoStatusChanges = ref<Map<number, boolean>>(new Map())

// TODOを分類して取得
const pastTodos = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  return props.schedules
    .filter(schedule => 
      schedule.schedule_type === 'TODO' && 
      !schedule.is_todo_completed &&
      new Date(schedule.start_datetime) < today
    )
    .sort((a, b) => new Date(a.start_datetime).getTime() - new Date(b.start_datetime).getTime())
})

const recentTodos = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const threeDaysLater = new Date(today)
  threeDaysLater.setDate(today.getDate() + 3)
  
  return props.schedules
    .filter(schedule => 
      schedule.schedule_type === 'TODO' && 
      !schedule.is_todo_completed &&
      new Date(schedule.start_datetime) >= today &&
      new Date(schedule.start_datetime) <= threeDaysLater
    )
    .sort((a, b) => new Date(a.start_datetime).getTime() - new Date(b.start_datetime).getTime())
})

// 変更があるかどうかを判定
const hasChanges = computed(() => {
  return todoStatusChanges.value.size > 0
})

// メソッド
function closeDialog() {
  // ダイアログを閉じる際に変更をリセット
  todoStatusChanges.value.clear()
  emit('close')
}

function getTodoStatus(todoId: number): boolean {
  // 変更された状態があればそれを返す、なければ元の状態を返す
  if (todoStatusChanges.value.has(todoId)) {
    return todoStatusChanges.value.get(todoId)!
  }
  
  const todo = props.schedules.find(s => s.id === todoId)
  return todo ? todo.is_todo_completed : false
}

function toggleTodoStatus(todoId: number) {
  const currentStatus = getTodoStatus(todoId)
  todoStatusChanges.value.set(todoId, !currentStatus)
}

function updateAllTodos() {
  // 変更されたTODOを一括で更新
  todoStatusChanges.value.forEach((isCompleted, todoId) => {
    const todo = props.schedules.find(s => s.id === todoId)
    if (todo) {
      emit('updateTodo', todo, isCompleted)
    }
  })
  
  // 更新後に変更をリセット
  todoStatusChanges.value.clear()
}

function formatDate(datetime: string): string {
  const date = new Date(datetime)
  return date.toLocaleDateString('ja-JP', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    weekday: 'short'
  })
}
</script>

<style scoped>
.todo-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.todo-dialog {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.todo-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.todo-dialog-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
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
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #f0f0f0;
}

.todo-dialog-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.todo-section {
  margin-bottom: 24px;
}

.todo-section:last-child {
  margin-bottom: 0;
}

.todo-section-title {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 1rem;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e0e0;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #ff9800;
}

.todo-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex: 1;
}

.todo-checkbox-input {
  width: 18px;
  height: 18px;
  accent-color: #4CAF50;
  cursor: pointer;
}

.todo-title {
  font-weight: 500;
  color: #333;
  flex: 1;
}

.todo-date {
  font-size: 0.9rem;
  color: #666;
  margin-left: 12px;
}

.no-todos {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 40px 20px;
}

.todo-dialog-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.update-button {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.update-button:hover:not(:disabled) {
  background: #1976D2;
}

.update-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.close-dialog-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.close-dialog-button:hover {
  background: #45a049;
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .todo-dialog {
    width: 95%;
    max-height: 90vh;
  }
  
  .todo-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .todo-date {
    margin-left: 0;
    font-size: 0.8rem;
  }
}
</style> 