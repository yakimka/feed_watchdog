<template>
  <v-app-bar
      color="primary"
      density="compact"
  >
    <template v-slot:prepend>
      <v-app-bar-nav-icon @click.stop="navigation.toggleLeftSideBar()"></v-app-bar-nav-icon>
    </template>

    <v-app-bar-title>{{ title }}</v-app-bar-title>

    <template v-slot:append>
      <v-btn icon="mdi-dots-vertical"></v-btn>
    </template>
  </v-app-bar>
</template>

<script lang="ts" setup>
import { navigation } from '@/stores/navigation'
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
