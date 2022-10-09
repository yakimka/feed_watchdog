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
          v-model="filtersDebounced.search"
          label="Search"
        ></v-text-field>
      </v-row>
    </v-form>
  </v-container>

  <v-progress-linear v-if="pageisLoading"
    indeterminate
    color="primary"
  ></v-progress-linear>

  <v-container style="position: relative" fluid>
    <v-overlay
      :model-value="pageisLoading"
      contained
      persistent
    ></v-overlay>

    <v-table fixed-header>
      <thead>
      <tr>
        <th class="text-left">Name</th>
        <th class="text-left">Slug</th>
        <th class="text-left">Fetcher Type</th>
        <th class="text-left">Parser Type</th>
        <th class="text-left">Tags</th>
        <th class="text-left">Actions</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="source in sources.results"
          :key="source.slug"
      >
        <td>
          <v-tooltip activator="parent" v-if="source.description">{{ source.description }}</v-tooltip>
          <router-link class="text-decoration-none font-weight-bold" :to="{name: 'edit-source', params: {id: source.slug}}">{{source.name}}</router-link>
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
        <td>
          <v-btn
            :loading="buttonsLoading[source.slug]"
            :disabled="buttonsLoading[source.slug]"
            icon="mdi-circle-edit-outline"
            variant="text"
            title="Edit"
            :to="{name: 'edit-source', params: {id: source.slug}}"
          ></v-btn>
          <v-dialog
            v-model="deleteDialog[source.slug]"
            max-width="290"
          >
            <template v-slot:activator="{ props }">
              <v-btn
                :loading="buttonsLoading[source.slug]"
                :disabled="buttonsLoading[source.slug]"
                icon="mdi-delete-outline"
                variant="text"
                title="Delete"
                v-bind="props"
              ></v-btn>
            </template>
            <v-card>
              <v-card-title class="text-h5">
                Delete source
              </v-card-title>
              <v-card-text>Delete {{ source.name }}? </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="green darken-1"
                  text
                  @click="deleteSourceAndRefreshList(source.slug)"
                >
                  Yes
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </td>
      </tr>
      </tbody>
    </v-table>
      <v-pagination
        v-model="filters.page"
        :total-visible="10"
        :length="sources.pages"
        class="mt-5"
      ></v-pagination>
  </v-container>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref, watch } from 'vue'
import useSources from '@/composables/useSources'
import { useRouter, useRoute, LocationQuery } from 'vue-router'
import { scrollToTop } from '@/utils/pageNavigation'
import { debounce } from '@/utils/debounce'

const router = useRouter()
const route = useRoute()

const {
  sources,
  getSources,
  deleteSource
} = useSources()

const buttonsLoading = reactive({} as {[key: string]: boolean})
const deleteDialog = reactive({} as {[key: string]: boolean})
const pageisLoading = ref(true)

const filters = reactive({
  page: 1,
  pageSize: 50
})
const filtersDebounced = reactive({
  search: ''
})

const fetchSources = async () => {
  pageisLoading.value = true
  await getSources(filtersDebounced.search, filters.page, filters.pageSize)
  pageisLoading.value = false
}
const fetchSourcesDebounced = debounce(fetchSources)

const deleteSourceAndRefreshList = async (id: string) => {
  buttonsLoading[id] = true
  delete deleteDialog[id]
  await deleteSource(id)
  delete buttonsLoading[id]
  await fetchSources()
}

const setQueryToURL = (params: object) => {
  router.replace({
    query: removeEmptyValues({
      ...route.query,
      ...params
    }, Object.keys(params))
  })
}

const getParamsFromURL = (): LocationQuery => {
  return route.query
}

const removeEmptyValues = (obj: any, keys: string[] = []) => {
  for (const propName in obj) {
    if ((propName.length && keys.includes(propName)) && !obj[propName]) {
      delete obj[propName]
    }
  }
  return obj
}

const parseFiltersFromURL = () => {
  const params = getParamsFromURL()
  if (params.page) {
    filters.page = parseInt(params.page as string)
  }
  if (params.pageSize) {
    filters.pageSize = parseInt(params.pageSize as string)
  }
  if (params.search) {
    filtersDebounced.search = params.search as string
  }
}

let initialized = false
watch(
  () => filters,
  async () => {
    if (initialized) {
      setQueryToURL(filters)
      console.log('fetch')
      await fetchSources()
    }
  },
  { deep: true }
)
watch(
  () => filtersDebounced,
  async () => {
    if (initialized) {
      setQueryToURL(filtersDebounced)
      console.log('fetch debounced')
      await fetchSourcesDebounced()
    }
  },
  { deep: true }
)

watch(
  () => filters.page,
  async () => {
    scrollToTop()
  }
)

onMounted(async () => {
  parseFiltersFromURL()
  await fetchSources()
  initialized = true
})
</script>
