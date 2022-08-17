import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import CreateSource from '@/views/source/CreateSource.vue'

export interface Breadcrumb {
  text: string
  disabled?: boolean
  href: string
}

declare module 'vue-router' {
  interface RouteMeta {
    title: string
    breadcrumbs?: Breadcrumb[]
  }
}

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'home',
    meta: {
      title: 'Home',
      breadcrumbs: [
        {
          text: 'Home',
          href: '/',
          disabled: true
        }
      ]
    },
    component: Home
  },
  {
    path: '/sources/create',
    name: 'create-source',
    meta: {
      title: 'Create Source',
      breadcrumbs: [
        {
          text: 'Home',
          href: '/',
          disabled: false
        },
        {
          text: 'Sources',
          href: '/sources',
          disabled: false
        },
        {
          text: 'Create',
          href: '/sources/create',
          disabled: true
        }
      ]
    },
    component: CreateSource
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
