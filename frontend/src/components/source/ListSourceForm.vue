<template>
  <list-component
    v-model:pagination="pagination"
    :total-pages="sources.pages"
    :filters="true"
    :is-loading="pageIsLoading"
    @filtersInput="onFiltersInput"
  >
    <template v-slot:header>
      Sources
    </template>

    <template v-slot:filters>
      <v-row>
        <v-text-field
          v-model="filters.search"
          label="Search"
        ></v-text-field>
      </v-row>
    </template>

    <template v-slot:tableContent>
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
                Are you sure?
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
    </template>
  </list-component>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import useSources from '@/composables/useSources'
import { debounce } from '@/utils/debounce'
import usePagination from '@/composables/usePagination'
import useURL from '@/composables/useURL'
import ListComponent from '@/components/core/AdminList.vue'

const {
  sources,
  getSources,
  deleteSource
} = useSources()

const fetchSources = async () => {
  pageIsLoading.value = true
  await getSources(filters.search, pagination.page, pagination.pageSize)
  pageIsLoading.value = false
}

const { pagination } = usePagination(fetchSources)
const { setQueryToURL, getParamsFromURL } = useURL()

const buttonsLoading = reactive({} as {[key: string]: boolean})
const deleteDialog = reactive({} as {[key: string]: boolean})
const pageIsLoading = ref(true)

const filters = reactive({
  search: ''
})

const onFiltersInput = debounce(async () => {
  setQueryToURL(filters)
  await fetchSources()
})

const deleteSourceAndRefreshList = async (id: string) => {
  buttonsLoading[id] = true
  delete deleteDialog[id]
  await deleteSource(id)
  delete buttonsLoading[id]
  await fetchSources()
}

const parseFiltersFromURL = () => {
  const params = getParamsFromURL()
  if (params.search) {
    filters.search = params.search as string
  }
}

onMounted(async () => {
  parseFiltersFromURL()
  await fetchSources()
})
</script>
