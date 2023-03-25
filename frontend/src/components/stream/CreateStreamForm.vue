<template>
  <admin-model-edit
    :model-name="stream.name || 'Stream'"
    :is-loading="formIsLoading"
    :error="formErrors.nonFieldError"
    @submit="submit"
  >
    <template v-slot:formContent>
      <ForeignField
        v-model="stream.sourceSlug"
        v-model:search="sourceSlugData.search"
        :items="sourceSlugData.items"
        :loading="sourceSlugData.isLoading"
        item-title="name"
        item-value="slug"
        label="Source"
        :error-messages="formErrors.sourceSlug"
        :rules="[required()]"
        router-name="edit-source"
      ></ForeignField>
      <ForeignField
        v-model="stream.receiverSlug"
        v-model:search="receiverSlugData.search"
        :items="receiverSlugData.items"
        :loading="receiverSlugData.isLoading"
        item-title="name"
        item-value="slug"
        label="Receiver"
        :error-messages="formErrors.receiverSlug"
        :rules="[required()]"
        router-name="edit-receiver"
      ></ForeignField>
      <slug-field
        :follow-value="fieldForSlugFollowing"
        v-model="stream.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></slug-field>
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
        :error-messages="formErrors.receiverOptionsOverride"
        :json-schema-mapping="overrideOptionsSchema"
        name="Override Receiver Options"
      ></json-field>
      <v-select
        v-model="selectedMessageTemplate"
        :items="messageTemplates"
        item-title="text"
        item-value="value"
        label="Message Templates"
        @update:modelValue="stream.messageTemplate = selectedMessageTemplate"
      ></v-select>
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
      ></modifiers-field>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import useStreams from '@/composables/useStreams'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import useURL from '@/composables/useURL'
import JsonField from '@/components/core/JsonField.vue'
import ForeignField from '@/components/core/ForeignField.vue'
import SlugField from '@/components/core/SlugField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import ModifiersField from '@/components/stream/ModifiersField.vue'

const {
  errors,
  stream,
  sourceSlugData,
  receiverSlugData,
  overrideOptionsSchema,
  intervalTypes,
  selectedMessageTemplate,
  messageTemplates,
  storeStream,
  searchSource,
  searchReceiver,
  getIntervalTypes,
  getMessageTemplates
} = useStreams()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await storeStream(event.submitter.id)
})

const { getParamsFromURL } = useURL()

const fieldForSlugFollowing = computed(() => {
  if (!stream.value.sourceSlug && !stream.value.receiverSlug) {
    return ''
  }
  return `${stream.value.sourceSlug || ''} to ${stream.value.receiverSlug || ''}`
})

onMounted(async () => {
  formIsLoading.value = false
  await getMessageTemplates()
  await getIntervalTypes()
  const params = getParamsFromURL()
  const sourceSlug = (params.source || '').toString()
  if (sourceSlug) {
    stream.value.sourceSlug = sourceSlug
  }
  await searchSource(sourceSlug)
  await searchReceiver()
})
</script>
