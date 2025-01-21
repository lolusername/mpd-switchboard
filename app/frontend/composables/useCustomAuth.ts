import { useNuxtApp } from '#app'

export function useCustomAuth() {
  const { $auth } = useNuxtApp()
  
  return {
    signIn: $auth.signIn,
    signOut: $auth.signOut,
    loggedIn: $auth.loggedIn
  }
} 