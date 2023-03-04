import { ListResource } from '@/types/ListResource'

export interface Modifier {
  type: string
  options: string
}

export interface Stream {
  slug: string
  sourceSlug: string
  receiverSlug: string
  intervals: string[]
  squash: boolean
  receiverOptionsOverride: string
  messageTemplate: string
  modifiers: Modifier[]
  active: boolean
}

interface SlugWithName {
  name: string
  slug: string
}

export interface StreamInList {
  slug: string
  source: SlugWithName
  receiver: SlugWithName
  intervals: string[]
  active: boolean
}

export interface StreamList extends ListResource{
  results: StreamInList[]
}
