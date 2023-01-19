<template>
  <div>
    <Dialog></Dialog>

    <v-main>
      <slot />
    </v-main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import Dialog from '@/components/admin/Dialog.vue'

export default defineComponent({
  components: { Dialog }
})
</script>
