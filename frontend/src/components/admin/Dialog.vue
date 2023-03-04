<template>
   <v-row justify="space-around">
    <v-col cols="auto">
      <v-dialog
        v-model="dialog.isActive"
        transition="dialog-bottom-transition"
      >
        <v-card>
          <v-toolbar
            color="primary"
          >
            <v-toolbar-title>{{ dialog.title }}</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <div class="text-h2 pa-12">{{ dialog.text }}</div>
          </v-card-text>
          <v-card-actions class="justify-end">
            <v-btn
              text
              @click="dialog.close()"
            >Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-col>
  </v-row>
</template>

<script lang="ts" setup>
import { dialog } from '@/stores/dialog'
</script>
