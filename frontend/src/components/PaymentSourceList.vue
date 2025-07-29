<template>
  <div>
    <h2>支出元一覧</h2>
    <ul>
      <li v-for="source in paymentSources" :key="source.id">
        {{ source.name }}（締め日: {{ source.closing_day }}日, 支払い月差分: {{ source.pay_month_diff }}, 支払い日: {{ source.pay_day }}日）
      </li>
    </ul>
    <h3>新規支出元登録</h3>
    <form @submit.prevent="addPaymentSource">
      <div>
        <label>名称: <input v-model="form.name" required /></label>
      </div>
      <div>
        <label>締め日: <input type="number" v-model.number="form.closing_day" min="0" max="31" required /></label>
      </div>
      <div>
        <label>支払い月までの差分: <input type="number" v-model.number="form.pay_month_diff" min="0" required /></label>
      </div>
      <div>
        <label>支払い日: <input type="number" v-model.number="form.pay_day" min="0" max="31" required /></label>
      </div>
      <button type="submit">登録</button>
    </form>
    <div v-if="error" style="color:red">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { buildApiUrl } from '../utils/api'

interface PaymentSource {
  id: number
  name: string
  closing_day: number
  pay_month_diff: number
  pay_day: number
}

const paymentSources = ref<PaymentSource[]>([])
const error = ref('')

const form = ref({
  name: '',
  closing_day: 0,
  pay_month_diff: 0,
  pay_day: 0,
})

const fetchPaymentSources = async () => {
  try {
    const res = await fetch(buildApiUrl('/payment_sources'))
    if (!res.ok) throw new Error('支出元取得に失敗しました')
    paymentSources.value = await res.json()
  } catch (e: any) {
    error.value = e.message
  }
}

const addPaymentSource = async () => {
  error.value = ''
  try {
    const res = await fetch(buildApiUrl('/payment_sources'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.value.name,
        closing_day: form.value.closing_day,
        pay_month_diff: form.value.pay_month_diff,
        pay_day: form.value.pay_day
      }),
    })
    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(`登録に失敗しました: ${errorData.detail || '不明なエラー'}`)
    }
    // フォームをリセット
    form.value = {
      name: '',
      closing_day: 0,
      pay_month_diff: 0,
      pay_day: 0,
    }
    await fetchPaymentSources()
  } catch (e: any) {
    error.value = e.message
  }
}

onMounted(fetchPaymentSources)
</script>