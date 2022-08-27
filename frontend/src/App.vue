<template>
  <v-app>
    <component :is="layout">
      <router-view/>
    </component>
  </v-app>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

const DEFAULT_LAYOUT = 'admin'

export default defineComponent({
  name: 'App',

  computed: {
    layout (): string {
      return (this.$route.meta.layout || DEFAULT_LAYOUT) + '-layout'
    }
  }
})
</script>
