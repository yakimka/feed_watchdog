import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Admin from './layouts/Admin.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import axios from 'axios'
import createAuthRefreshInterceptor from 'axios-auth-refresh'
import { dialog } from '@/stores/dialog'
import { logout } from '@/auth'
import config from '@/config'

axios.defaults.baseURL = config.VUE_APP_ROOT_API
// TODO 404 and move to error.ts
const refreshAuthLogic = (failedRequest: any): Promise<any> => {
  const refreshToken = localStorage.getItem('refresht')
  if (!refreshToken) {
    logout()
    return Promise.resolve()
  }

  const headersConf = {
    headers: {
      Authorization: `Bearer ${refreshToken}`
    }
  }
  return axios.post('/user/refresh_token/', {}, headersConf).then(r => {
    localStorage.setItem('accesst', r.data.access_token)
    failedRequest.response.config.headers.Authorization = `Bearer ${r.data.access_token}`
    return Promise.resolve()
  }).catch(() => {
    logout()
  })
}
createAuthRefreshInterceptor(axios, refreshAuthLogic, { statusCodes: [401, 403] })

axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  const { response: { status } } = error

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
