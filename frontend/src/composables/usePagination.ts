import { reactive, watch } from 'vue'
import useURL from '@/composables/useURL'
import { scrollToTop } from '@/utils/pageNavigation'

// eslint-disable-next-line @typescript-eslint/no-empty-function
export default function usePagination (onChange: () => Promise<void> = async () => {}) {
  const { setQueryToURL, getParamsFromURL } = useURL()

  const parsePaginationFromURL = (): {page: number, pageSize: number} => {
    const fromQuery = getParamsFromURL()
    const result = {
      page: 1,
      pageSize: 25
    }

    if (fromQuery.page) {
      result.page = parseInt(fromQuery.page as string)
    }
    if (fromQuery.pageSize) {
      result.pageSize = parseInt(fromQuery.pageSize as string)
    }
    return result
  }

  const pagination = reactive(parsePaginationFromURL())

  watch(
    () => pagination,
    async () => {
      setQueryToURL(pagination)
      await onChange()
    },
    { deep: true }
  )

  watch(
    () => pagination.page,
    async () => {
      scrollToTop()
    }
  )

  return {
    pagination
  }
}
