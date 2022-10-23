<template>
  <admin-model-edit
    model-name="Stream"
    :has-delete="true"
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
      <v-text-field
        v-model="stream.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></v-text-field>
      <v-select
        multiple
        v-model="stream.intervals"
        :error-messages="formErrors.intervals"
        :items="intervalTypes"
        item-title="text"
        item-value="value"
        label="Intervals"
        :rules="[required()]"
      ></v-select>
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
      <v-checkbox
        v-model="stream.active"
        :error-messages="formErrors.active"
        label="Active"
      ></v-checkbox>
      <modifiers-field
        v-model="stream.modifiers"
        :saved-value="savedModifiers"
      ></modifiers-field>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { defineProps, onMounted } from 'vue'
import useStreams from '@/composables/useStreams'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import JsonField from '@/components/core/JsonField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import ModifiersField from '@/components/stream/ModifiersField.vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const {
  errors,
  stream,
  sourceSlugData,
  receiverSlugData,
  overrideOptionsSchema,
  savedReceiverOptionsOverride,
  savedModifiers,
  intervalTypes,
  getStream,
  updateStream,
  searchSource,
  searchReceiver,
  setFocus,
  updateSavedOptions,
  getIntervalTypes
} = useStreams()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await updateStream(event.submitter.id)
})

onMounted(async () => {
  await searchSource()
  await searchReceiver()
  await getIntervalTypes()
  await getStream(props.id)

  updateSavedOptions()
  formIsLoading.value = false
})
</script>
