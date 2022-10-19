<template>
  <list-component
    v-model:pagination="pagination"
    :total-pages="receivers.pages"
    :filters="true"
    :is-loading="pageIsLoading"
    @filtersInput="onFiltersInput"
  >
    <template v-slot:header>
      Receivers
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
        <th class="text-left">Type</th>
        <th class="text-left">Actions</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="receiver in receivers.results"
          :key="receiver.slug"
      >
        <td>
          <v-tooltip activator="parent" v-if="receiver.description">{{ receiver.description }}</v-tooltip>
          <router-link class="text-decoration-none font-weight-bold" :to="{name: 'edit-receiver', params: {id: receiver.slug}}">{{receiver.name}}</router-link>
        </td>
        <td>{{receiver.slug}}</td>
        <td>{{ receiver.type }}</td>
        <td class="text-right">
          <v-btn
            :loading="buttonsLoading[receiver.slug]"
            :disabled="buttonsLoading[receiver.slug]"
            icon="mdi-circle-edit-outline"
            variant="text"
            title="Edit"
            :to="{name: 'edit-receiver', params: {id: receiver.slug}}"
          ></v-btn>
          <v-dialog
            v-model="deleteDialog[receiver.slug]"
            max-width="290"
          >
            <template v-slot:activator="{ props }">
              <v-btn
                :loading="buttonsLoading[receiver.slug]"
                :disabled="buttonsLoading[receiver.slug]"
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
              <v-card-text>Delete {{ receiver.name }}? </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="green darken-1"
                  text
                  @click="deleteReceiverAndRefreshList(receiver.slug)"
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
import useReceivers from '@/composables/useReceivers'
import { debounce } from '@/utils/debounce'
import usePagination from '@/composables/usePagination'
import useURL from '@/composables/useURL'
import ListComponent from '@/components/core/AdminList.vue'

const {
  receivers,
  getReceivers,
  deleteReceiver
} = useReceivers()

const fetchReceivers = async () => {
  pageIsLoading.value = true
  await getReceivers(filters.search, pagination.page, pagination.pageSize)
  pageIsLoading.value = false
}

const { pagination } = usePagination(fetchReceivers)
const { setQueryToURL, getParamsFromURL } = useURL()

const buttonsLoading = reactive({} as {[key: string]: boolean})
const deleteDialog = reactive({} as {[key: string]: boolean})
const pageIsLoading = ref(true)

const filters = reactive({
  search: ''
})

const onFiltersInput = debounce(async () => {
  setQueryToURL(filters)
  await fetchReceivers()
})

const deleteReceiverAndRefreshList = async (id: string) => {
  buttonsLoading[id] = true
  delete deleteDialog[id]
  await deleteReceiver(id)
  delete buttonsLoading[id]
  await fetchReceivers()
}

const parseFiltersFromURL = () => {
  const params = getParamsFromURL()
  if (params.search) {
    filters.search = params.search as string
  }
}

onMounted(async () => {
  parseFiltersFromURL()
  await fetchReceivers()
})
</script>
