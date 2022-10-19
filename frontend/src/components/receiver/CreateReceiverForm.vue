<template>
  <admin-model-edit
    :model-name="receiver.name || 'Receiver'"
    :is-loading="formIsLoading"
    :error="formErrors.nonFieldError"
    @submit="submit"
  >
    <template v-slot:formContent>
      <v-text-field
          v-model="receiver.name"
          :error-messages="formErrors.name"
          label="Name"
          :rules="[required()]"
      ></v-text-field>
      <slug-field
        :follow-value="receiver.name || ''"
        v-model="receiver.slug"
        :error-messages="formErrors.slug"
        label="Slug"
        :rules="[required()]"
      ></slug-field>
      <v-select
          v-model="receiver.type"
          :error-messages="formErrors.type"
          :items="receiverTypes"
          label="Receiver Type"
          :rules="[required()]"
      ></v-select>
      <json-field
          compact
          v-model="receiver.options"
          :saved-value="savedReceiverOptions"
          :error-messages="formErrors.options"
          name="Receiver options"
          :follow-value="receiver.type"
          :json-schema-mapping="receiverOptionsSchema"
      ></json-field>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import useReceivers from '@/composables/useReceivers'
import { required } from '@/validation'
import useForm from '@/composables/useForm'
import JsonField from '@/components/core/JsonField.vue'
import SlugField from '@/components/core/SlugField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'

const {
  errors,
  receiver,
  receiverTypes,
  receiverOptionsSchema,
  storeReceiver,
  getReceiverOptionsSchema
} = useReceivers()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await storeReceiver(event.submitter.id)
  updateSavedOptions()
})

const savedReceiverOptions = ref('')

const updateSavedOptions = () => {
  savedReceiverOptions.value = receiver.value.options
}

onMounted(async () => {
  await getReceiverOptionsSchema()
  updateSavedOptions()
  formIsLoading.value = false
})
</script>
