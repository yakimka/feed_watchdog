interface NewSource {
  name: string
  slug: string
  fetcherType: string
  fetcherOptions: string
  parserType: string
  parserOptions: string
  description: string
  tags: string[]
}

interface Source extends NewSource {
  id: string
}

export interface APIError {
  errorMessage: string
  field?: string
}

export default {
  createSource (data: NewSource): Source | APIError {
    if (data.name.length < 3) {
      return {
        errorMessage: 'Name must be at least 3 characters long',
        field: 'name'
      }
    }
    return { ...data, ...{ id: 'some_id' } }
  },
  getSource (id: string): Source | APIError {
    return {
      id: id,
      name: 'Some Source',
      slug: 'some-source',
      fetcherType: 'some-fetcher-type',
      fetcherOptions: '{}',
      parserType: 'some-parser-type',
      parserOptions: '{}',
      description: 'Some description',
      tags: ['some', 'tags']
    }
  }
}
