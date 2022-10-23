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

export interface StreamList extends ListResource{
  results: Stream[]
}
