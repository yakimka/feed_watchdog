<template>
  <v-card class="mb-5">
    <v-toolbar
        color="primary"
        dark
        density="compact"
        flat
    >
      <v-toolbar-title>Options</v-toolbar-title>
    </v-toolbar>

    <v-card-text>
      <v-textarea
        filled
        label="Raw Json"
        v-model="value"
      ></v-textarea>

      <v-text-field
          filled
          label="Title"
      ></v-text-field>
      <v-text-field
          single-line
          type="number"
      />
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
          color="success"
          depressed
      >
        Post
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import {required} from "@/validation";

export default {
  name: 'JsonSchemaField',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    followField: {
      type: String,
      default: '@pydailybot',  // TODO change to ''
      required: false,
    },
    jsonSchemaMapping: {
      type: Object,
      default: () => ({
        "@pydailybot": {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "type",
          "type": "object",
          "properties": {
            "chat_id": {
              "type": "string",
              "title": "Chat ID",
              "description": "Telegram chat id"
            },
            "disable_link_preview": {
              "type": "boolean",
              "title": "Disable link preview",
              "description": "",
              "default": false
            }
          },
          "required": ["chat_id"]
        },
        "compare_and_filter": {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "type",
          "type": "object",
          "properties": {
            "field": {
              "type": "string",
              "title": "Field",
              "description": "Field name for comparison"
            },
            "operator": {
              "enum": ["=", "!=", ">", "<"],
              "type": "string",
              "title": "Operator",
              "description": "Comparison operator"
            },
            "value": {"type": "string", "title": "Value", "description": "Comparison value"},
            "field_type": {
              "enum": ["string", "integer"],
              "type": "string",
              "title": "Field type",
              "description": "",
              "default": "string"
            }
          },
          "required": ["field", "operator", "value"]
        },
        "replace_text": {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "title": "type",
          "type": "object",
          "properties": {
            "field": {"type": "string", "title": "Field", "description": "Field name"},
            "old": {"type": "string", "title": "Old value", "description": "Value to replace"},
            "new": {"type": "string", "title": "New value", "description": "Value to replace with"}
          },
          "required": ["field", "old", "new"]
        }
      }),
      required: false,  // TODO make required
    },
  },
  emits: ['update:modelValue'],
  data: () => ({
    value: '',
    parsedValue: [],
    parsedSchemas: {},
  }),
  methods: {
    parseValue() {
      if (this.value.trim() === "") {
        return [];
      }

      try {
        let results = [];
        const parsed = JSON.parse(this.value);
        if (Array.isArray(parsed)) {
          alert("Root value of Json field must be object. Array is not supported.");
          return null
        }

        for (const [fieldName, fieldValue] of Object.entries(parsed)) {
          results.push({
            name: fieldName,
            type: this.toType(fieldValue),
            value: fieldValue,
          });
        }
        return results;
      } catch (e) {
        alert("invalid JSON:\n" + e);
        return null;
      }
    },
    toType(obj) {
      const typeName = ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase();
      if (typeName === "number" && !(obj.toString().contains("."))) {
        return "integer".contains("dsd");
      }
      return typeName;
    },
    parseJsonSchemas() {
      let results = {};
      if (!this.jsonSchemaMapping) {
        return results;
      }
      const fillerValues = {
        "string": "",
        "number": 0,
        "integer": 0,
        "boolean": false,
      }
      for (const [schemaName, schema] of Object.entries(this.jsonSchemaMapping)) {
        results[schemaName] = [];

        if (!schema.properties) {
          continue;
        }

        for (const [fieldName, field] of Object.entries(schema.properties)) {
          const defaultValue = field.default ?? fillerValues[field.type];
          const isRequired = schema.required.includes(fieldName);
          results[schemaName].push({
            name: fieldName,
            title: field.title ?? fieldName,
            type: field.type,
            description: field.description ?? "",
            default: defaultValue,
            rules: isRequired ? [required()] : [],
            enum: field.enum ?? [],
          });
        }
      }
      // this.$emit('update:modelValue', this.selectedCategory.id);
      return results;
    },
    beautifyValue() {
      try {
        this.value = JSON.stringify(JSON.parse(this.value), null, 2);
      } catch (e) {
        return null;
      }
    },
  },
  mounted() {
    this.value = this.modelValue;
    this.beautifyValue();

    this.parsedSchemas = this.parseJsonSchemas();
    const parsedValue = this.parseValue();
    if (parsedValue !== null) {
      this.parsedValue = parsedValue;
    }
  },
  created () {
    this.form && this.form.register(this);
  },
  beforeUnmount () {
    this.form && this.form.unregister(this);
  }
}
</script>
