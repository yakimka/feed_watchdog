<template>
  <admin-model-edit
    :model-name="receiver.name || 'Receiver'"
    :is-loading="formIsLoading"
    :has-delete="true"
    :error="formErrors.nonFieldError"
    @submit="submit"
    @delete="deleteReceiverAndRedirect"
  >
    <template v-slot:formContent>
      <v-text-field
          v-model="receiver.name"
          :error-messages="formErrors.name"
          label="Name"
          :rules="[required()]"
      ></v-text-field>
      <v-text-field
          v-model="receiver.slug"
          :error-messages="formErrors.slug"
          label="Slug"
          :rules="[required()]"
      ></v-text-field>
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
      <allowed-to-override-field
        v-model="receiver.optionsAllowedToOverride"
        :error-messages="formErrors.options"
        :schema="receiverOptionsSchema"
        :follow-value="receiver.type || ''"
      ></allowed-to-override-field>
    </template>
  </admin-model-edit>
</template>

<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue'
import useReceivers from '@/composables/useReceivers'
import useForm from '@/composables/useForm'
import { required } from '@/validation'
import { useRouter } from 'vue-router'
import JsonField from '@/components/core/JsonField.vue'
import AdminModelEdit from '@/components/core/AdminModelEdit.vue'
import AllowedToOverrideField from '@/components/receiver/AllowedToOverrideField.vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const {
  errors,
  receiver,
  receiverTypes,
  receiverOptionsSchema,
  getReceiver,
  updateReceiver,
  deleteReceiver,
  getReceiverOptionsSchema
} = useReceivers()

const {
  formErrors,
  formIsLoading,
  submit
} = useForm(errors, async (event) => {
  await updateReceiver(event.submitter.id)
  updateSavedOptions()
})

const savedReceiverOptions = ref('')

const router = useRouter()

const updateSavedOptions = () => {
  savedReceiverOptions.value = receiver.value.options
}

const deleteReceiverAndRedirect = async () => {
  formIsLoading.value = true
  await deleteReceiver(receiver.value.slug)
  await router.push({ name: 'receivers' })
}

onMounted(async () => {
  await getReceiverOptionsSchema()
  await getReceiver(props.id)

  updateSavedOptions()
  formIsLoading.value = false
})
</script>
