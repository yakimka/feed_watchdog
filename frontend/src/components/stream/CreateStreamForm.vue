<template>
  <admin-model-edit
    :model-name="stream.name || 'Stream'"
    :is-loading="formIsLoading"
    :error="formErrors.nonFieldError"
    @submit="submit"
  >
    <template v-slot:formContent>
      <slug-field
        :follow-value="'some'"
        v-model="stream.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></slug-field>

      <v-autocomplete
        v-model="stream.sourceSlug"
        v-model:search="search"
        :items="items"
        :loading="isLoading"
        hide-no-data
        hide-selected
        item-title="Description"
        item-value="API"
        label="Source slug"
        placeholder="Start typing to Search"
        return-object
      ></v-autocomplete>

      <v-textarea
        name="Description"
        label="Description"
        :auto-grow="true"
        v-model="stream.description"
        :error-messages="formErrors.description"
      ></v-textarea>
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
import { onMounted, ref } from 'vue'
import useStreams from '@/composables/useStreams'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import JsonField from '@/components/core/JsonField.vue'
import SlugField from '@/components/core/SlugField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'

const {
  errors,
  stream,
  storeStream
} = useStreams()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await storeStream(event.submitter.id)
  updateSavedOptions()
})

const savedFetcherOptions = ref('')
const savedParserOptions = ref('')

const updateSavedOptions = () => {
  savedFetcherOptions.value = stream.value.fetcherOptions
  savedParserOptions.value = stream.value.parserOptions
}

onMounted(async () => {
  updateSavedOptions()
  formIsLoading.value = false
})
</script>
