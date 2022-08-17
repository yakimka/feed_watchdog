import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import CreateSource from '@/views/source/CreateSource.vue'

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
      title: 'Home'
    },
    component: Home
  },
  {
    path: '/sources/create',
    name: 'create-source',
    meta: {
      title: 'Create Source'
    },
    component: CreateSource
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
