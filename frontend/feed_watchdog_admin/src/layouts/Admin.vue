<template>
  <div>
    <app-bar></app-bar>
    <left-side-bar></left-side-bar>
    <v-main>
      <slot/>
    </v-main>
  </div>
</template>

<script>
import AppBar from '@/components/AppBar.vue';
import LeftSideBar from '@/components/LeftSideBar.vue';

export default {
  components: {AppBar, LeftSideBar},
}
</script>
