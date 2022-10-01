// eslint-disable-next-line @typescript-eslint/no-var-requires
const debounceDep = require('debounce')

export function debounce (func: () => any) {
  return debounceDep(func, 500)
}
