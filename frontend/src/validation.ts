export function required () {
  return (value: any) => {
    if (!value) {
      return 'Field is required.'
    }
    return true
  }
}

export function minTextLength (length: number) {
  return (value: string) => {
    if (value.length < length) {
      return `Minimum length is ${length} characters.`
    }
    return true
  }
}

export function maxTextLength (length: number) {
  return (value: string) => {
    if (value.length > length) {
      return `Maximum length is ${length} characters.`
    }
    return true
  }
}

export function email () {
  return (value: string) => {
    if (!/.+@.+\..+/.test(value)) {
      return 'This is not a valid email.'
    }
    return true
  }
}

export function json () {
  return (value: string) => {
    try {
      JSON.parse(value)
      return true
    } catch (e) {
      return 'Invalid JSON.'
    }
  }
}
