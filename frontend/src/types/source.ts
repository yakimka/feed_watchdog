import { ListResource } from '@/types/ListResource'

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

export interface SourceList extends ListResource{
  results: Source[]
}
