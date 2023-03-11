<template>
  <v-container fluid>
    <div class="text-h2 mb-5">
      <slot name="header"></slot>
    </div>
  </v-container>
  <v-container fluid v-if="props.filters">
    <v-form
      ref="form"
      @input="onFiltersInput"
      @keydown.enter.prevent="onFiltersInput"
    >
      <slot name="filters"></slot>
    </v-form>
  </v-container>

  <progress-container
    :fluid="true"
    :is-loading="props.isLoading"
  >
    <v-table fixed-header>
      <slot name="tableContent"></slot>
    </v-table>
    <v-row>
      <v-col cols="10">
        <v-pagination
          v-model="props.pagination.page"
          :total-visible="10"
          :length="totalPages"
          class="mt-5"
        ></v-pagination>
      </v-col>
      <v-col cols="2">
        <v-select
          class="mt-5"
          v-model="props.pagination.pageSize"
          :items="[25, 50, 100]"
          variant="plain"
          label="Page Size"
        ></v-select>
      </v-col>
    </v-row>
  </progress-container>
</template>

<script lang="ts" setup>
/* eslint vue/no-mutating-props: 0 */
import { defineEmits, defineProps } from 'vue'
import { debounce } from '@/utils/debounce'
import ProgressContainer from '@/components/core/ProgressContainer.vue'

const props = defineProps({
  filters: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  totalPages: {
    type: Number,
    default: 1
  },
  pagination: {
    type: Object,
    default: () => ({
      page: 1,
      pageSize: 25
    })
  }
})

const emit = defineEmits(['filtersInput'])

const onFiltersInput = debounce(async () => {
  props.pagination.page = 1
  emit('filtersInput')
})
</script>
