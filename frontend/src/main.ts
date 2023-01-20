import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Admin from './layouts/Admin.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import axios from 'axios'
import { dialog } from '@/stores/dialog'
import { logout } from '@/auth'

axios.defaults.baseURL = 'http://localhost:8000/api'
// TODO 404 and move to error.ts
axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  const { config, response: { status } } = error

  if (status === 401) {
    const refrestToken = localStorage.getItem('refresht')
    if (refrestToken) {
      const headersConf = {
        headers: {
          Authorization: `Bearer ${refrestToken}`
        }
      }
      axios.post('/user/refresh_token/', {}, headersConf).then(r => {
        localStorage.setItem('accesst', r.data.access_token)
        config.headers.Authorization = `Bearer ${r.data.access_toke}`
        return axios.request(config)
      }).catch(() => {
        logout()
      })
    } else {
      logout()
    }
  }

  if (status === 0 || status >= 500) {
    dialog.set(error.message, 'Something went wrong')
  }
  return Promise.reject(error)
})

const noAuthPaths = [
  '/user/login',
  '/user/refresh_token'
]
axios.interceptors.request.use(function (config: any) {
  const path = config.url.replace(/\/$/, '')
  if (noAuthPaths.includes(path)) {
    return config
  }

  const token = localStorage.getItem('accesst')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .component('admin-layout', Admin)
  .mount('#app')
