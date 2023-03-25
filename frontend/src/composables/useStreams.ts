import { reactive, ref, watch, onMounted, computed } from 'vue'
import { StreamList, Stream, Modifier, StreamInList } from '@/types/stream'
import Error from '@/types/error'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { parseResponseErrors, handle404 } from '@/errors'
import { Source } from '@/types/source'
import { Receiver } from '@/types/receiver'
import useSources from '@/composables/useSources'
import useReceivers from '@/composables/useReceivers'
import { debounce } from '@/utils/debounce'

export default function useStreams () {
  const errors = ref<Error[]>([])
  const streams = ref<StreamList>({
    count: 0,
    page: 0,
    pageSize: 0,
    pages: 0,
    results: []
  })
  const stream = ref<Stream>({
    slug: '',
    sourceSlug: '',
    receiverSlug: '',
    intervals: [],
    squash: false,
    receiverOptionsOverride: '',
    messageTemplate: '',
    modifiers: [],
    active: true
  })

  interface Interval {
    text: string
    value: string
  }
  interface MessageTemplate {
    text: string
    value: string
  }
  const streamTypes = ref<string[]>([])
  const intervalTypes = ref<Interval[]>([])
  const selectedMessageTemplate = ref('')
  const messageTemplates = ref<MessageTemplate[]>([])
  const modifierOptionsSchema = ref({})
  const savedReceiverOptionsOverride = ref('')
  const savedModifiers = ref<Modifier[]>([])

  const sourceSlugData = reactive({
    search: '',
    items: [] as Source[],
    isLoading: false,
    cache: {} as Record<string, Source[]>
  })
  const receiverSlugData = reactive({
    search: '',
    items: [] as Receiver[],
    isLoading: false,
    cache: {} as Record<string, Receiver[]>
  })
  const { sources, getSources } = useSources()
  const { receivers, receiverOptionsSchema, getReceivers, getReceiverOptionsSchema } = useReceivers()

  const router = useRouter()

  const updateSavedOptions = () => {
    savedReceiverOptionsOverride.value = stream.value.receiverOptionsOverride
    savedModifiers.value = JSON.parse(JSON.stringify(stream.value.modifiers))
  }

  const getStreams = async (q: string, page: number, pageSize: number) => {
    const response = await axios.get('/streams/', {
      params: {
        q: q,
        page: page,
        page_size: pageSize
      }
    })

    const streamListResult = {
      count: response.data.count,
      page: response.data.page,
      pageSize: response.data.page_size,
      pages: response.data.pages,
      results: [] as StreamInList[]
    }

    for (const item of response.data.results) {
      streamListResult.results.push({
        slug: item.slug,
        source: item.source,
        receiver: item.receiver,
        intervals: item.intervals,
        active: item.active
      })
    }
    streams.value = streamListResult
  }

  const getStream = async (id: string) => {
    try {
      const response = await axios.get(`/streams/${id}/`)
      stream.value = {
        slug: response.data.slug,
        sourceSlug: response.data.source_slug,
        receiverSlug: response.data.receiver_slug,
        intervals: response.data.intervals,
        squash: response.data.squash,
        receiverOptionsOverride: JSON.stringify(response.data.receiver_options_override),
        messageTemplate: response.data.message_template,
        modifiers: response.data.modifiers.map((o: Modifier) => { return { type: o.type, options: JSON.stringify(o.options) } }),
        active: response.data.active
      }
    } catch (error: any) {
      await handle404(error, router, history)
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRedirectsBySaveType = async (type: string) => {
    await router.push({ name: 'edit-stream', params: { id: stream.value.slug } })
  }

  const storeStream = async (type: string) => {
    try {
      await axios.post('/streams/', {
        slug: stream.value.slug,
        source_slug: stream.value.sourceSlug,
        receiver_slug: stream.value.receiverSlug,
        intervals: stream.value.intervals,
        squash: stream.value.squash,
        receiver_options_override: JSON.parse(stream.value.receiverOptionsOverride),
        message_template: stream.value.messageTemplate,
        modifiers: stream.value.modifiers.map((o: Modifier) => { return { type: o.type, options: JSON.parse(o.options) } }),
        active: stream.value.active
      })
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const updateStream = async (type: string) => {
    try {
      await axios.put(`/streams/${stream.value.slug}/`, {
        slug: stream.value.slug,
        source_slug: stream.value.sourceSlug,
        receiver_slug: stream.value.receiverSlug,
        intervals: stream.value.intervals,
        squash: stream.value.squash,
        receiver_options_override: JSON.parse(stream.value.receiverOptionsOverride),
        message_template: stream.value.messageTemplate,
        modifiers: stream.value.modifiers.map((o: Modifier) => { return { type: o.type, options: JSON.parse(o.options) } }),
        active: stream.value.active
      })
      updateSavedOptions()
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const deleteStream = async (id: string) => {
    try {
      await axios.delete(`/streams/${id}/`)
    } catch (error: any) {
      console.log(error.response.data)
    }
  }

  const getModifierOptionsSchema = async () => {
    const response = await axios.get('/processors/config/modifiers/')
    modifierOptionsSchema.value = response.data

    streamTypes.value = []
    for (const key in modifierOptionsSchema.value) {
      streamTypes.value.push(key)
    }
  }

  const overrideOptionsSchema = computed(() => {
    let receiver = null
    for (const item of receivers.value.results) {
      if (item.slug === stream.value.receiverSlug) {
        receiver = item
        break
      }
    }
    if (receiver === null) {
      return {}
    }

    const result = { '': {} }
    for (const [key, value] of Object.entries(receiverOptionsSchema.value)) {
      if (key === receiver.type) {
        const schema = JSON.parse(JSON.stringify(value))
        for (const item in schema.properties) {
          if (receiver.optionsAllowedToOverride.includes(item)) {
            schema.properties[item].default = JSON.parse(receiver.options)[item]
          } else {
            delete schema.properties[item]
          }
        }
        result[''] = schema
        break
      }
    }
    return result
  })

  const getIntervalTypes = async () => {
    const response = await axios.get('/streams/intervals/')
    intervalTypes.value = response.data
  }

  const getMessageTemplates = async () => {
    const response = await axios.get('/streams/message_templates/')
    messageTemplates.value = response.data
  }

  const search = async (type: string, value = '') => {
    let data, items, func
    if (type === 'source') {
      data = sourceSlugData
      items = sources
      func = getSources
    } else {
      data = receiverSlugData
      items = receivers
      func = getReceivers
    }

    if (value in data.cache) {
      data.items = data.cache[value]
      return
    }
    data.isLoading = true
    await func(value, 1, 10)
    data.items = items.value.results
    data.cache[value] = items.value.results
    data.isLoading = false
  }

  const searchSource = async (value = '') => {
    await search('source', value)
  }

  const searchReceiver = async (value = '') => {
    await search('receiver', value)
  }

  watch(
    () => sourceSlugData.search,
    debounce(async (value: string) => {
      // this fucking autocomplete component is so fucking stupid
      // it set the value of search to empty string when it loses focus
      if (value === '') {
        return
      }
      await searchSource(value)
    })
  )
  watch(
    () => receiverSlugData.search,
    debounce(async (value: string) => {
      if (value === '') {
        return
      }
      await searchReceiver(value)
    })
  )
  watch(
    () => stream.value.messageTemplate,
    (value: string) => {
      for (const item of messageTemplates.value) {
        if (item.value === value) {
          selectedMessageTemplate.value = value
          return
        }
      }
      selectedMessageTemplate.value = ''
    }
  )

  onMounted(async () => {
    await getReceiverOptionsSchema()
  })

  return {
    errors,
    streams,
    stream,
    streamTypes,
    modifierOptionsSchema,
    sourceSlugData,
    receiverSlugData,
    overrideOptionsSchema,
    savedReceiverOptionsOverride,
    savedModifiers,
    intervalTypes,
    selectedMessageTemplate,
    messageTemplates,
    getStream,
    getStreams,
    storeStream,
    updateStream,
    deleteStream,
    getModifierOptionsSchema,
    searchSource,
    searchReceiver,
    updateSavedOptions,
    getIntervalTypes,
    getMessageTemplates
  }
}
