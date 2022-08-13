<template>
  <v-container>
    <v-form
        ref="form"
        v-model="valid"
        lazy-validation
    >
      <v-text-field
          v-model="fields.name.value"
          :counter="10"
          :rules="rules.name"
          :error-messages="fields.name.error"
          @input="clearError('name')"
          label="Name"
      ></v-text-field>

      <v-text-field
          v-model="fields.email.value"
          :rules="rules.email"
          :error-messages="fields.email.error"
          @input="clearError('email')"
          label="E-mail"
      ></v-text-field>
      <json-field></json-field>
      <v-select
          v-model="fields.item.value"
          :items="fields.item.values"
          :rules="rules.item"
          :error-messages="fields.item.error"
          @input="clearError('item')"
          label="Item"
      ></v-select>

      <v-btn
          :disabled="!valid"
          class="mr-4"
          color="success"
          @click="submit"
      >
        Submit
      </v-btn>

    </v-form>
  </v-container>
</template>

<script>
import {required, maxTextLength, email} from "@/validation";
import JsonField from "@/components/JsonField";

export default {
  components: {JsonField},
  data: () => ({
    valid: true,
    rules: {
      name: [
        required(),
        maxTextLength(10),
      ],
      email: [
        required(),
        email(),
      ],
      item: []
    },
    fields: {
      name: {
        value: '',
        error: '',
      },
      email: {
        value: '',
        error: '',
      },
      item: {
        value: null,
        error: '',
        values: [
          'Item 1',
          'Item 2',
          'Item 3',
          'Item 4',
        ]
      },
    }
  }),

  methods: {
    submit() {
      this.validate();
      if (this.valid) {
        alert("Submitted");
        this.fields.name.error = 'Wrong Name!';
      }
    },
    clearError(field) {
      if (this.fields[field].error) {
        this.fields[field].error = '';
      }
    },
    validate() {
      this.$refs.form.validate()
    },
    reset() {
      this.$refs.form.reset()
    },
    resetValidation() {
      this.$refs.form.resetValidation()
    },
  },
}
</script>
