<template>
  <v-container>
      <div class="text-h2 mb-5">
        Create new Source
      </div>
  </v-container>
  <progress-container
    :is-loading="pageIsLoading"
  >
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
          :rules="[required()]"
      ></v-text-field>
      <slug-field
        :follow-value="source.name || ''"
        v-model="source.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></slug-field>
      <v-select
          v-model="source.fetcherType"
          :error-messages="formErrors.fetcherType"
          :items="fetcherTypes"
          label="Fetcher Type"
          :rules="[required()]"
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
          label="Parser Type"
          :rules="[required()]"
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
  </progress-container>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import useSources from '@/composables/useSources'
import JsonField from '@/components/core/JsonField.vue'
import SlugField from '@/components/core/SlugField.vue'
import { scrollToTop } from '@/utils/pageNavigation'
import ProgressContainer from '@/components/core/ProgressContainer.vue'
import { required } from '@/validation'

const {
  errors,
  source,
  fetcherTypes,
  fetcherOptionsSchema,
  parserTypes,
  parserOptionsSchema,
  availableTags,
  storeSource,
  getFetcherOptionsSchema,
  getParserOptionsSchema,
  getAvailableTags
} = useSources()

const pageIsLoading = ref(true)
const savedFetcherOptions = ref('')
const savedParserOptions = ref('')

const updateSavedOptions = () => {
  savedFetcherOptions.value = source.value.fetcherOptions
  savedParserOptions.value = source.value.parserOptions
}

onMounted(async () => {
  await getFetcherOptionsSchema()
  await getParserOptionsSchema()
  await getAvailableTags()

  updateSavedOptions()
  pageIsLoading.value = false
})

const form = ref(null)

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
    return
  }

  pageIsLoading.value = true
  await storeSource(event.submitter.id)
  updateSavedOptions()
  pageIsLoading.value = false
}

const isValid = async () => {
  if (form.value) {
    const result = await form.value.validate()
    return result.valid
  }
  return false
}
</script>
