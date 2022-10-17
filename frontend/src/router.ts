import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import CreateSourceForm from '@/components/source/CreateSourceForm.vue'
import UpdateSourceForm from '@/components/source/UpdateSourceForm.vue'
import ListSourceForm from '@/components/source/ListSourceForm.vue'
import Form404 from '@/components/admin/Form404.vue'

export interface Breadcrumb {
  text: string
  disabled?: boolean
  href?: string
  to?: object
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
          text: 'Home'
        }
      ]
    },
    component: Home
  },
  {
    path: '/sources',
    name: 'sources',
    meta: {
      title: 'Sources',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Sources'
        }
      ]
    },
    component: ListSourceForm
  },
  {
    path: '/sources/create',
    name: 'create-source',
    meta: {
      title: 'Create Source',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Sources',
          to: { name: 'sources' }
        },
        {
          text: 'Create'
        }
      ]
    },
    component: CreateSourceForm
  },
  {
    path: '/sources/:id/edit',
    name: 'edit-source',
    props: true,
    meta: {
      title: 'Edit Source',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Sources',
          to: { name: 'sources' }
        },
        {
          text: 'Edit'
        }
      ]
    },
    component: UpdateSourceForm
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    meta: {
      title: '404',
      breadcrumbs: []
    },
    component: Form404
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
