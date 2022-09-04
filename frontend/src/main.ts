import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Admin from './layouts/Admin.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import axios from 'axios'

axios.defaults.baseURL = 'http://localhost:8000/api'

loadFonts()

createApp(App)
  .use(router)
  .use(vuetify)
  .component('admin-layout', Admin)
  .mount('#app')
