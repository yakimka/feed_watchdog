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
          label="Search"
        ></v-text-field>
      </v-row>
    </v-form>
  </v-container>
  <v-container fluid>
    <v-table fixed-header>
      <thead>
      <tr>
        <th class="text-left">ID</th>
        <th class="text-left">Name</th>
        <th class="text-left">Fetcher Type</th>
        <th class="text-left">Parser Type</th>
        <th class="text-left">Tags</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="source in sources"
          :key="source.id"
      >
        <td><router-link :to="{name: 'edit-source', params: {id: source.id}}">{{source.id}}</router-link></td>
        <td>
          <v-tooltip activator="parent" v-if="source.description">{{ source.description }}</v-tooltip>
          <router-link :to="{name: 'edit-source', params: {id: source.id}}">{{source.name}}</router-link>
        </td>
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
        v-model="pagination.page"
        :total-visible="10"
        :length="pagination.pagesTotal"
        class="mt-5"
      ></v-pagination>
  </v-container>
</template>

<script lang="ts" setup>
// TODO https://stackoverflow.com/a/65737202
import { onMounted, reactive } from 'vue'
import useSources from '@/composables/source'

const {
  sources,
  getSources
} = useSources()

onMounted(async () => {
  await getSources()
})

const pagination = reactive({
  page: 1,
  pagesTotal: 10
})
</script>
