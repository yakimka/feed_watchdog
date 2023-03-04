<template>
  <v-text-field
    v-bind="$attrs"
  ></v-text-field>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { slugify } from '@/utils/slug'

export default defineComponent({
  name: 'SlugField',
  props: {
    followValue: {
      type: String,
      required: true
    }
  },
  watch: {
    followValue (newValue, oldValue) {
      if (slugify(oldValue) === (this.$attrs.modelValue || '')) {
        this.$emit('update:modelValue', slugify(this.followValue))
      }
    }
  }
})
</script>
