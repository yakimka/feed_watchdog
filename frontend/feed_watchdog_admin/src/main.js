import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import Admin from '@/layouts/Admin.vue';
import router from '@/router';

loadFonts()

createApp(App)
  .use(vuetify)
  .use(router)
  .component('admin-layout', Admin)
  .mount('#app')
