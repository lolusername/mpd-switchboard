<template>
  <div>
    <slot />
  </div>
</template>

<script setup>
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const auth = useAuth()
const router = useRouter()

onMounted(() => {
  // Check auth status
  auth.checkAuth()
  
  // If not authenticated and not on login page, redirect to login
  if (!auth.isAuthenticated.value && router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
})
</script> 