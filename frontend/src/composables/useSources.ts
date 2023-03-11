import { ref } from 'vue'
import { SourceList, Source } from '@/types/source'
import Error from '@/types/error'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { parseResponseErrors, handle404 } from '@/errors'

export default function useSources () {
  const errors = ref<Error[]>([])
  const sources = ref<SourceList>({
    count: 0,
    page: 0,
    pageSize: 0,
    pages: 0,
    results: []
  })
  const source = ref<Source>({
    name: '',
    slug: '',
    fetcherType: '',
    fetcherOptions: '',
    parserType: '',
    parserOptions: '',
    description: '',
    tags: []
  })
  const fetcherTypes = ref<string[]>([])
  const fetcherOptionsSchema = ref<object>({})
  const parserTypes = ref<string[]>([])
  const parserOptionsSchema = ref<object>({})
  const availableTags = ref<string[]>([])
  const savedFetcherOptions = ref('')
  const savedParserOptions = ref('')

  const router = useRouter()

  const updateSavedOptions = () => {
    savedFetcherOptions.value = source.value.fetcherOptions
    savedParserOptions.value = source.value.parserOptions
  }

  const getSources = async (q: string, page: number, pageSize: number) => {
    const response = await axios.get('/sources/', {
      params: {
        q: q,
        page: page,
        page_size: pageSize
      }
    })

    const sourceListResult = {
      count: response.data.count,
      page: response.data.page,
      pageSize: response.data.page_size,
      pages: response.data.pages,
      results: [] as Source[]
    }

    for (const item of response.data.results) {
      sourceListResult.results.push({
        name: item.name,
        slug: item.slug,
        fetcherType: item.fetcher_type,
        fetcherOptions: JSON.stringify(item.fetcher_options),
        parserType: item.parser_type,
        parserOptions: JSON.stringify(item.parser_options),
        description: item.description,
        tags: item.tags
      })
    }
    sources.value = sourceListResult
  }

  const getSource = async (id: string) => {
    try {
      const response = await axios.get(`/sources/${id}/`)
      source.value = {
        name: response.data.name,
        slug: response.data.slug,
        fetcherType: response.data.fetcher_type,
        fetcherOptions: JSON.stringify(response.data.fetcher_options),
        parserType: response.data.parser_type,
        parserOptions: JSON.stringify(response.data.parser_options),
        description: response.data.description,
        tags: response.data.tags
      }
    } catch (error: any) {
      await handle404(error, router, history)
    }
  }

  const handleRedirectsBySaveType = async (type: string) => {
    if (type === 'save-and-create-stream') {
      await router.push({ name: 'home' })
    } else {
      await router.push({ name: 'edit-source', params: { id: source.value.slug } })
    }
  }

  const storeSource = async (type: string) => {
    try {
      await axios.post('/sources/', {
        name: source.value.name,
        slug: source.value.slug,
        fetcher_type: source.value.fetcherType,
        fetcher_options: JSON.parse(source.value.fetcherOptions),
        parser_type: source.value.parserType,
        parser_options: JSON.parse(source.value.parserOptions),
        description: source.value.description,
        tags: source.value.tags
      })
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const updateSource = async (type: string) => {
    try {
      await axios.put(`/sources/${source.value.slug}/`, {
        name: source.value.name,
        slug: source.value.slug,
        fetcher_type: source.value.fetcherType,
        fetcher_options: JSON.parse(source.value.fetcherOptions),
        parser_type: source.value.parserType,
        parser_options: JSON.parse(source.value.parserOptions),
        description: source.value.description,
        tags: source.value.tags
      })
      updateSavedOptions()
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const deleteSource = async (id: string) => {
    try {
      await axios.delete(`/sources/${id}/`)
    } catch (error: any) {
      console.log(error.response.data)
    }
  }

  const getFetcherOptionsSchema = async () => {
    const response = await axios.get('/processors/config/fetchers/')
    fetcherOptionsSchema.value = response.data

    fetcherTypes.value = []
    for (const key in response.data) {
      fetcherTypes.value.push(key)
    }
  }

  const getParserOptionsSchema = async () => {
    const response = await axios.get('/processors/config/parsers/')
    parserOptionsSchema.value = response.data

    parserTypes.value = []
    for (const key in response.data) {
      parserTypes.value.push(key)
    }
  }

  const getAvailableTags = async () => {
    availableTags.value = ['tag1', 'tag2', 'tag3']
  }

  return {
    errors,
    sources,
    source,
    fetcherTypes,
    fetcherOptionsSchema,
    parserTypes,
    parserOptionsSchema,
    availableTags,
    savedFetcherOptions,
    savedParserOptions,
    getSource,
    getSources,
    storeSource,
    updateSource,
    deleteSource,
    getFetcherOptionsSchema,
    getParserOptionsSchema,
    getAvailableTags,
    updateSavedOptions
  }
}
