import { ref } from 'vue'
import { ReceiverList, Receiver } from '@/types/receiver'
import Error from '@/types/error'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { parseResponseErrors, handle404 } from '@/errors'

export default function useReceivers () {
  const errors = ref<Error[]>([])
  const receivers = ref<ReceiverList>({
    count: 0,
    page: 0,
    pageSize: 0,
    pages: 0,
    results: []
  })
  const receiver = ref<Receiver>({} as Receiver)
  const receiverTypes = ref<string[]>([])
  const receiverOptionsSchema = ref<object>({})

  const router = useRouter()

  const getReceivers = async (q: string, page: number, pageSize: number) => {
    const response = await axios.get('/receivers', {
      params: {
        q: q,
        page: page,
        page_size: pageSize
      }
    })

    const receiverListResult = {
      count: response.data.count,
      page: response.data.page,
      pageSize: response.data.page_size,
      pages: response.data.pages,
      results: [] as Receiver[]
    }

    for (const item of response.data.results) {
      receiverListResult.results.push({
        name: item.name,
        slug: item.slug,
        type: item.type,
        options: JSON.stringify(item.options)
      })
    }
    receivers.value = receiverListResult
  }

  const getReceiver = async (id: string) => {
    try {
      const response = await axios.get(`/receivers/${id}`)
      receiver.value = {
        name: response.data.name,
        slug: response.data.slug,
        type: response.data.type,
        options: JSON.stringify(response.data.options)
      }
    } catch (error: any) {
      await handle404(error, router, history)
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleRedirectsBySaveType = async (type: string) => {
    await router.push({ name: 'edit-receiver', params: { id: receiver.value.slug } })
  }

  const storeReceiver = async (type: string) => {
    try {
      await axios.post('/receivers', {
        name: receiver.value.name,
        slug: receiver.value.slug,
        type: receiver.value.type,
        options: JSON.parse(receiver.value.options)
      })
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const updateReceiver = async (type: string) => {
    try {
      await axios.put(`/receivers/${receiver.value.slug}/`, {
        name: receiver.value.name,
        slug: receiver.value.slug,
        type: receiver.value.type,
        options: JSON.parse(receiver.value.options)
      })
    } catch (error: any) {
      errors.value = parseResponseErrors(error)
    }

    await handleRedirectsBySaveType(type)
  }

  const deleteReceiver = async (id: string) => {
    try {
      await axios.delete(`/receivers/${id}/`)
    } catch (error: any) {
      console.log(error.response.data)
    }
  }

  const getReceiverOptionsSchema = async () => {
    const response = await axios.get('/processors/config/receivers')
    receiverOptionsSchema.value = response.data

    receiverTypes.value = []
    for (const key in response.data) {
      receiverTypes.value.push(key)
    }
  }

  return {
    errors,
    receivers,
    receiver,
    receiverTypes,
    receiverOptionsSchema,
    getReceiver,
    getReceivers,
    storeReceiver,
    updateReceiver,
    deleteReceiver,
    getReceiverOptionsSchema
  }
}
