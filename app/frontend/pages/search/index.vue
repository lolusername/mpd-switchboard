<template>
    <div class="flex flex-col h-screen">
      <!-- Pinned Documents Tabs -->
      <div v-if="pinnedDocs.length" class="flex bg-gray-100 p-2 border-b">
        <div
          v-for="doc in pinnedDocs"
          :key="doc.file_url"
          class="mr-2 px-4 py-2 bg-white shadow rounded-t cursor-pointer flex items-center"
          :class="{ 'bg-indigo-100': doc === selectedResult }"
          @click="selectPinnedDoc(doc)"
        >
          <span class="truncate max-w-[200px] font-medium text-gray-800">{{ doc.title || doc.file_name }}</span>
          <button @click.stop="unpinDoc(doc)" class="ml-2 text-red-500">&times;</button>
        </div>
      </div>
  
      <div class="flex flex-1 overflow-hidden">
        <!-- Search Panel -->
        <div class="w-1/3 p-5 overflow-y-auto bg-white border-r">
          <h1 class="text-2xl font-semibold text-gray-800 mb-5">PDF Search</h1>
          
          <!-- Search Input -->
          <div class="relative mb-4">
            <input
              v-model="searchQuery"
              placeholder="Search PDFs..."
              class="w-full p-3 pr-10 border rounded-md shadow-sm focus:ring-2 focus:ring-indigo-500"
              :disabled="isLoading"
            />
            <div v-if="isLoading" class="absolute right-2 top-2">
              <div class="animate-spin h-5 w-5 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
            </div>
          </div>
  
          <!-- Search Stats -->
          <div v-if="pagination" class="text-sm text-gray-500 mb-4">
            Found {{ pagination.total_documents.toLocaleString() }} documents
            <span v-if="pagination.total_pages > 1">
              (Page {{ pagination.current_page }} of {{ pagination.total_pages }})
            </span>
          </div>
  
          <!-- Results List -->
          <ul v-if="searchResults.length" class="space-y-3">
            <li
              v-for="result in searchResults"
              :key="result.file_name"
              class="p-4 bg-gray-50 border border-gray-200 rounded-lg shadow hover:bg-gray-100 transition-colors cursor-pointer"
              @mouseenter="showFullContent(result)"
            >
              <h3 class="text-lg font-medium text-gray-800">{{ result.title || result.file_name }}</h3>
              
              <!-- Highlights or Content Preview -->
              <div class="mt-2 text-sm text-gray-600">
                <div v-if="result.highlights?.content" class="space-y-1">
                  <div 
                    v-for="(highlight, idx) in result.highlights.content" 
                    :key="idx"
                    v-html="highlight"
                    class="bg-yellow-100 p-1 rounded-md"
                  ></div>
                </div>
                <p v-else>
                  {{ result.content ? result.content.substring(0, 200) + '...' : 'No content preview available' }}
                </p>
              </div>
  
              <!-- Actions and Metadata -->
              <div class="flex items-center justify-between mt-4 text-sm">
                <div class="flex items-center space-x-3">
                  <a 
                    :href="`/pdf/${result.file_url}`" 
                    target="_blank" 
                    class="text-indigo-600 hover:underline"
                  >
                    Download PDF
                  </a>
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      :checked="isPinned(result)" 
                      @change="togglePin(result)" 
                      class="mr-2 text-indigo-600 focus:ring-0"
                    >
                    <span>Pin</span>
                  </label>
                </div>
                <div class="text-gray-500">
                  Score: {{ result.score.toFixed(2) }}
                </div>
              </div>
            </li>
          </ul>
  
          <!-- Pagination Controls -->
          <div v-if="pagination && pagination.total_pages > 1" class="flex justify-center gap-2 mt-8">
            <button
              v-for="page in getPageNumbers()"
              :key="page"
              @click="changePage(page)"
              class="px-4 py-2 border rounded shadow-sm focus:outline-none transition-colors"
              :class="[
                page === pagination.current_page
                  ? 'bg-indigo-500 text-white'
                  : 'bg-gray-100 hover:bg-gray-200'
              ]"
            >
              {{ page }}
            </button>
          </div>
  
          <!-- No Results Message -->
          <p v-else-if="searchQuery && !isLoading" class="text-center text-gray-500 mt-8">
            No results found.
          </p>
        </div>
  
        <!-- Document Viewer -->
        <div v-if="selectedResult" class="w-2/3 p-6 bg-gray-100 overflow-y-auto">
          <div class="max-w-4xl mx-auto">
            <h2 class="text-3xl font-semibold mb-6 text-gray-800">
              {{ selectedResult.title || selectedResult.file_name }}
            </h2>
            <div class="prose max-w-none" v-html="formattedContent"></div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  
  <script setup>
  import { ref, watch, computed } from 'vue'
  
  // State
  const searchQuery = ref('')
  const searchResults = ref([])
  const pagination = ref(null)
  const isLoading = ref(false)
  const selectedResult = ref(null)
  const pinnedDocs = ref([])
  
  // Methods
  const handleSearch = async (page = 1) => {
    if (searchQuery.value.length < 3) {
      searchResults.value = []
      pagination.value = null
      return
    }
  
    isLoading.value = true
    try {
      const response = await $fetch('http://localhost:8000/search', {
        method: 'POST',
        body: {
          query: searchQuery.value,
          page,
          size: 50
        }
      })
      
      searchResults.value = response.results
      pagination.value = response.pagination
    } catch (error) {
      console.error('Search error:', error)
      searchResults.value = []
      pagination.value = null
    } finally {
      isLoading.value = false
    }
  }
  
  const getPageNumbers = () => {
    if (!pagination.value) return []
    const total = pagination.value.total_pages
    const current = pagination.value.current_page
    
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
    
    if (current <= 4) return [1, 2, 3, 4, 5, '...', total]
    if (current >= total - 3) return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
    
    return [1, '...', current - 1, current, current + 1, '...', total]
  }
  
  const showFullContent = (result) => {
    selectedResult.value = result
  }
  
  const hideFullContent = () => {
    // Remove this method since we don't need it anymore
    // Or if you want to keep it for other functionality:
    // if (!pinnedDocs.value.includes(selectedResult.value)) {
    //   selectedResult.value = null
    // }
  }
  
  const isPinned = (doc) => {
    return pinnedDocs.value.some(pinnedDoc => pinnedDoc.file_url === doc.file_url)
  }
  
  const togglePin = (doc) => {
    if (isPinned(doc)) {
      unpinDoc(doc)
    } else {
      pinnedDocs.value.push(doc)
      selectedResult.value = doc
    }
  }
  
  const unpinDoc = (doc) => {
    const index = pinnedDocs.value.findIndex(pinnedDoc => pinnedDoc.file_url === doc.file_url)
    if (index !== -1) {
      pinnedDocs.value.splice(index, 1)
      if (selectedResult.value === doc) {
        selectedResult.value = pinnedDocs.value[0] || null
      }
    }
  }
  
  const selectPinnedDoc = (doc) => {
    selectedResult.value = doc
  }
  
  const changePage = (page) => {
    if (typeof page === 'number' && page !== pagination.value?.current_page) {
      handleSearch(page)
    }
  }
  
  // Debounced search
  const debouncedSearch = useDebounce(() => handleSearch(1), 300)
  
  watch(searchQuery, () => {
    debouncedSearch()
  })
  
  function useDebounce(fn, delay) {
    let timeout
    return function (...args) {
      clearTimeout(timeout)
      timeout = setTimeout(() => fn(...args), delay)
    }
  }
  
  const formattedContent = computed(() => {
    if (!selectedResult.value?.content) return ''
  
    const content = selectedResult.value.content
  
    // Helper to find the most complete email header section
    const findEmailHeaders = (text) => {
      const sections = text.split('\n\n')
      const emailData = {
        'From': '',
        'Sent': '',
        'To': '',
        'Subject': ''
      }

      // Find the section that looks most like a complete header
      const headerSection = sections.find(section => {
        const headerCount = ['From:', 'Sent:', 'To:', 'Subject:']
          .filter(header => section.includes(header)).length
        return headerCount >= 3 // Section has most of the headers
      })

      if (headerSection) {
        // Parse each line carefully
        headerSection.split('\n').forEach(line => {
          const match = line.match(/^(From|Sent|To|Subject):\s*(.+)/)
          if (match) {
            const [_, key, value] = match
            if (value && !value.includes('[REDACTED]')) {
              emailData[key] = value.trim()
            }
          }
        })
      }

      // If any fields are still empty, look through the whole content
      if (!emailData['From']) {
        const fromMatch = text.match(/First Alert [I|l] (?:Alert|Urgent Update) \[alert@dataminr\.com\]/)
        if (fromMatch) emailData['From'] = fromMatch[0]
      }

      if (!emailData['Sent']) {
        const sentMatch = text.match(/\d{1,2}\/\d{1,2}\/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s*(?:AM|PM)/)
        if (sentMatch) emailData['Sent'] = sentMatch[0]
      }

      if (!emailData['To'] && text.includes('/CN=')) {
        const toMatch = text.match(/[a-zA-Z\.]+@[\w\.]+\s*(?:\/[A-Z]+=[^"\n]+)/)
        if (toMatch) emailData['To'] = toMatch[0]
      }

      if (!emailData['Subject']) {
        const subjectMatch = text.match(/Individual posts[^"\n]+via Twitter\./)
        if (subjectMatch) emailData['Subject'] = subjectMatch[0]
      }

      return emailData
    }

    const emailData = findEmailHeaders(content)
    const formattedSections = []

    // Add email header once
    formattedSections.push(`
      <div class="email-header">
        ${Object.entries(emailData).map(([key, value]) => `
          <div class="header-row">
            <span class="header-label">${key}:</span>
            <span class="header-value ${!value ? 'redacted' : ''}">
              ${value || '[REDACTED]'}
            </span>
          </div>
        `).join('')}
      </div>
    `)

    // Process remaining content
    content.split('\n\n').forEach(section => {
      const trimmedSection = section.trim()
      
      if (!trimmedSection || 
          trimmedSection === 'Message' ||
          trimmedSection.match(/^(From|Sent|To|Subject):/)) {
        return
      }

      if (trimmedSection.includes('CAUTION:')) {
        formattedSections.push(`<div class="caution-box">${trimmedSection}</div>`)
      } else if (trimmedSection.match(/DC_\d{4}-[A-Z]+-\d{6}\s+[A-Z]-\d+/)) {
        formattedSections.push(`<div class="doc-id">${trimmedSection}</div>`)
      } else if (!trimmedSection.includes('First Alert') && 
                 !trimmedSection.match(/^\d{1,2}\/\d{1,2}\/\d{4}/)) {
        formattedSections.push(`<div class="content-block">${trimmedSection.replace(/\n/g, '<br>')}</div>`)
      }
    })

    return formattedSections.filter(Boolean).join('\n')
  })
  </script>
  
  <style>
  .email-header {
    @apply bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200;
  }

  .header-row {
    @apply flex mb-2 last:mb-0;
  }

  .header-label {
    @apply w-24 font-medium text-gray-600;
  }

  .header-value {
    @apply flex-1 text-gray-900;
  }

  .caution-box {
    @apply bg-yellow-50 border-l-4 border-yellow-400 p-4 my-4 text-yellow-700;
  }

  .tweet-box {
    @apply bg-blue-50 rounded-lg p-4 my-4;
  }

  .tweet-header {
    @apply font-semibold mb-2 text-blue-800;
  }

  .tweet-content {
    @apply text-gray-800;
  }

  .location-box {
    @apply bg-green-50 rounded-lg p-4 my-4;
  }

  .location-label {
    @apply font-semibold text-green-800 mb-2;
  }

  .location-value {
    @apply text-gray-800;
  }

  .eyewitness-box {
    @apply bg-purple-50 rounded-lg p-4 my-4;
  }

  .eyewitness-line {
    @apply mb-1 last:mb-0;
  }

  .doc-id {
    @apply font-mono text-sm bg-gray-100 px-3 py-1.5 rounded my-2 text-gray-700 inline-block;
  }

  .content-block {
    @apply my-4 leading-relaxed;
  }

  /* Search highlight styling */
  :deep(em) {
    @apply bg-yellow-200 not-italic px-1 rounded;
  }

  .header-value.redacted {
    @apply text-gray-400 italic;
  }
  </style>