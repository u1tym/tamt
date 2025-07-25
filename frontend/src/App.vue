<script setup lang="ts">
import { ref } from 'vue'
import PaymentSourceList from './components/PaymentSourceList.vue'
import TransactionList from './components/TransactionList.vue'

const currentTab = ref<'payment' | 'transaction'>('payment')
</script>

<template>
  <div>
    <h1>出納管理アプリ</h1>
    <div style="margin-bottom: 1em;">
      <button @click="currentTab = 'payment'" :disabled="currentTab === 'payment'">支出元管理</button>
      <button @click="currentTab = 'transaction'" :disabled="currentTab === 'transaction'">取引管理</button>
    </div>
    <PaymentSourceList v-if="currentTab === 'payment'" />
    <TransactionList v-else />
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
