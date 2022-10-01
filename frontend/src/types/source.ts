export interface Source {
  name: string
  slug: string
  fetcherType: string
  fetcherOptions: string
  parserType: string
  parserOptions: string
  description: string
  tags: string[]
}

export interface SourceList {
  count: number
  page: number
  pageSize: number
  pages: number
  results: Source[]

}
