<template>
  <v-card class="mb-5">
    <v-toolbar
        density="compact"
    >
      <v-toolbar-title>{{name}}{{ isChanged ? '*' : '' }}</v-toolbar-title>
      <template v-slot:append v-if="compact">
         <v-btn
            depressed
            @click.stop="toggleEditMode"
        >
          {{ rawEditMode ? 'Schema' : 'Raw' }}
        </v-btn>
      </template>
    </v-toolbar>

    <v-card-text>
      <v-textarea v-if="rawEditMode"
                  v-model="rawValue"
                  :rules="[json()]"
                  filled
                  label="Raw Json"
      ></v-textarea>

      <template v-for="item in currentSchema" v-else>
        <v-select v-if="item.enum.length"
                  :key="item.name"
                  v-model="currentValues[item.name]"
                  :items="item.enum"
                  :label="item.title"
                  :rules="item.rules"
        ></v-select>
        <v-text-field v-else-if="item.type === 'string'"
                      :key="item.name"
                      v-model="currentValues[item.name]"
                      :label="item.title"
                      :rules="item.rules"
                      filled
        ></v-text-field>
        <v-text-field v-else-if="item.type === 'integer' || item.type === 'number'"
                      :key="item.name"
                      v-model="currentValues[item.name]"
                      :label="item.title"
                      :rules="item.rules"
                      single-line
                      type="number"
        ></v-text-field>
        <v-checkbox v-else-if="item.type === 'boolean'"
                    :key="item.name"
                    v-model="currentValues[item.name]"
                    :label="item.title"
                    :rules="item.rules"
        ></v-checkbox>
      </template>
    </v-card-text>

    <v-card-actions v-if="!compact || (compact && rawEditMode)">
      <v-spacer></v-spacer>
      <v-btn v-if="rawEditMode"
             color="success"
             depressed
             @click.stop="restoreSavedValue"
      >
        Restore saved
      </v-btn>
      <v-btn v-if="rawEditMode"
             color="success"
             depressed
             @click.stop="beautifyValue"
      >
        Beautify
      </v-btn>
      <v-btn v-if="!compact"
          color="success"
          depressed
          @click.stop="toggleEditMode"
      >
        {{ rawEditMode ? 'Schema Editor' : 'Raw Json Editor' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { json, required } from '@/validation'

interface ParsedValue {
  name: string
  type: string
  value: any
}

interface ParsedSchema {
  name: string
  title: string
  type: string
  description: string
  default: any
  rules: Array<(value: any) => boolean | string>
  enum: Array<string>
}

export default defineComponent({
  name: 'JsonField',
  setup () {
    return { json }
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    savedValue: {
      type: String,
      default: ''
    },
    compact: {
      type: Boolean,
      default: false
    },
    name: {
      type: String,
      required: true
    },
    followValue: {
      type: String,
      default: '',
      required: false
    },
    jsonSchemaMapping: {
      type: Object,
      default: () => ({}),
      required: false
    }
  },
  emits: ['update:modelValue'],
  data: () => ({
    rawEditMode: false,
    rawValue: '',
    store: {} as { [index: string]: { [index: string]: any } },
    parsedValue: [] as Array<ParsedValue>,
    parsedSchemas: {} as { [index: string]: Array<ParsedSchema> }
  }),
  watch: {
    currentValues () {
      this.dumpStore()
    },
    rawValue () {
      this.$emit('update:modelValue', this.rawValue)
    },
    jsonSchemaMapping () {
      this.parsedSchemas = this.parseJsonSchemas()
      this.loadStore()
      this.dumpStore()
    }
  },
  computed: {
    currentSchema () {
      return this.parsedSchemas[this.followValue] || {}
    },
    currentValues () {
      return this.store[this.followValue] || {}
    },
    isChanged () {
      try {
        return JSON.stringify(this.currentValues) !== JSON.stringify(JSON.parse(this.savedValue))
      } catch (e) {
        return true
      }
    }
  },
  methods: {
    parseValue (): Array<ParsedValue> | null {
      if (this.rawValue.trim() === '') {
        return []
      }

      try {
        const results = []
        const parsed = JSON.parse(this.rawValue)
        if (Array.isArray(parsed)) {
          alert('Root value of Json field must be object. Array is not supported.')
          return null
        }

        for (const [fieldName, fieldValue] of Object.entries(parsed)) {
          results.push({
            name: fieldName,
            type: this.toType(fieldValue),
            value: fieldValue as any
          })
        }
        return results
      } catch (e) {
        alert('invalid JSON:\n' + e)
        return null
      }
    },
    toType (obj: any): string {
      const typeName = ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)?.[1].toLowerCase()
      if (typeName === 'number' && !(obj.toString().contains('.'))) {
        return 'integer'
      }
      return typeName || 'unknown'
    },
    parseJsonSchemas (): { [index: string]: Array<ParsedSchema> } {
      const results: { [index: string]: Array<ParsedSchema> } = {}
      if (!this.jsonSchemaMapping) {
        return results
      }
      const fillerValues = {
        string: '',
        number: 0,
        integer: 0,
        boolean: false
      }
      enum TypeEnum {
        string = 'string',
        number = 'number',
        integer = 'integer',
        boolean = 'boolean'
      }
      for (const [schemaName, schema] of Object.entries(this.jsonSchemaMapping)) {
        results[schemaName] = []

        if (!schema.properties) {
          continue
        }

        for (const [fieldName, field] of Object.entries(schema.properties as { [index: string]: any })) {
          const defaultValue = field.default ?? fillerValues[field.type as TypeEnum]
          const isRequired = schema.required.includes(fieldName)
          results[schemaName].push({
            name: fieldName,
            title: field.title ?? fieldName,
            type: field.type,
            description: field.description ?? '',
            default: defaultValue,
            rules: isRequired ? [required()] : [],
            enum: field.enum ?? []
          })
        }
      }
      return results
    },
    beautifyValue (): void | null {
      try {
        this.rawValue = JSON.stringify(JSON.parse(this.rawValue), null, 2)
      } catch (e) {
        return null
      }
    },
    initStore (): void {
      this.store = {}
      for (const [schemaName, fields] of Object.entries(this.parsedSchemas)) {
        this.store[schemaName] = {}
        for (const field of fields) {
          let found = false
          for (const item of this.parsedValue) {
            if (item.name === field.name) {
              found = true
              this.store[schemaName][field.name] = item.value
            }
          }
          if (!found) {
            this.store[schemaName][field.name] = field.default
          }
        }
      }
    },
    toggleEditMode (): void {
      if (this.rawEditMode) {
        this.loadStore()
      }
      this.rawEditMode = !this.rawEditMode
    },
    dumpStore (): void {
      if (!this.currentValues) {
        this.rawValue = '{}'
        return
      }
      this.rawValue = JSON.stringify(this.currentValues, null, 2)
    },
    loadStore (): void {
      this.parsedValue = this.parseValue() || []
      this.initStore()
    },
    restoreSavedValue (): void {
      this.rawValue = this.savedValue
    }
  },
  created (): void {
    this.rawValue = this.modelValue

    this.beautifyValue()
  }
})
</script>
