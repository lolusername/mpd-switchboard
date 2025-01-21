import { defineNuxtPlugin } from '#app'
import { useAuth } from '~/composables/useAuth'

export default defineNuxtPlugin((nuxtApp) => {
  const auth = useAuth()
  
  // Add auth token to all fetch requests
  nuxtApp.hook('app:created', () => {
    auth.checkAuth()
  })
}) 