import { useAuth } from '~/composables/useAuth'

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuth()
  
  // Check auth status
  auth.checkAuth()

  // Public routes that don't require authentication
  const publicRoutes = ['/login']
  
  // If route requires auth and user is not authenticated
  if (!publicRoutes.includes(to.path) && !auth.isAuthenticated.value) {
    return navigateTo('/login')
  }

  // If user is authenticated and trying to access login page
  if (to.path === '/login' && auth.isAuthenticated.value) {
    return navigateTo('/')
  }
}) 