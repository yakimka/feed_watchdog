import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'

declare module 'vue-router' {
  interface RouteMeta {
    title: string
  }
}

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    meta: {
      title: 'Главная страница'
    },
    component: Home
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
