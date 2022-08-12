import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import Page from '@/layouts/Page.vue';
import AppBar from '@/components/AppBar.vue';
import LeftSideBar from '@/components/LeftSideBar.vue';
import router from '@/router'

loadFonts()

createApp(App)
  .use(vuetify)
  .use(router)
  .component('page-layout', Page)
  .component('app-bar', AppBar)
  .component('left-side-bar', LeftSideBar)
  .mount('#app')
