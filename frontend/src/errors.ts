import { snakeToCamel } from '@/utils'

interface Error {
  message: string
  field: string
}

export function parseErrors (errors: Error[]): Error[] {
  const parsedErrors: Error[] = []
  for (const error of errors) {
    parsedErrors.push({
      message: error.message,
      field: snakeToCamel(error.field)
    })
  }
  return parsedErrors
}
