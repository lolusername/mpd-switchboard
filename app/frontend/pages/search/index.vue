<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Sidebar -->
    <div class="fixed left-0 top-0 h-full w-16 bg-white border-r border-gray-100 flex flex-col items-center py-4 space-y-6">
      <div class="text-red-500 font-bold text-xs tracking-wider">
        D4BL
      </div>
      <NuxtLink to="/" class="p-2 hover:bg-gray-100 rounded-full">
        <svg class="w-6 h-6 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </NuxtLink>
      <div class="p-2 bg-gray-100 rounded-full">
        <svg class="w-6 h-6 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
    </div>

    <!-- Main Content -->
    <div class="ml-16 p-8">
      <!-- Header -->
      <div class="flex justify-between items-start mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Search Email Documents</h1>
          <p class="text-gray-500 mt-1">search across {{ pagination?.total_documents?.toLocaleString() || 'all' }} documents</p>
        </div>
      </div>

      <!-- Search Input -->
      <div class="bg-white rounded-2xl border border-gray-100 p-6 mb-6 shadow-sm">
        <div class="relative">
          <input
            v-model="searchQuery"
            placeholder="Search across all email documents..."
            class="w-full p-4 pr-12 bg-gray-50 border-none rounded-xl focus:ring-2 focus:ring-red-500 focus:bg-white transition-all"
            :disabled="isLoading"
          />
          <div class="absolute right-4 top-1/2 -translate-y-1/2">
            <div v-if="isLoading" class="animate-spin h-5 w-5 border-2 border-red-500 border-t-transparent rounded-full"></div>
            <svg v-else class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
        </div>
      </div>

      <!-- Pinned Documents Bar -->
      <div v-if="pinnedDocs.length" class="bg-white rounded-2xl border border-gray-100 p-4 mb-6 shadow-sm overflow-x-auto">
        <div class="flex gap-2">
          <div
            v-for="doc in pinnedDocs"
            :key="doc.file_url"
            class="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-xl cursor-pointer"
            :class="{ 'bg-red-50 border-2 border-red-500': doc === selectedResult }"
            @click="selectPinnedDoc(doc)"
          >
            <svg class="w-4 h-4 text-red-500" viewBox="0 0 24 24" fill="currentColor" stroke="none">
              <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
            </svg>
            <span class="truncate max-w-[200px] text-sm">{{ doc.title || doc.file_name }}</span>
            <button 
              @click.stop="unpinDoc(doc)" 
              class="text-gray-400 hover:text-red-500"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M6 18L18 6M6 6l12 12" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-6">
        <!-- Results Panel -->
        <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-medium text-gray-900">Search Results</h3>
            <div class="flex items-center gap-2 text-xs text-gray-500">
              <span class="w-2 h-2 rounded-full bg-red-500"></span>
              <span>{{ searchResults.length }} matches</span>
            </div>
          </div>

          <!-- Results List -->
          <div class="space-y-4 max-h-[calc(100vh-300px)] overflow-y-auto">
            <div
              v-for="result in searchResults"
              :key="result.file_name"
              class="p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
              :class="{ 'border-2 border-red-500': selectedResult === result }"
              @click="showFullContent(result)"
            >
              <h4 class="font-medium text-gray-900">{{ result.title || result.file_name }}</h4>
              <div v-if="result.highlights?.content" class="mt-2 space-y-1">
                <div 
                  v-for="(highlight, idx) in result.highlights.content" 
                  :key="idx"
                  v-html="highlight"
                  class="text-sm text-gray-600"
                ></div>
              </div>
              <div class="flex items-center justify-between mt-3 text-xs">
                <div class="flex items-center gap-3">
                  <button 
                    @click.stop="togglePin(result)"
                    class="flex items-center gap-1 text-gray-500 hover:text-red-500"
                  >
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path :d="isPinned(result) ? 'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z' : 'M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'" 
                            :fill="isPinned(result) ? 'currentColor' : 'none'"
                            stroke-width="1.5"/>
                    </svg>
                    {{ isPinned(result) ? 'Pinned' : 'Pin' }}
                  </button>
                </div>
                <span class="text-gray-400">Score: {{ result.score.toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="pagination?.total_pages > 1" class="flex justify-center gap-2 mt-6">
            <button
              v-for="page in getPageNumbers()"
              :key="page"
              @click="changePage(page)"
              class="px-3 py-1 rounded-md text-sm transition-colors"
              :class="[
                page === pagination.current_page
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              ]"
            >
              {{ page }}
            </button>
          </div>
        </div>

        <!-- Document Viewer -->
        <div class="bg-white rounded-2xl border border-gray-100 p-6 shadow-sm">
          <div v-if="selectedResult" class="h-full">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-medium text-gray-900">Document View</h3>
              <div class="flex items-center gap-2 text-xs text-gray-500">
                <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                <span>Selected Document</span>
              </div>
            </div>
            <div class="prose max-w-none max-h-[calc(100vh-400px)] overflow-y-auto">
              <div v-html="formattedContent"></div>
            </div>
            <div class="mt-4">
              <textarea 
                v-model="annotations[selectedResult.file_url]"
                @blur="saveAnnotation(selectedResult.file_url)"
                class="w-full p-3 bg-gray-50 border-none rounded-xl focus:ring-2 focus:ring-red-500 resize-none"
                rows="4"
                placeholder="Add notes about this document..."
              ></textarea>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-full text-gray-400">
            Select a document to view its contents
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
  
  
  <script setup>
  import { ref, watch, computed, onMounted } from 'vue'
  
  // State
  const searchQuery = ref('')
  const searchResults = ref([])
  const pagination = ref(null)
  const isLoading = ref(false)
  const selectedResult = ref(null)
  const pinnedDocs = ref([])
  
  const annotations = ref({})
  
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
      localStorage.setItem('pinnedDocs', JSON.stringify(pinnedDocs.value))
    }
  }
  
  const unpinDoc = (doc) => {
    const index = pinnedDocs.value.findIndex(pinnedDoc => pinnedDoc.file_url === doc.file_url)
    if (index !== -1) {
      pinnedDocs.value.splice(index, 1)
      if (selectedResult.value?.file_url === doc.file_url) {
        selectedResult.value = pinnedDocs.value[0] || null
      }
      localStorage.setItem('pinnedDocs', JSON.stringify(pinnedDocs.value))
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
  
  // Load annotations from localStorage
  onMounted(() => {
    const savedAnnotations = JSON.parse(localStorage.getItem('annotations') || '{}')
    annotations.value = savedAnnotations
    
    const savedPinnedDocs = JSON.parse(localStorage.getItem('pinnedDocs') || '[]')
    pinnedDocs.value = savedPinnedDocs
  })

  // Save annotation to localStorage
  const saveAnnotation = (fileUrl) => {
    localStorage.setItem('annotations', JSON.stringify(annotations.value))
  }
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