<template>
  <v-card class="mb-5">
    <v-toolbar
      flat
      dark
      density="compact"
      color="primary"
    >
      <v-toolbar-title>Options</v-toolbar-title>
    </v-toolbar>

    <v-card-text>
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
export default {
  name: 'JsonSchemaField',
  props: {
    followField: {
      type: String,
      default: '',
      required: false,
    }
  },
  data: () => ({}),
}
</script>
