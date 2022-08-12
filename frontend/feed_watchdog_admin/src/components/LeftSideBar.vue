<template>
  <v-navigation-drawer
      v-model="navigation.isLeftSideBarOpen"
      bottom
  >
    <v-list
        :items="items"
    ></v-list>
  </v-navigation-drawer>
</template>

<script setup>
import {navigation} from "@/stores/navigation.js";
</script>

<script>


export default {
  data: () => ({
    items: [
      {
        title: 'Foo',
        value: 'foo',
      },
      {
        title: 'Bar',
        value: 'bar',
      },
      {
        title: 'Fizz',
        value: 'fizz',
      },
      {
        title: 'Buzz',
        value: 'buzz',
      },
    ],
  }),
}
</script>
