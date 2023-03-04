import { LocationQuery, useRoute, useRouter } from 'vue-router'

export default function useURL () {
  const router = useRouter()
  const route = useRoute()

  const setQueryToURL = (params: any) => {
    router.replace({
      query: removeEmptyValues({
        ...route.query,
        ...params
      }, Object.keys(params))
    })
  }

  const removeEmptyValues = (obj: any, keys: string[] = []) => {
    for (const propName in obj) {
      if ((propName.length && keys.includes(propName)) && !obj[propName]) {
        delete obj[propName]
      }
    }
    return obj
  }

  const getParamsFromURL = (): LocationQuery => {
    return route.query
  }

  return {
    setQueryToURL,
    getParamsFromURL
  }
}
