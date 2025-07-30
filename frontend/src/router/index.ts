import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'TopMenu',
    component: () => import('../components/TopMenu.vue'),
  },
  {
    path: '/transactions',
    name: 'Transactions',
    component: () => import('../components/CashManagement.vue'),
  },
  {
    path: '/knowhow',
    name: 'Knowhow',
    component: () => import('../components/KnowhowManagement.vue'),
  },
  {
    path: '/goods',
    name: 'Goods',
    component: () => import('../components/UnderConstruction.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router