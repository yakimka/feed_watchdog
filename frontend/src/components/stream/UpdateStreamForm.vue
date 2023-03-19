<template>
  <admin-model-edit
    model-name="Stream"
    :has-delete="true"
    :is-loading="formIsLoading"
    :error="formErrors.nonFieldError"
    @submit="submit"
    @delete="deleteStreamAndRedirect"
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
      ></ForeignField>
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
import ForeignField from '@/components/core/ForeignField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import ModifiersField from '@/components/stream/ModifiersField.vue'
import { useRouter } from 'vue-router'

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
  deleteStream,
  searchSource,
  searchReceiver,
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

const router = useRouter()

const deleteStreamAndRedirect = async () => {
  formIsLoading.value = true
  await deleteStream(stream.value.slug)
  await router.push({ name: 'streams' })
}

onMounted(async () => {
  await getStream(props.id)
  await searchSource(stream.value.sourceSlug)
  await searchReceiver(stream.value.receiverSlug)
  await getIntervalTypes()
  // FIXME: This is a hack to get the saved values to show up in the JSON field
  await getStream(props.id)
  updateSavedOptions()
  formIsLoading.value = false
})
</script>
