<template>
  <admin-model-edit
    :model-name="stream.name || 'Stream'"
    :is-loading="formIsLoading"
    :error="formErrors.nonFieldError"
    @submit="submit"
  >
    <template v-slot:formContent>
      <v-autocomplete
        @blur="setFocus('source', false)"
        @focus="setFocus('source', true)"
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
      <v-autocomplete
        @blur="setFocus('receiver', false)"
        @focus="setFocus('receiver', true)"
        v-model="stream.receiverSlug"
        v-model:search="receiverSlugData.search"
        :items="receiverSlugData.items"
        :loading="receiverSlugData.isLoading"
        hide-selected
        item-title="name"
        item-value="slug"
        label="Receiver"
        placeholder="Start typing to Search"
        :error-messages="formErrors.receiverSlug"
        :rules="[required()]"
      ></v-autocomplete>
      <slug-field
        :follow-value="fieldForSlugFollowing"
        v-model="stream.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></slug-field>
      <v-checkbox
        v-model="stream.squash"
        :error-messages="formErrors.squash"
        label="Squash"
      ></v-checkbox>
      <json-field
        compact
        v-model="stream.receiverOptionsOverride"
        :saved-value="savedReceiverOptionsOverride"
        :error-messages="formErrors.receiverOptionsOverride"
        :json-schema-mapping="overrideOptionsSchema"
        name="Override Receiver Options"
      ></json-field>
      <v-textarea
        name="Message Template"
        label="Message Template"
        :auto-grow="true"
        v-model="stream.messageTemplate"
        :error-messages="formErrors.messageTemplate"
      ></v-textarea>
      <modifiers-field
      ></modifiers-field>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import useStreams from '@/composables/useStreams'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import JsonField from '@/components/core/JsonField.vue'
import SlugField from '@/components/core/SlugField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import ModifiersField from '@/components/stream/ModifiersField.vue'

const {
  errors,
  stream,
  sourceSlugData,
  receiverSlugData,
  overrideOptionsSchema,
  storeStream,
  searchSource,
  searchReceiver,
  setFocus
} = useStreams()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await storeStream(event.submitter.id)
  updateSavedOptions()
})

const savedReceiverOptionsOverride = ref('')

const updateSavedOptions = () => {
  savedReceiverOptionsOverride.value = stream.value.receiverOptionsOverride
}

const fieldForSlugFollowing = computed(() => {
  if (!stream.value.sourceSlug && !stream.value.receiverSlug) {
    return ''
  }
  return `${stream.value.sourceSlug || ''} to ${stream.value.receiverSlug || ''}`
})

onMounted(async () => {
  updateSavedOptions()
  formIsLoading.value = false

  await searchSource()
  await searchReceiver()
})
</script>
