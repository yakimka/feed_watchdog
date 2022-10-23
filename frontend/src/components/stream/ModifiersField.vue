<template>
  <div>
    <v-divider class="mb-5"></v-divider>
    <v-card class="mb-5" v-for="(field, index) in values" :key="index">
      <v-toolbar density="compact">
        <v-toolbar-title>Modifier {{ index + 1 }}</v-toolbar-title>
        <template v-slot:append>
           <v-btn
              depressed
              @click.stop="deleteField(index)"
          >
            DELETE
          </v-btn>
        </template>
      </v-toolbar>
      <v-card-text>
        <v-select
          v-model="field.type"
          :items="types"
          label="Modifier Type"
          :rules="[required()]"
        ></v-select>
        <json-field
          compact
          v-model="field.options"
          :follow-value="field.type"
          :json-schema-mapping="JSON.parse(JSON.stringify(modifierOptionsSchema))"
          :saved-value="savedValue[index]?.options || ''"
          name="Modifier options"
        ></json-field>
      </v-card-text>
    </v-card>
    <div class="mb-5 text-right">
      <v-btn
         depressed
         @click.stop="addField"
        >
          Add Modifier
      </v-btn>
    </div>
    <v-divider class="mb-5"></v-divider>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, defineProps, withDefaults, defineEmits, watch } from 'vue'
import { required } from '@/validation'
import useStreams from '@/composables/useStreams'
import JsonField from '@/components/core/JsonField.vue'
import Modifier from '@/types/stream'

interface Props {
  modelValue: Modifier[]
  savedValue?: Modifier[]
}

const props = withDefaults(defineProps<Props>(), {})
const emit = defineEmits(['update:modelValue'])

const {
  modifierOptionsSchema,
  getModifierOptionsSchema
} = useStreams()

const values = ref<Modifier[]>(props.modelValue)

const addField = () => {
  values.value.push({ type: '', options: '{}' })
}

const deleteField = (index: number) => {
  values.value.splice(index, 1)
}

const types = computed(() => {
  const result = []
  for (const item in modifierOptionsSchema.value) {
    result.push(item)
  }
  return result
})

watch(() => props.modelValue,
  (value) => {
    values.value = value
  },
  { deep: true }
)
watch(() => values.value,
  (value) => {
    emit('update:modelValue', value)
  },
  { deep: true }
)

onMounted(async () => {
  await getModifierOptionsSchema()
})

</script>
