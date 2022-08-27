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
      const result = []
      for (const item of this.$route.meta.breadcrumbs || []) {
        result.push(this.breadcrumbAttrs(item))
      }
      return result
    }
  },
  methods: {
    breadcrumbAttrs (item: Breadcrumb): Breadcrumb {
      const result = {
        text: item.text,
        replace: false
      } as Breadcrumb
      if (!item.to && !item.href) {
        result.href = '#'
        result.disabled = true
      }
      if ('to' in item) {
        // TODO copy `to`, delete `href`
        result.href = this.$router.resolve(item.to || {}).path
        result.disabled = false
      }
      if ('disabled' in item) {
        result.disabled = item.disabled
      }
      return result
    }
  }
})
</script>
