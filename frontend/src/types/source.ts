export default interface Source {
  name: string
  slug: string
  fetcherType: string
  fetcherOptions: string
  parserType: string
  parserOptions: string
  description: string
  tags: string[]
}
