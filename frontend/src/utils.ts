export function snakeToCamel (text: string) {
  return text.replace(/[^a-zA-Z\d]+(.)/g, (m, chr) => chr.toUpperCase())
}

export function camelToSnake (text: string) {
  return text.replace(/[^a-zA-Z\d]+(.)/g, (_m, chr) => `_${chr.toLowerCase()}`)
}

export function snakeObjectToCamel (obj: any) {
  const newObj: any = {}
  for (const key in obj) {
    newObj[snakeToCamel(key)] = obj[key]
  }
  return newObj
}

export function camelObjectToSnake (obj: any) {
  const newObj: any = {}
  for (const key in obj) {
    newObj[camelToSnake(key)] = obj[key]
  }
  return newObj
}
