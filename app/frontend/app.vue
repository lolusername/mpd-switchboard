<template>
  <div>
    <h1 class="text-lime-500">PDF Search</h1>
    <input v-model="searchQuery" @input="handleSearch" placeholder="Search PDFs..." />
    <ul v-if="searchResults.length">
      <li v-for="result in searchResults" :key="result.file_url">
        <!-- <pre>{{ result }}</pre> -->
        <h3>{{ result.title }}</h3>
        <p v-if="result.highlights && result.highlights.content">
          <span v-html="result.highlights.content[0]"></span>
        </p>
        <p v-else>{{ result.content ? result.content.substring(0, 200) + '...' : 'No content preview available' }}</p>
        <a :href="result.file_url" target="_blank">View PDF</a>
      </li>
    </ul>
    <p v-else-if="searchQuery && !isLoading">No results found.</p>
    <p v-if="isLoading">Searching...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useApi } from '~/services/api'

const api = useApi()
const searchQuery = ref('')
const searchResults = ref([])
const isLoading = ref(false)

const handleSearch = async () => {
  if (searchQuery.value.length < 3) {
    searchResults.value = []
    return
  }

  isLoading.value = true
  try {
    const results = await api.search(searchQuery.value)
    searchResults.value = results || []
  } catch (error) {
    console.error('Search error:', error)
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

// Debounce the search to avoid too many API calls
const debouncedSearch = useDebounce(handleSearch, 300)

watch(searchQuery, () => {
  debouncedSearch()
})

// Simple debounce function
function useDebounce(fn: Function, delay: number) {
  let timeout: NodeJS.Timeout
  return function (...args: any[]) {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}
</script>
