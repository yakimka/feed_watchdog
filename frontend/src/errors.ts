import { snakeToCamel } from '@/utils/case'
import Error from '@/types/error'
import { Router } from 'vue-router'

export function parseResponseErrors (error: any): Error[] {
  if (error.message) {
    return [{ message: error.message }]
  }

  const validationErrors = error.response.data?.error.details
  if (validationErrors) {
    return parseValidationErrors(validationErrors)
  }
  return []
}

export function parseValidationErrors (errors: Error[]): Error[] {
  const parsedErrors: Error[] = []
  for (const error of errors) {
    parsedErrors.push({
      message: error.message,
      field: snakeToCamel(error.field || '')
    })
  }
  return parsedErrors
}

export async function handle404 (error: any, router: Router, history: History) {
  if (error.response.status === 404) {
    const currentURL = window.location.href
    await router.replace({ name: 'not-found' })
    history.replaceState({}, 'Not Found', currentURL)
    return true
  }
  return false
}
