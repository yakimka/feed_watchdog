import { ref } from 'vue'
import Source from '@/types/source'
import Error from '@/types/error'
import { useRouter } from 'vue-router'

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
        id: 'some_id',
        name: 'Some Source',
        slug: 'some-source',
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
    source.value = {
      id: id,
      name: 'Some Source',
      slug: 'some-source',
      fetcherType: 'some-fetcher-type',
      fetcherOptions: '{"chat_id": "123456789"}',
      parserType: 'some-parser-type',
      parserOptions: '{}',
      description: 'Some description',
      tags: ['some', 'tags']
    }
  }

  const handleRedirectsBySaveType = async (type: string) => {
    if (type === 'save-and-create-stream') {
      await router.push({ name: 'home' })
    }
  }

  const storeSource = async (type: string) => {
    console.log('source stored', source.value)

    await handleRedirectsBySaveType(type)
  }

  const updateSource = async (type: string) => {
    console.log('source updated', source.value)

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
