<template>
  <v-app-bar
      color="primary"
      density="compact"
  >
    <template v-slot:prepend>
      <v-app-bar-nav-icon @click.stop="navigation.toggleLeftSideBar()"></v-app-bar-nav-icon>
    </template>

    <v-app-bar-title>{{ title }}</v-app-bar-title>

    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
      </template>

      <v-list>
        <v-list-item>
          <v-btn @click="logout()">Logout</v-btn>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { navigation } from '@/stores/navigation'
import { logout } from '@/auth'
</script>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'AppBar',

  data: () => ({}),
  computed: {
    title (): string {
      return (this.$route.meta.title || '')
    }
  }
})
</script>
