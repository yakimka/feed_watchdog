<template>
  <v-container>
      <div class="text-h2 mb-5">
        <slot name="header">
          {{ props.hasDelete ? 'Edit' : 'Create' }} {{ modelName }}
        </slot>
      </div>
  </v-container>
  <progress-container
    :is-loading="props.isLoading"
  >
    <v-form
        ref="form"
        lazy-validation
        @submit.prevent="onSubmit($event)"
    >
      <v-alert v-if="error"
        class="mb-5"
        icon="mdi-fire"
        title="Error"
        variant="outlined"
        type="error"
      >
        {{ error }}
      </v-alert>

      <slot name="formContent"></slot>

      <v-btn
          id="save"
          class="mr-4"
          color="primary"
          type="submit"
      >
        Save
      </v-btn>
      <slot name="appendButton"></slot>
      <v-dialog
        v-if="props.hasDelete"
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
          <v-card-text>Delete {{ modelName }}? </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="green darken-1"
              text
              @click="onDelete()"
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
import { defineEmits, defineProps, ref } from 'vue'
import ProgressContainer from '@/components/core/ProgressContainer.vue'

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  hasDelete: {
    type: Boolean,
    default: false
  },
  modelName: {
    type: String,
    required: true
  },
  error: {
    type: String,
    default: ''
  }
})
const form = ref(null)

const emit = defineEmits(['submit', 'delete'])

const deleteDialog = ref(false)

const onSubmit = async (event: any) => {
  emit('submit', event, form)
}

const onDelete = async () => {
  deleteDialog.value = false
  emit('delete')
}
</script>
