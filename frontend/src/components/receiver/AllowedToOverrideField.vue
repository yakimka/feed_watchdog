<template>
  <v-select
    multiple
    v-bind="$attrs"
    v-model="values[props.followValue]"
    :items="items"
    item-title="text"
    item-value="value"
    label="Options allowed to override"
  ></v-select>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, computed, reactive, watch, defineEmits } from 'vue'

interface Schema {
  [key: string]: {
    properties: {
      [key: string]: { title: string }
    }
  }
}
interface Props {
  modelValue: string[]
  schema: Schema
  followValue: string
}

const props = withDefaults(defineProps<Props>(), {})

const emit = defineEmits(['update:modelValue'])

const values = reactive({} as Record<string, string[]>)

interface Item {
  text: string
  value: string
}

const items = computed((): Item[] => {
  if (!(props.followValue in props.schema)) {
    return []
  }
  const result = []
  for (const [key, value] of Object.entries(props.schema[props.followValue].properties)) {
    result.push({ text: value.title, value: key })
  }
  return result
})

watch(
  () => props.modelValue,
  (value) => {
    values[props.followValue] = value
  }
)
watch(
  () => props.followValue,
  (value) => {
    emit('update:modelValue', values[value] || [])
  }
)
watch(
  () => values,
  (value) => {
    emit('update:modelValue', value[props.followValue] || [])
  },
  { deep: true }
)
</script>
