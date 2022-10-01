<template>
  <v-container>
      <div class="text-h2 mb-5">
        Edit {{ source.name || 'Source' }}
      </div>
  </v-container>
  <v-container>
    <v-form
        ref="form"
        lazy-validation
        @submit.prevent="submit($event)"
    >
      <v-alert v-if="formErrors.nonFieldError"
        class="mb-5"
        icon="mdi-fire"
        title="Error"
        variant="outlined"
        type="error"
      >
        {{ formErrors.nonFieldError }}
      </v-alert>
      <v-text-field
          v-model="source.name"
          :error-messages="formErrors.name"
          label="Name"
      ></v-text-field>
      <v-text-field
          v-model="source.slug"
          :error-messages="formErrors.slug"
          label="Slug"
      ></v-text-field>
      <v-select
          v-model="source.fetcherType"
          :error-messages="formErrors.fetcherType"
          :items="fetcherTypes"
          label="Fetcher Type"
      ></v-select>
      <json-field
          compact
          v-model="source.fetcherOptions"
          :saved-value="savedFetcherOptions"
          :error-messages="formErrors.fetcherOptions"
          name="Fetcher options"
          :follow-value="source.fetcherType"
          :json-schema-mapping="fetcherOptionsSchema"
      ></json-field>
      <v-select
          v-model="source.parserType"
          :error-messages="formErrors.parserType"
          :items="parserTypes"
          label="Fetcher Type"
      ></v-select>
      <json-field
          compact
          v-model="source.parserOptions"
          :saved-value="savedParserOptions"
          :error-messages="formErrors.parserOptions"
          name="Parser options"
          :follow-value="source.parserType"
          :json-schema-mapping="parserOptionsSchema"
      ></json-field>
      <v-textarea
        name="Description"
        label="Description"
        :auto-grow="true"
        v-model="source.description"
        :error-messages="formErrors.description"
      ></v-textarea>
      <v-combobox
        label="Tags"
        v-model="source.tags"
        :error-messages="formErrors.tags"
        :items="availableTags"
        multiple
        chips
      ></v-combobox>

      <v-btn
          id="save"
          class="mr-4"
          color="primary"
          type="submit"
      >
        Save
      </v-btn>
      <v-btn
          id="save-and-create-stream"
          class="mr-4"
          color="primary"
          type="submit"
      >
        Save and create stream
      </v-btn>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { defineProps, onMounted, computed, ref } from 'vue'
import useSources from '@/composables/useSources'
import JsonField from '@/components/JsonField.vue'
import { scrollToTop } from '@/utils/pageNavigation'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const {
  errors,
  source,
  fetcherTypes,
  fetcherOptionsSchema,
  parserTypes,
  parserOptionsSchema,
  availableTags,
  getSource,
  updateSource,
  getFetcherTypes,
  getFetcherOptionsSchema,
  getParserTypes,
  getParserOptionsSchema,
  getAvailableTags
} = useSources()

const savedFetcherOptions = ref('')
const savedParserOptions = ref('')

const updateSavedOptions = () => {
  savedFetcherOptions.value = source.value.fetcherOptions
  savedParserOptions.value = source.value.parserOptions
}

const form = ref(null)
onMounted(async () => {
  await getFetcherTypes()
  await getFetcherOptionsSchema()
  await getParserTypes()
  await getParserOptionsSchema()
  await getAvailableTags()
  await getSource(props.id)

  updateSavedOptions()
})

const formErrors = computed(() => {
  const result: { [key: string ]: string} = {}
  for (const error of errors.value) {
    if (!error.field) {
      result.nonFieldError = error.message
    } else {
      result[error.field] = error.message
    }
  }
  return result
})

const submit = async (event: any) => {
  if (!await isValid()) {
    scrollToTop()
    // TODO Add global error message?
    console.log('Form is not valid')
    return
  }

  await updateSource(event.submitter.id)
  updateSavedOptions()
}

const isValid = async () => {
  if (form.value) {
    const result = await form.value.validate()
    return result.valid
  }
  return false
}
</script>
