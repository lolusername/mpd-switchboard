import { ref } from 'vue'
import { useRuntimeConfig } from '#app'

const isAuthenticated = ref(false)
const token = ref<string | null>(null)

export function useAuth() {
  const config = useRuntimeConfig()
  
  const login = async (username: string, password: string) => {
    try {
      const response = await fetch(`${config.public.apiBase}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username,
          password,
        }),
        credentials: 'include', // Important for CORS
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()
      token.value = data.access_token
      isAuthenticated.value = true
      
      // Only use localStorage on client side
      if (process.client) {
        localStorage.setItem('auth_token', data.access_token)
      }
      
      return data
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  const logout = () => {
    token.value = null
    isAuthenticated.value = false
    if (process.client) {
      localStorage.removeItem('auth_token')
    }
  }

  const checkAuth = () => {
    if (process.client) {
      const savedToken = localStorage.getItem('auth_token')
      if (savedToken) {
        token.value = savedToken
        isAuthenticated.value = true
      }
    }
  }

  const isProtectedRoute = (route: string) => {
    const publicRoutes = ['/login']
    return !publicRoutes.includes(route)
  }

  return {
    login,
    logout,
    checkAuth,
    isAuthenticated,
    token,
    isProtectedRoute
  }
} 