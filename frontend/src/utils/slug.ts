import slugifyDep from 'slugify'

export function slugify (value: string): string {
  return slugifyDep(value, {
    lower: true
  })
}
