<template>
  <v-container>
      <div class="text-h2 mb-5">
        Edit {{ source.name || 'Source' }}
      </div>
  </v-container>
  <progress-container
    :is-loading="formIsLoading"
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
      <v-dialog
        v-model="deleteDialog"
        max-width="290"
      >
        <template v-slot:activator="{ props }">
          <v-btn
              class="float-right"
              color="red"
              v-bind="props"
          >
            Delete
          </v-btn>
        </template>
        <v-card>
          <v-card-title class="text-h5">
            Are you sure?
          </v-card-title>
          <v-card-text>Delete {{ source.name }}? </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="green darken-1"
              text
              @click="deleteSourceAndRedirect()"
            >
              Yes
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-form>
  </progress-container>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue'
import useSources from '@/composables/useSources'
import useForm from '@/composables/useForm'
import { required } from '@/validation'
import { useRouter } from 'vue-router'
import JsonField from '@/components/core/JsonField.vue'
import ProgressContainer from '@/components/core/ProgressContainer.vue'

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
  deleteSource,
  getFetcherOptionsSchema,
  getParserOptionsSchema,
  getAvailableTags
} = useSources()

const {
  form,
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await updateSource(event.submitter.id)
  updateSavedOptions()
})

const deleteDialog = ref(false)
const savedFetcherOptions = ref('')
const savedParserOptions = ref('')

const router = useRouter()

const updateSavedOptions = () => {
  savedFetcherOptions.value = source.value.fetcherOptions
  savedParserOptions.value = source.value.parserOptions
}

const deleteSourceAndRedirect = async () => {
  formIsLoading.value = true
  deleteDialog.value = false
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
