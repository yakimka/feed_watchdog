<template>
  <v-container>
    <v-form
        ref="form"
        v-model="form.valid"
        lazy-validation
    >
      <div class="text-h2 mb-5">New Source</div>
      <v-text-field
          v-model="form.fields.name.value"
          :counter="10"
          :error-messages="form.fields.name.error"
          :rules="form.rules.name"
          label="Name"
          @input="clearError('name')"
      ></v-text-field>
      <v-text-field
          v-model="form.fields.slug.value"
          :counter="10"
          :error-messages="form.fields.slug.error"
          :rules="form.rules.slug"
          label="Slug"
          @input="clearError('slug')"
      ></v-text-field>
      <v-select
          v-model="form.fields.fetcherType.value"
          :error-messages="form.fields.fetcherType.error"
          :items="form.fields.fetcherType.values"
          :rules="form.rules.fetcherType"
          label="Fetcher Type"
          @input="clearError('fetcherType')"
      ></v-select>
      <json-field
          compact
          v-model="form.fields.fetcherOptions.value"
          name="Fetcher options"
          :follow-value="form.fields.fetcherType.value"
          :json-schema-mapping="form.fields.fetcherOptions.jsonSchemaMapping"
      ></json-field>
      <v-select
          v-model="form.fields.parserType.value"
          :error-messages="form.fields.parserType.error"
          :items="form.fields.parserType.values"
          :rules="form.rules.parserType"
          label="Fetcher Type"
          @input="clearError('parserType')"
      ></v-select>
      <json-field
          compact
          v-model="form.fields.parserOptions.value"
          name="Parser options"
          :follow-value="form.fields.parserType.value"
          :json-schema-mapping="form.fields.parserOptions.jsonSchemaMapping"
      ></json-field>
      <v-textarea
        name="Description"
        label="Description"
        :auto-grow="true"
        v-model="form.fields.description.value"
        :error-messages="form.fields.description.error"
        :rules="form.rules.description"
      ></v-textarea>
      <v-combobox
        label="Tags"
        v-model="form.fields.tags.value"
        :error-messages="form.fields.tags.error"
        :rules="form.rules.tags"
        :items="form.fields.tags.items"
        multiple
        chips
      ></v-combobox>

      <v-btn
          :disabled="!form.valid"
          class="mr-4"
          color="success"
          @click="submit"
      >
        Submit
      </v-btn>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { required } from '@/validation'
import JsonField from '@/components/JsonField.vue'

export default defineComponent({
  components: { JsonField },
  data: () => ({
    form: {
      valid: true,
      rules: {
        name: [
          required()
        ],
        slug: [
          required()
        ],
        fetcherType: []
      },
      fields: {
        name: {
          value: '',
          error: ''
        },
        slug: {
          value: '',
          error: ''
        },
        fetcherType: {
          value: '',
          error: '',
          values: [
            '@pydailybot',
            'compare_and_filter',
            'replace_text',
            'Item 4'
          ]
        },
        fetcherOptions: {
          value: '',
          jsonSchemaMapping: {
            '@pydailybot': {
              $schema: 'https://json-schema.org/draft/2020-12/schema',
              title: 'type',
              type: 'object',
              properties: {
                chat_id: {
                  type: 'string',
                  title: 'Chat ID',
                  description: 'Telegram chat id'
                },
                disable_link_preview: {
                  type: 'boolean',
                  title: 'Disable link preview',
                  description: '',
                  default: false
                }
              },
              required: ['chat_id']
            },
            compare_and_filter: {
              $schema: 'https://json-schema.org/draft/2020-12/schema',
              title: 'type',
              type: 'object',
              properties: {
                field: {
                  type: 'string',
                  title: 'Field',
                  description: 'Field name for comparison'
                },
                operator: {
                  enum: ['=', '!=', '>', '<'],
                  type: 'string',
                  title: 'Operator',
                  description: 'Comparison operator'
                },
                value: { type: 'string', title: 'Value', description: 'Comparison value' },
                field_type: {
                  enum: ['string', 'integer'],
                  type: 'string',
                  title: 'Field type',
                  description: '',
                  default: 'string'
                }
              },
              required: ['field', 'operator', 'value']
            },
            replace_text: {
              $schema: 'https://json-schema.org/draft/2020-12/schema',
              title: 'type',
              type: 'object',
              properties: {
                field: { type: 'string', title: 'Field', description: 'Field name' },
                old: { type: 'string', title: 'Old value', description: 'Value to replace' },
                new: { type: 'string', title: 'New value', description: 'Value to replace with' }
              },
              required: ['field', 'old', 'new']
            }
          }
        },
        parserType: {
          value: '',
          error: '',
          values: [
            'rss',
            'reddit_json'
          ]
        },
        parserOptions: {
          value: '',
          jsonSchemaMapping: {}
        },
        description: {
          value: '',
          error: ''
        },
        tags: {
          value: [],
          error: '',
          items: []
        }
      },
      schema: {
        '@pydailybot': {
          $schema: 'https://json-schema.org/draft/2020-12/schema',
          title: 'type',
          type: 'object',
          properties: {
            chat_id: {
              type: 'string',
              title: 'Chat ID',
              description: 'Telegram chat id'
            },
            disable_link_preview: {
              type: 'boolean',
              title: 'Disable link preview',
              description: '',
              default: false
            }
          },
          required: ['chat_id']
        },
        compare_and_filter: {
          $schema: 'https://json-schema.org/draft/2020-12/schema',
          title: 'type',
          type: 'object',
          properties: {
            field: {
              type: 'string',
              title: 'Field',
              description: 'Field name for comparison'
            },
            operator: {
              enum: ['=', '!=', '>', '<'],
              type: 'string',
              title: 'Operator',
              description: 'Comparison operator'
            },
            value: { type: 'string', title: 'Value', description: 'Comparison value' },
            field_type: {
              enum: ['string', 'integer'],
              type: 'string',
              title: 'Field type',
              description: '',
              default: 'string'
            }
          },
          required: ['field', 'operator', 'value']
        },
        replace_text: {
          $schema: 'https://json-schema.org/draft/2020-12/schema',
          title: 'type',
          type: 'object',
          properties: {
            field: { type: 'string', title: 'Field', description: 'Field name' },
            old: { type: 'string', title: 'Old value', description: 'Value to replace' },
            new: { type: 'string', title: 'New value', description: 'Value to replace with' }
          },
          required: ['field', 'old', 'new']
        }
      }
    }
  }),
  methods: {
    submit (): void {
      this.validate()
      if (this.form.valid) {
        alert('Submitted')
        this.form.fields.name.error = 'Wrong Name!'
      }
    },
    clearError (field: keyof typeof this.form.fields) {
      if (this.form.fields[field].error) {
        this.form.fields[field].error = ''
      }
    },
    validate (): void {
      (this.$refs.form as HTMLFormElement).validate()
    },
    reset () {
      (this.$refs.form as HTMLFormElement).reset()
    },
    resetValidation () {
      (this.$refs.form as HTMLFormElement).resetValidation()
    }
  }
})
</script>
