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
    component: () => import('../components/cash/CashManagement.vue'),
  },
  {
    path: '/knowhow',
    name: 'Knowhow',
    component: () => import('../components/knowhow/KnowhowManagement.vue'),
  },
  {
    path: '/goods',
    name: 'Goods',
    component: () => import('../components/goods/GoodsManagement.vue'),
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../components/schedule/ScheduleManagement.vue'),
  },
  {
    path: '/holidays',
    name: 'Holidays',
          component: () => import('../components/holiday/HolidayManagement.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router