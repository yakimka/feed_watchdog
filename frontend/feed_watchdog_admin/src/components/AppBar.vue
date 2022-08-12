<template>
  <v-app-bar
      color="primary"
      density="compact"
  >
    <template v-slot:prepend>
      <v-app-bar-nav-icon @click.stop="navigation.toggleLeftSideBar()"></v-app-bar-nav-icon>
    </template>

    <v-app-bar-title>{{ title }}</v-app-bar-title>

    <template v-slot:append>
      <v-btn icon="mdi-dots-vertical"></v-btn>
    </template>
  </v-app-bar>
</template>

<script setup>
import {navigation} from "@/stores/navigation.js";
</script>

<script>
export default {
  name: 'AppBar',

  data: () => ({}),
  computed: {
    title() {
      return (this.$route.meta.title || "");
    }
  },
}
</script>
