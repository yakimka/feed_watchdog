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
        @blur="onFocus(false)"
        @focus="onFocus(true)"
        v-model="stream.sourceSlug"
        v-model:search="sourceSlugData.search"
        :items="sourceSlugData.items"
        :loading="sourceSlugData.isLoading"
        hide-selected
        item-title="name"
        item-value="slug"
        label="Source"
        placeholder="Start typing to Search"
        :error-messages="formErrors.sourceSlug"
        :rules="[required()]"
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
import { onMounted, reactive, ref, watch } from 'vue'
import useStreams from '@/composables/useStreams'
import useSources from '@/composables/useSources'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import Source from '@/types/source'
import JsonField from '@/components/core/JsonField.vue'
import SlugField from '@/components/core/SlugField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import { debounce } from '@/utils/debounce'

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

const sourceSlugData = reactive({
  search: '',
  items: [] as Source[],
  isLoading: false,
  cache: {} as Record<string, Source[]>,
  focused: false
})

const { sources, getSources } = useSources()

const searchSource = async (value = '') => {
  if (value in sourceSlugData.cache) {
    sourceSlugData.items = sourceSlugData.cache[value]
    console.log(456)
    return
  }

  sourceSlugData.isLoading = true
  await getSources(value, 1, 10)
  sourceSlugData.items = sources.value.results
  sourceSlugData.cache[value] = sources.value.results
  sourceSlugData.isLoading = false
}

const onFocus = async (value: boolean) => {
  sourceSlugData.focused = value
}

watch(
  () => sourceSlugData.search,
  debounce(async (value: string) => {
    console.log(901)
    // this fucking autocomplete component is so fucking stupid
    // it set the value of search to empty string when it loses focus
    // so we need to check if it's focused before sending the request
    if (value === '' && !sourceSlugData.focused) {
      console.log(123)
      return
    }
    await searchSource(value)
  })
)

const savedFetcherOptions = ref('')
const savedParserOptions = ref('')

const updateSavedOptions = () => {
  savedFetcherOptions.value = stream.value.fetcherOptions
  savedParserOptions.value = stream.value.parserOptions
}

onMounted(async () => {
  updateSavedOptions()
  formIsLoading.value = false

  await searchSource()
})
</script>
