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

  <progress-container
    :fluid="true"
    :is-loading="pageisLoading"
  >

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
    <v-row>
      <v-col cols="10">
        <v-pagination
          v-model="pagination.page"
          :total-visible="10"
          :length="sources.pages"
          class="mt-5"
        ></v-pagination>
      </v-col>
      <v-col cols="2">
        <v-select
          class="mt-5"
          v-model="pagination.pageSize"
          :items="[25, 50, 100]"
          variant="plain"
          label="Page Size"
        ></v-select>
      </v-col>
    </v-row>
  </progress-container>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref, watch } from 'vue'
import useSources from '@/composables/useSources'
import { useRouter, useRoute, LocationQuery } from 'vue-router'
import { scrollToTop } from '@/utils/pageNavigation'
import { debounce } from '@/utils/debounce'
import ProgressContainer from '@/components/ProgressContainer.vue'

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

const pagination = reactive({
  page: 1,
  pageSize: 25
})
const filtersDebounced = reactive({
  search: ''
})

const fetchSources = async () => {
  pageisLoading.value = true
  await getSources(filtersDebounced.search, pagination.page, pagination.pageSize)
  pageisLoading.value = false
}

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
  if (params.search) {
    filtersDebounced.search = params.search as string
  }
  if (params.pageSize) {
    pagination.pageSize = parseInt(params.pageSize as string)
  }
  if (params.page) {
    pagination.page = parseInt(params.page as string)
  }
}

let initialized = false
watch(
  () => pagination,
  async () => {
    if (initialized) {
      setQueryToURL(pagination)
      await fetchSources()
    }
  },
  { deep: true }
)
watch(
  () => filtersDebounced,
  debounce(async () => {
    if (initialized) {
      pagination.page = 1
      setQueryToURL({ ...pagination, ...filtersDebounced })
      await fetchSources()
    }
  }),
  { deep: true }
)

watch(
  () => pagination.page,
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
