import { defineNuxtRouteMiddleware, navigateTo } from '#app'
import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuth()
  
  // Check for stored token
  auth.checkAuth()

  // If route requires auth and user is not authenticated
  if (to.path !== '/login' && !auth.isAuthenticated.value) {
    return navigateTo('/login')
  }

  // If user is authenticated and trying to access login page
  if (to.path === '/login' && auth.isAuthenticated.value) {
    return navigateTo('/')
  }
}) 