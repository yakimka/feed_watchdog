<template>
  <admin-model-edit
    :model-name="source.name || 'Source'"
    :is-loading="formIsLoading"
    :has-delete="true"
    :error="formErrors.nonFieldError"
    @submit="submit"
    @delete="deleteSourceAndRedirect"
  >
    <template v-slot:formContent>
      <v-text-field
          v-model="source.name"
          :error-messages="formErrors.name"
          label="Name"
          :rules="[required()]"
      ></v-text-field>
      <v-text-field
          v-model="source.slug"
          :error-messages="formErrors.slug"
          label="Slug"
          :rules="[required()]"
      ></v-text-field>
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
    </template>
    <template v-slot:appendButton>
      <v-btn
          id="save-and-create-stream"
          class="mr-4"
          color="primary"
          type="submit"
      >
        Save and create stream
      </v-btn>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { defineProps, onMounted } from 'vue'
import useSources from '@/composables/useSources'
import useForm from '@/composables/useForm'
import { required } from '@/validation'
import { useRouter } from 'vue-router'
import JsonField from '@/components/core/JsonField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'

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
  savedFetcherOptions,
  savedParserOptions,
  getSource,
  updateSource,
  deleteSource,
  getFetcherOptionsSchema,
  getParserOptionsSchema,
  getAvailableTags,
  updateSavedOptions
} = useSources()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await updateSource(event.submitter.id)
})

const router = useRouter()

const deleteSourceAndRedirect = async () => {
  formIsLoading.value = true
  await deleteSource(source.value.slug)
  await router.push({ name: 'sources' })
}

onMounted(async () => {
  await getFetcherOptionsSchema()
  await getParserOptionsSchema()
  await getAvailableTags()
  await getSource(props.id)

  updateSavedOptions()
  formIsLoading.value = false
})
</script>
