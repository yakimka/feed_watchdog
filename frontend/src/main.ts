import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Admin from './layouts/Admin.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import axios from 'axios'
import { dialog } from '@/stores/dialog'

axios.defaults.baseURL = 'http://localhost:8000/api'
// TODO 404 and move to error.ts
axios.interceptors.response.use(function (response) {
  return response
}, function (error) {
  if (error.request.status === 0 || error.request.status >= 500) {
    dialog.set(error.message, 'Something went wrong')
  }
  return Promise.reject(error)
})

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .component('admin-layout', Admin)
  .mount('#app')
