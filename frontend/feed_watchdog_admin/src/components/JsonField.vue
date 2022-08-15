<template>
  <v-card class="mb-5">
    <v-toolbar
        color="primary"
        dark
        density="compact"
        flat
    >
      <v-toolbar-title>{{name}}{{ isChanged ? '*' : '' }}</v-toolbar-title>
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
    name: {
      type: String,
      required: true,
    },
    followValue: {
      type: String,
      default: '',
      required: false,
    },
    jsonSchemaMapping: {
      type: Object,
      default: () => ({}),
      required: false,
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
      try {
        return JSON.stringify(this.currentValues) !== JSON.stringify(JSON.parse(this.savedValue));
      } catch (e) {
        return true;
      }
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
        return "integer";
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
      if (!this.currentValues) {
        this.rawValue = "{}";
        return;
      }
      this.rawValue = JSON.stringify(this.currentValues, null, 2);
    },
    loadStore() {
      this.parsedValue = this.parseValue() || [];
      this.initStore();
    },
    restoreSavedValue() {
      this.rawValue = this.savedValue;
    },
    saveValue() {
      this.savedValue = this.rawValue;
    }
  },
  created() {
    this.rawValue = this.modelValue;

    this.saveValue();
    this.beautifyValue();

    this.parsedSchemas = this.parseJsonSchemas();
    this.loadStore();
    this.dumpStore();
  }
}
</script>
