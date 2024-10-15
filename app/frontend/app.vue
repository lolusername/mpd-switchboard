<template>
  <div class="flex h-screen">
    <!-- Left 1/3 for search and highlights -->
    <div class="w-1/3 p-4 overflow-y-auto">
      <h1 class="text-lime-500 text-2xl mb-4">PDF Search</h1>
      <input
        v-model="searchQuery"
        @input="handleSearch"
        placeholder="Search PDFs..."
        class="w-full p-2 mb-4 border rounded"
      />
      <ul v-if="searchResults.length">
        <li
          v-for="result in searchResults"
          :key="result.file_url"
          class="mb-4 p-2 border rounded hover:bg-gray-100"
          @mouseenter="showFullContent(result)"
          @mouseleave="hideFullContent"
        >
          <h3 class="font-bold">{{ result.title }}</h3>
          <p v-if="result.highlights && result.highlights.content">
            <span v-html="result.highlights.content[0]"></span>
          </p>
          <p v-else>{{ result.content ? result.content.substring(0, 200) + '...' : 'No content preview available' }}</p>
          <a :href="result.file_url" target="_blank" class="text-blue-500 hover:underline">View PDF</a>
        </li>
      </ul>
      <p v-else-if="searchQuery && !isLoading">No results found.</p>
      <p v-if="isLoading">Searching...</p>
    </div>

    <!-- Right 2/3 for full content -->
    <div class="w-2/3 p-4 bg-gray-100 overflow-y-auto" v-if="selectedResult">
      <h2 class="text-xl font-bold mb-4">{{ selectedResult.title }}</h2>
      <div v-html="selectedResult.content"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useApi } from '~/services/api'

const api = useApi()
const searchQuery = ref('')
const searchResults = ref([])
const isLoading = ref(false)
const selectedResult = ref(null)

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

const showFullContent = (result) => {
  selectedResult.value = result
}

const hideFullContent = () => {
  selectedResult.value = null
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

<style scoped>
/* Add any additional styles here */
</style>
