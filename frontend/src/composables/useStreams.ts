import { ref } from 'vue'
import { StreamList, Stream } from '@/types/stream'
import Error from '@/types/error'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { parseResponseErrors, handle404 } from '@/errors'

export default function useStreams () {
  const errors = ref<Error[]>([])
  const streams = ref<StreamList>({
    count: 0,
    page: 0,
    pageSize: 0,
    pages: 0,
    results: []
  })
  const stream = ref<Stream>({} as Stream)
  const streamTypes = ref<string[]>([])
  const modifierOptionsSchema = ref<object>({})

  const router = useRouter()

  const getStreams = async (q: string, page: number, pageSize: number) => {
    const response = await axios.get('/streams', {
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
      results: [] as Stream[]
    }

    for (const item of response.data.results) {
      streamListResult.results.push({
        slug: item.slug,
        sourceSlug: item.source_slug,
        receiverSlug: item.receiver_slug,
        squash: item.squash,
        receiverOptionsOverride: JSON.stringify(item.receiver_options_override),
        messageTemplate: item.message_template,
        modifiers: item.modifiers
      })
    }
    streams.value = streamListResult
  }

  const getStream = async (id: string) => {
    try {
      const response = await axios.get(`/streams/${id}`)
      stream.value = {
        slug: response.data.slug,
        sourceSlug: response.data.source_slug,
        receiverSlug: response.data.receiver_slug,
        squash: response.data.squash,
        receiverOptionsOverride: JSON.stringify(response.data.receiver_options_override),
        messageTemplate: response.data.message_template,
        modifiers: response.data.modifiers
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
      await axios.post('/streams', {
        slug: stream.value.slug,
        source_slug: stream.value.sourceSlug,
        receiver_slug: stream.value.receiverSlug,
        squash: stream.value.squash,
        receiver_options_override: JSON.parse(stream.value.receiverOptionsOverride),
        message_template: stream.value.messageTemplate,
        modifiers: stream.value.modifiers
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
        squash: stream.value.squash,
        receiver_options_override: JSON.parse(stream.value.receiverOptionsOverride),
        message_template: stream.value.messageTemplate,
        modifiers: stream.value.modifiers
      })
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
    const response = await axios.get('/processors/config/streams')
    modifierOptionsSchema.value = response.data

    streamTypes.value = []
    for (const key in response.data) {
      streamTypes.value.push(key)
    }
  }

  return {
    errors,
    streams,
    stream,
    streamTypes,
    modifierOptionsSchema,
    getStream,
    getStreams,
    storeStream,
    updateStream,
    deleteStream,
    getModifierOptionsSchema
  }
}
