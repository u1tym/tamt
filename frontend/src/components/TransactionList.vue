<template>
  <div>
    <h2>取引一覧</h2>
    <ul>
      <li v-for="tx in transactions" :key="tx.id">
        {{ tx.used_date }} | {{ tx.purpose }} | {{ tx.memo }} | {{ tx.amount }}円 | 支出元: {{ getPaymentSourceName(tx.payment_source_id) }} | 支払日: {{ tx.paid_date }}
      </li>
    </ul>
    <h3>新規取引登録</h3>
    <form @submit.prevent="addTransaction">
      <div>
        <label>使用日: <input type="date" v-model="form.used_date" required /></label>
      </div>
      <div>
        <label>用途: <input v-model="form.purpose" required /></label>
      </div>
      <div>
        <label>メモ: <input v-model="form.memo" /></label>
      </div>
      <div>
        <label>金額: <input type="number" v-model.number="form.amount" required /></label>
      </div>
      <div>
        <label>支出元:
          <select v-model.number="form.payment_source_id" required>
            <option v-for="source in paymentSources" :key="source.id" :value="source.id">
              {{ source.name }}
            </option>
          </select>
        </label>
      </div>
      <button type="submit">登録</button>
    </form>
    <div v-if="error" style="color:red">{{ error }}</div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'

interface Transaction {
  id: number
  used_date: string
  purpose: string
  memo: string
  amount: number
  payment_source_id: number
  paid_date: string
  created_at: string
  updated_at: string
}

interface PaymentSource {
  id: number
  name: string
}

const transactions = ref<Transaction[]>([])
const paymentSources = ref<PaymentSource[]>([])
const error = ref('')

const form = ref({
  used_date: '',
  purpose: '',
  memo: '',
  amount: 0,
  payment_source_id: 0,
})

const fetchTransactions = async () => {
  try {
    const res = await fetch('http://localhost:8000/transactions')
    if (!res.ok) throw new Error('取引取得に失敗しました')
    transactions.value = await res.json()
  } catch (e: any) {
    error.value = e.message
  }
}

const fetchPaymentSources = async () => {
  try {
    const res = await fetch('http://localhost:8000/payment_sources')
    if (!res.ok) throw new Error('支出元取得に失敗しました')
    paymentSources.value = await res.json()
    if (paymentSources.value.length > 0 && form.value.payment_source_id === 0) {
      form.value.payment_source_id = paymentSources.value[0].id
    }
  } catch (e: any) {
    error.value = e.message
  }
}

const getPaymentSourceName = (id: number) => {
  const source = paymentSources.value.find(s => s.id === id)
  return source ? source.name : `ID:${id}`
}

const addTransaction = async () => {
  error.value = ''
  try {
    const res = await fetch('http://localhost:8000/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    if (!res.ok) throw new Error('登録に失敗しました')
    form.value = { used_date: '', purpose: '', memo: '', amount: 0, payment_source_id: paymentSources.value[0]?.id || 0 }
    await fetchTransactions()
  } catch (e: any) {
    error.value = e.message
  }
}

onMounted(() => {
  fetchPaymentSources()
  fetchTransactions()
})
</script>