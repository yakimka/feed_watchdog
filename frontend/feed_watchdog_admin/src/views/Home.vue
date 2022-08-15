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
          :error-messages="fields.name.error"
          :rules="rules.name"
          label="Name"
          @input="clearError('name')"
      ></v-text-field>
      <v-select
          v-model="fields.item.value"
          :error-messages="fields.item.error"
          :items="fields.item.values"
          :rules="rules.item"
          label="Item"
          @input="clearError('item')"
      ></v-select>
      <json-field v-model="fields.options.value"
                  :follow-value="fields.item.value"
      ></json-field>

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
import {email, maxTextLength, required} from "@/validation";
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
      options: {
        value: '{"key": "value"}',
        error: '',
      },
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
          '@pydailybot',
          'compare_and_filter',
          'replace_text',
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
