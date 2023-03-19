<template>
  <div>
    <v-autocomplete
      v-bind="$attrs"
      placeholder="Start typing to Search"
      :item-value="itemValue"
      :items="itemsCombined"
    ></v-autocomplete>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ForeignField',
  props: {
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
  mounted () {
    console.log('mounted')
    console.log(this.$attrs)
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
