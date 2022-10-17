<template>
  <v-progress-linear v-if="props.isLoading"
    indeterminate
    color="primary"
  ></v-progress-linear>

  <v-container style="position: relative" :fluid="props.fluid">
    <v-overlay
      :model-value="props.isLoading"
      contained
      persistent
    ></v-overlay>

    <slot></slot>

  </v-container>
</template>

<script lang="ts" setup>
import { defineProps } from 'vue'

const props = defineProps({
  fluid: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})
</script>
