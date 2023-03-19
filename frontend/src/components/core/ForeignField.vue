<template>
  <div>
    <v-autocomplete
      v-bind="$attrs"
      placeholder="Start typing to Search"
      :item-value="itemValue"
      :items="itemsCombined"
    >
      <template v-slot:append v-if="$attrs.modelValue">
        <v-btn
          icon="mdi-link"
          variant="text"
          title="Go to"
          :to="{name: routerName, params: {id: $attrs.modelValue}}"
        ></v-btn>
        </template>
    </v-autocomplete>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ForeignField',
  props: {
    routerName: {
      type: String,
      required: true
    },
    items: {
      type: Array,
      default: () => [],
      required: false
    },
    itemValue: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      savedItem: null
    }
  },
  computed: {
    itemsCombined () {
      if (this.savedItem === null || this.items.includes(this.savedItem)) {
        return this.items
      }
      return [...this.items, this.savedItem]
    }
  },
  watch: {
    items: function (value) {
      for (const item of value) {
        if (item[this.itemValue] === this.$attrs.modelValue) {
          this.savedItem = item
          break
        }
      }
    }
  }
})
</script>
