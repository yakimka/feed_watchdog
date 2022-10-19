import { ListResource } from '@/types/ListResource'

export interface Receiver {
  name: string
  slug: string
  type: string
  options: string
}

export interface ReceiverList extends ListResource{
  results: Receiver[]
}
