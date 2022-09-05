import { ref } from 'vue'
import Source from '@/types/source'
import Error from '@/types/error'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { parseErrors } from '@/errors'

export default function useSources () {
  const errors = ref<Error[]>([])
  const sources = ref<Source[]>([])
  const source = ref<Source>({} as Source)
  const fetcherTypes = ref<string[]>([])
  const fetcherOptionsSchema = ref<object>({})
  const parserTypes = ref<string[]>([])
  const parserOptionsSchema = ref<object>({})
  const availableTags = ref<string[]>([])

  const router = useRouter()

  const getSources = async () => {
    sources.value = [
      {
        name: 'Some Source 1',
        slug: 'some-source-1',
        fetcherType: 'some-fetcher-type',
        fetcherOptions: '{}',
        parserType: 'some-parser-type',
        parserOptions: '{}',
        description: 'Some description',
        tags: ['some', 'tags']
      },
      {
        name: 'Some Source 2',
        slug: 'some-source-2',
        fetcherType: 'some-fetcher-type',
        fetcherOptions: '{}',
        parserType: 'some-parser-type',
        parserOptions: '{}',
        description: 'Some description',
        tags: ['some', 'tags']
      },
      {
        name: 'Some Source 3',
        slug: 'some-source-3',
        fetcherType: 'some-fetcher-type',
        fetcherOptions: '{}',
        parserType: 'some-parser-type',
        parserOptions: '{}',
        description: 'Some description',
        tags: ['some', 'tags']
      }
    ]
  }

  const getSource = async (id: string) => {
    // TODO handle errors
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
      console.log(error.response.data)
    }
  }

  const handleRedirectsBySaveType = async (type: string) => {
    // TODO redirect to slug
    if (type === 'save-and-create-stream') {
      await router.push({ name: 'home' })
    }
  }

  const storeSource = async (type: string) => {
    // TODO handle errors
    try {
      await axios.post('/sources', {
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
      console.log(error.response.data)
    }

    await handleRedirectsBySaveType(type)
  }

  const updateSource = async (type: string) => {
    // TODO handle errors
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
    } catch (error: any) {
      errors.value = parseErrors(error.response.data.error.details)
      console.log(error.response.data)
    }

    await handleRedirectsBySaveType(type)
  }

  const getFetcherTypes = async () => {
    fetcherTypes.value = [
      '@pydailybot',
      'compare_and_filter',
      'replace_text',
      'Item 4'
    ]
  }

  const getFetcherOptionsSchema = async () => {
    fetcherOptionsSchema.value = {
      '@pydailybot': {
        $schema: 'https://json-schema.org/draft/2020-12/schema',
        title: 'type',
        type: 'object',
        properties: {
          chat_id: {
            type: 'string',
            title: 'Chat ID',
            description: 'Telegram chat id'
          },
          disable_link_preview: {
            type: 'boolean',
            title: 'Disable link preview',
            description: '',
            default: false
          }
        },
        required: ['chat_id']
      },
      compare_and_filter: {
        $schema: 'https://json-schema.org/draft/2020-12/schema',
        title: 'type',
        type: 'object',
        properties: {
          field: {
            type: 'string',
            title: 'Field',
            description: 'Field name for comparison'
          },
          operator: {
            enum: ['=', '!=', '>', '<'],
            type: 'string',
            title: 'Operator',
            description: 'Comparison operator'
          },
          value: { type: 'string', title: 'Value', description: 'Comparison value' },
          field_type: {
            enum: ['string', 'integer'],
            type: 'string',
            title: 'Field type',
            description: '',
            default: 'string'
          }
        },
        required: ['field', 'operator', 'value']
      },
      replace_text: {
        $schema: 'https://json-schema.org/draft/2020-12/schema',
        title: 'type',
        type: 'object',
        properties: {
          field: { type: 'string', title: 'Field', description: 'Field name' },
          old: { type: 'string', title: 'Old value', description: 'Value to replace' },
          new: { type: 'string', title: 'New value', description: 'Value to replace with' }
        },
        required: ['field', 'old', 'new']
      }
    }
  }

  const getParserTypes = async () => {
    parserTypes.value = [
      'rss',
      'reddit_json'
    ]
  }

  const getParserOptionsSchema = async () => {
    parserOptionsSchema.value = {}
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
    getSource,
    getSources,
    storeSource,
    updateSource,
    getFetcherTypes,
    getFetcherOptionsSchema,
    getParserTypes,
    getParserOptionsSchema,
    getAvailableTags
  }
}
