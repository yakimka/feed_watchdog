import { createRouter, createWebHistory, RouteLocationNormalized, RouteRecordRaw } from 'vue-router'
import Home from '@/views/Home.vue'
import Login from '@/components/admin/Login.vue'
import CreateSourceForm from '@/components/source/CreateSourceForm.vue'
import UpdateSourceForm from '@/components/source/UpdateSourceForm.vue'
import ListSourceForm from '@/components/source/ListSourceForm.vue'
import CreateReceiverForm from '@/components/receiver/CreateReceiverForm.vue'
import UpdateReceiverForm from '@/components/receiver/UpdateReceiverForm.vue'
import ListReceiverForm from '@/components/receiver/ListReceiverForm.vue'
import CreateStreamForm from '@/components/stream/CreateStreamForm.vue'
import UpdateStreamForm from '@/components/stream/UpdateStreamForm.vue'
import ListStreamForm from '@/components/stream/ListStreamForm.vue'
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
    path: '/login',
    name: 'login',
    meta: {
      layout: 'empty',
      title: 'Login',
      breadcrumbs: []
    },
    component: Login
  },
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
    path: '/receivers',
    name: 'receivers',
    meta: {
      title: 'Receivers',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Receivers'
        }
      ]
    },
    component: ListReceiverForm
  },
  {
    path: '/receivers/create',
    name: 'create-receiver',
    meta: {
      title: 'Create Receiver',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Receivers',
          to: { name: 'receivers' }
        },
        {
          text: 'Create'
        }
      ]
    },
    component: CreateReceiverForm
  },
  {
    path: '/receivers/:id/edit',
    name: 'edit-receiver',
    props: true,
    meta: {
      title: 'Edit Receiver',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Receivers',
          to: { name: 'receivers' }
        },
        {
          text: 'Edit'
        }
      ]
    },
    component: UpdateReceiverForm
  },
  {
    path: '/streams',
    name: 'streams',
    meta: {
      title: 'Streams',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Streams'
        }
      ]
    },
    component: ListStreamForm
  },
  {
    path: '/streams/create',
    name: 'create-stream',
    meta: {
      title: 'Create Stream',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Streams',
          to: { name: 'streams' }
        },
        {
          text: 'Create'
        }
      ]
    },
    component: CreateStreamForm
  },
  {
    path: '/streams/:id/edit',
    name: 'edit-stream',
    props: true,
    meta: {
      title: 'Edit Stream',
      breadcrumbs: [
        {
          text: 'Home',
          to: { name: 'home' }
        },
        {
          text: 'Streams',
          to: { name: 'streams' }
        },
        {
          text: 'Edit'
        }
      ]
    },
    component: UpdateStreamForm
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

const guardAuth = function (to: RouteLocationNormalized) {
  if (to.name === 'login') {
    return
  }

  const token = localStorage.getItem('accesst')
  if (!token) {
    router.push({ name: 'login' })
  }
}

router.beforeEach(async (to) => {
  document.title = `${to.meta.title} | Feed Watchdog Admin`
  guardAuth(to)
})

export default router
