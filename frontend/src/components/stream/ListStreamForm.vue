<template>
  <list-component
    v-model:pagination="pagination"
    :total-pages="streams.pages"
    :filters="true"
    :is-loading="pageIsLoading"
    @filtersInput="onFiltersInput"
  >
    <template v-slot:header>
      Streams
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
        <th class="text-left">Intervals</th>
        <th class="text-left">Active</th>
        <th class="text-left">Actions</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="stream in streams.results"
          :key="stream.slug"
      >
        <td>
          <router-link class="text-decoration-none font-weight-bold" :to="{name: 'edit-stream', params: {id: stream.slug}}">{{stream.source.name}} to {{stream.receiver.name}}</router-link>
        </td>
        <td>{{stream.slug}}</td>
        <td>
          <v-chip
            v-for="interval in stream.intervals"
            :key="interval"
          >
            {{ intervalsMap[interval] || interval }}
          </v-chip>
        </td>
        <td>
          <v-icon icon="mdi-check" v-if="stream.active"></v-icon>
          <v-icon icon="mdi-close-octagon" v-else></v-icon>
        </td>
        <td class="text-right">
          <v-btn
            :loading="buttonsLoading[stream.slug]"
            :disabled="buttonsLoading[stream.slug]"
            icon="mdi-circle-edit-outline"
            variant="text"
            title="Edit"
            :to="{name: 'edit-stream', params: {id: stream.slug}}"
          ></v-btn>
          <v-dialog
            v-model="deleteDialog[stream.slug]"
            max-width="290"
          >
            <template v-slot:activator="{ props }">
              <v-btn
                :loading="buttonsLoading[stream.slug]"
                :disabled="buttonsLoading[stream.slug]"
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
              <v-card-text>Delete {{ stream.name }}? </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="green darken-1"
                  text
                  @click="deleteStreamAndRefreshList(stream.slug)"
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
import useStreams from '@/composables/useStreams'
import { debounce } from '@/utils/debounce'
import usePagination from '@/composables/usePagination'
import useURL from '@/composables/useURL'
import ListComponent from '@/components/core/AdminList.vue'

const {
  streams,
  intervalTypes,
  getStreams,
  getIntervalTypes,
  deleteStream
} = useStreams()

const intervalsMap: { [key: string ]: string} = {}
const fetchStreams = async () => {
  pageIsLoading.value = true
  if (Object.keys(intervalsMap).length === 0) {
    await getIntervalTypes()
    for (const item of intervalTypes.value) {
      intervalsMap[item.value] = item.text
    }
  }
  await getStreams(filters.search, pagination.page, pagination.pageSize)
  pageIsLoading.value = false
}

const { pagination } = usePagination(fetchStreams)
const { setQueryToURL, getParamsFromURL } = useURL()

const buttonsLoading = reactive<{[key: string]: boolean}>({})
const deleteDialog = reactive<{[key: string]: boolean}>({})
const pageIsLoading = ref(true)

const filters = reactive({
  search: ''
})

const onFiltersInput = debounce(async () => {
  setQueryToURL(filters)
  await fetchStreams()
})

const deleteStreamAndRefreshList = async (id: string) => {
  buttonsLoading[id] = true
  delete deleteDialog[id]
  await deleteStream(id)
  delete buttonsLoading[id]
  await fetchStreams()
}

const parseFiltersFromURL = () => {
  const params = getParamsFromURL()
  if (params.search) {
    filters.search = params.search as string
  }
}

onMounted(async () => {
  parseFiltersFromURL()
  await fetchStreams()
})
</script>
