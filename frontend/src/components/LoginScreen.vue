<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="portal-title">PORTAL</h1>
      
      <div class="portal-icon">
        <img src="/images/PORTAL.jpg" alt="PORTAL" class="icon-image" />
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="input-group">
          <label for="username" class="input-label">ユーザー名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="input-field"
            placeholder="ユーザー名を入力してください"
            required
          />
        </div>
        
        <div class="input-group">
          <label for="password" class="input-label">パスワード</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="input-field"
            placeholder="パスワードを入力してください"
            required
          />
        </div>
        
        <button type="submit" class="login-button">
          LOGIN
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')

function handleLogin() {
  // 認証機能は後で実装予定
  // 現在はログインボタンを押すとトップメニューに遷移
  router.push('/menu')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.portal-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  letter-spacing: 2px;
}

.portal-icon {
  margin-bottom: 40px;
}

.icon-image {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid #8B4513;
  box-shadow: 0 8px 24px rgba(139, 69, 19, 0.3);
  transition: all 0.3s ease;
}

.icon-image:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 32px rgba(139, 69, 19, 0.4);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  text-align: left;
}

.input-label {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  margin-bottom: 4px;
}

.input-field {
  padding: 16px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.input-field:focus {
  outline: none;
  border-color: #8B4513;
  background: white;
  box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1);
}

.input-field::placeholder {
  color: #999;
}

.login-button {
  background: linear-gradient(135deg, #8B4513 0%, #A0522D 100%);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 16px;
  letter-spacing: 1px;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 69, 19, 0.3);
  background: linear-gradient(135deg, #A0522D 0%, #CD853F 100%);
}

.login-button:active {
  transform: translateY(0);
}

/* レスポンシブ対応 */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
  
  .portal-title {
    font-size: 2rem;
  }
  
  .icon-image {
    width: 100px;
    height: 100px;
  }
  
  .input-field {
    padding: 14px;
    font-size: 16px;
  }
  
  .login-button {
    padding: 14px 28px;
    font-size: 16px;
  }
}
</style> 