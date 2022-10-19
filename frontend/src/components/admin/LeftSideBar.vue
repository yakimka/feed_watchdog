<template>
  <v-navigation-drawer
      v-model="navigation.isLeftSideBarOpen"
      bottom
  >
      <v-card
    class="mx-auto"
    max-width="300"
  >
    <v-list density="compact">
      <v-list-item prepend-icon="mdi-home" title="Home" :to="{name: 'home'}"></v-list-item>
      <v-list-item prepend-icon="mdi-web" title="Sources" :to="{name: 'sources'}">
        <template v-slot:append>
          <v-btn
            icon="mdi-plus"
            variant="text"
            title="Add Source"
            :to="{name: 'create-source'}"
          ></v-btn>
        </template>
      </v-list-item>
      <v-list-item prepend-icon="mdi-send" title="Receivers" :to="{name: 'receivers'}">
        <template v-slot:append>
          <v-btn
            icon="mdi-plus"
            variant="text"
            title="Add Receiver"
            :to="{name: 'create-receiver'}"
          ></v-btn>
        </template>
      </v-list-item>
      <v-list-item prepend-icon="mdi-broadcast" title="Streams" :to="{name: 'streams'}">
        <template v-slot:append>
          <v-btn
            icon="mdi-plus"
            variant="text"
            title="Add Stream"
            :to="{name: 'create-stream'}"
          ></v-btn>
        </template>
      </v-list-item>
    </v-list>
    </v-card>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { navigation } from '@/stores/navigation'
</script>
