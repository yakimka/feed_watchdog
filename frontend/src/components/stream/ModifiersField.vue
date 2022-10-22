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
          :json-schema-mapping="modifierOptionsSchema"
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
import { computed, ref, onMounted } from 'vue'
import { required } from '@/validation'
import useStreams from '@/composables/useStreams'
import JsonField from '@/components/core/JsonField.vue'
import Modifier from '@/types/stream'

const values = ref<Modifier[]>([])

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

onMounted(async () => {
  await getModifierOptionsSchema()
})

const {
  modifierOptionsSchema,
  getModifierOptionsSchema
} = useStreams()

</script>
