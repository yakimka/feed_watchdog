<template>
  <div>
    <app-bar></app-bar>
    <left-side-bar></left-side-bar>
    <v-main>
      <v-breadcrumbs :items="breadcrumbs">
        <template v-slot:divider>
          <v-icon icon="mdi-chevron-right"></v-icon>
        </template>
      </v-breadcrumbs>
      <slot/>
    </v-main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import AppBar from '@/components/AppBar.vue'
import LeftSideBar from '@/components/LeftSideBar.vue'
import { Breadcrumb } from '@/router'

export default defineComponent({
  components: { AppBar, LeftSideBar },
  computed: {
    breadcrumbs (): Breadcrumb[] {
      return this.$route.meta.breadcrumbs || []
    }
  }
})
</script>
