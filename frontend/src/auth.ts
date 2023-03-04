import router from '@/router'

export const logout = () => {
  localStorage.removeItem('accesst')
  localStorage.removeItem('refresht')
  router.push({ name: 'login' })
}
