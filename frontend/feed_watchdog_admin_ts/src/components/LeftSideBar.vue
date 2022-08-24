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
            title="Add source"
            :to="{name: 'create-source'}"
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

<script lang="ts">
export default {
  data: () => ({
    items: [
      {
        title: 'Foo',
        value: 'foo'
      },
      {
        title: 'Bar',
        value: 'bar'
      },
      {
        title: 'Fizz',
        value: 'fizz'
      },
      {
        title: 'Buzz',
        value: 'buzz'
      }
    ]
  })
}
</script>
