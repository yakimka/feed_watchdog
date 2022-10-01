<template>
  <v-container fluid>
    <div class="text-h2 mb-5">
      Sources
    </div>
  </v-container>
  <v-container fluid>
    <v-form
      ref="form"
    >
      <v-row>
        <v-text-field
          v-model="filters.search"
          label="Search"
        ></v-text-field>
      </v-row>
    </v-form>
  </v-container>
  <v-container fluid>
    <v-table fixed-header>
      <thead>
      <tr>
        <th class="text-left">Name</th>
        <th class="text-left">Slug</th>
        <th class="text-left">Fetcher Type</th>
        <th class="text-left">Parser Type</th>
        <th class="text-left">Tags</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="source in sources.results"
          :key="source.slug"
      >
        <td>
          <v-tooltip activator="parent" v-if="source.description">{{ source.description }}</v-tooltip>
          <router-link :to="{name: 'edit-source', params: {id: source.slug}}">{{source.name}}</router-link>
        </td>
        <td>{{source.slug}}</td>
        <td>{{ source.fetcherType }}</td>
        <td>{{ source.parserType }}</td>
        <td>
          <v-chip v-for="tag in source.tags"
                  :key="tag"
          >
            {{ tag }}
          </v-chip>
        </td>
      </tr>
      </tbody>
    </v-table>
      <v-pagination
        v-model="page"
        :total-visible="10"
        :length="sources.pages"
        class="mt-5"
      ></v-pagination>
  </v-container>
</template>

<script lang="ts" setup>
// TODO https://stackoverflow.com/a/65737202
import { onMounted, ref, reactive, watch } from 'vue'
import useSources from '@/composables/useSources'
import { debounce } from '@/utils/debounce'

const {
  sources,
  getSources
} = useSources()

const page = ref(1)
const filters = reactive({
  search: ''
})

const fetchSources = debounce(async () => {
  console.log('fetchSources')
  await getSources(filters.search, page.value, 100)
})

watch(
  () => page.value,
  async () => {
    await fetchSources()
  },
  { deep: true }
)
watch(
  () => filters,
  async () => {
    await fetchSources()
  },
  { deep: true }
)

onMounted(async () => {
  await fetchSources()
})
</script>
