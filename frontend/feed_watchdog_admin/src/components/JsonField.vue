<template>
  <v-card class="mb-5">
    <v-toolbar
        color="primary"
        dark
        density="compact"
        flat
    >
      <v-toolbar-title>Options{{ isChanged ? '*' : '' }}</v-toolbar-title>
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

    <v-divider></v-divider>

    <v-card-actions>
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
      <v-btn
          color="success"
          depressed
          @click.stop="toggleEditMode"
      >
        {{ rawEditMode ? 'Schema Editor' : 'Raw Json Editor' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import {json, required} from "@/validation";
</script>

<script>
export default {
  name: 'JsonSchemaField',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    followValue: {
      type: String,
      default: '',
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
    rawEditMode: false,
    savedValue: '',
    rawValue: '',
    store: {},
    parsedValue: [],
    parsedSchemas: {},
  }),
  watch: {
    currentValues() {
      this.dumpStore();
    },
    rawValue() {
      this.$emit('update:modelValue', this.rawValue);
    }
  },
  computed: {
    currentSchema() {
      return this.parsedSchemas[this.followValue];
    },
    currentValues() {
      return this.store[this.followValue];
    },
    isChanged() {
      return true;
    }
  },
  methods: {
    parseValue() {
      if (this.rawValue.trim() === "") {
        return [];
      }

      try {
        let results = [];
        const parsed = JSON.parse(this.rawValue);
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
      return results;
    },
    beautifyValue() {
      try {
        this.rawValue = JSON.stringify(JSON.parse(this.rawValue), null, 2);
      } catch (e) {
        return null;
      }
    },
    initStore() {
      this.store = {};
      for (const [schemaName, fields] of Object.entries(this.parsedSchemas)) {
        this.store[schemaName] = {};
        for (const field of fields) {
          let found = false;
          for (const item of this.parsedValue) {
            if (item.name === field.name) {
              found = true;
              this.store[schemaName][field.name] = item.value;
            }
          }
          if (!found) {
            this.store[schemaName][field.name] = field.default;
          }
        }
      }
    },
    toggleEditMode() {
      if (this.rawEditMode) {
        this.loadStore();
      }
      this.rawEditMode = !this.rawEditMode;
    },
    dumpStore() {
      this.rawValue = JSON.stringify(this.currentValues, null, 2);
    },
    loadStore() {
      const parsedValue = this.parseValue();
      if (parsedValue !== null) {
        this.parsedValue = parsedValue;
      }
      this.initStore();
    },
    restoreSavedValue() {
      this.rawValue = this.savedValue;
    },
    saveValue() {
      this.savedValue = this.rawValue;
    }
  },
  mounted() {
    this.rawValue = this.modelValue;

    this.saveValue();
    this.beautifyValue();

    this.parsedSchemas = this.parseJsonSchemas();
    this.loadStore();
  }
}
</script>
