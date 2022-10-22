import { ListResource } from '@/types/ListResource'

export interface Modifier {
  type: string
  options: string
}

export interface Stream {
  slug: string
  sourceSlug: string
  receiverSlug: string
  squash: boolean
  receiverOptionsOverride: string
  messageTemplate: string
  modifiers: Modifier[]
}

export interface StreamList extends ListResource{
  results: Stream[]
}
