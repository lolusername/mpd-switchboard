<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="ml-48 p-8">
      <!-- Header -->
      <div class="flex justify-between items-start mb-8">
        <div>
          <h1 class="text-2xl font-bold">Search Email Documents</h1>
        </div>
      </div>

      <!-- Search Input -->
      <div class="bg-white rounded-2xl border border-[var(--viz-primary)] p-6 mb-6 shadow-sm">
        <div class="relative flex gap-2">
          <input
            v-model="searchQuery"
            placeholder="Search across all email documents..."
            class="flex-1 p-4 pr-12 bg-opacity-50 border-none rounded-xl focus:ring-2 transition-all"
            :class="[isLoading ? 'opacity-75' : '']"
            style="background: var(--pattern); box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);"
            :disabled="isLoading"
            @keyup.enter="handleSearch(1)"
          />
          <button
            @click="handleSearch(1)"
            :disabled="isLoading || searchQuery.length < 3"
            class="font-mono uppercase px-6 py-2 bg-[var(--viz-primary)] text-white rounded-xl hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div v-if="isLoading" class="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
            <span v-else>Search</span>
          </button>
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
            <h3 class="text-sm font-medium text-[var(--viz-accent)]">Search Results</h3>
            <div class="flex items-center gap-2 text-xs text-gray-500">
              <span class="w-2 h-2 rounded-full bg-red-500"></span>
              <span>
                {{ 
                  pagination?.total_documents 
                    ? `${((pagination.current_page - 1) * 50) + 1}-${Math.min(pagination.current_page * 50, pagination.total_documents)} of ${pagination.total_documents.toLocaleString()} matches`
                    : '0 matches'
                }}
              </span>
            </div>
          </div>

          <!-- Results List -->
          <div class="space-y-4 max-h-[calc(100vh-300px)] overflow-y-auto">
            <div
              v-for="result in searchResults"
              :key="result.file_name"
              class="p-4 bg-opacity-50 rounded-xl hover:bg-opacity-75 transition-colors cursor-pointer"
              :class="{ 'border-2': selectedResult === result }"
              style="background: var(--viz-background); border-color: var(--viz-accent);"
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
                  ? 'text-white'
                  : 'bg-opacity-50 hover:bg-opacity-75'
              ]"
              :style="{
                background: page === pagination.current_page ? 'var(--viz-secondary)' : '',
                color: page === pagination.current_page ? 'white' : 'var(--neutral)'
              }"
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
                <span class="w-2 h-2 rounded-full bg-[var(--viz-accent)]"></span>
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
      return
    }
  
    isLoading.value = true
    try {
      const response = await $fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: {
          query: searchQuery.value,
          page
        }
      })
      
      // Handle empty or invalid responses
      if (!response || !response.pagination) {
        searchResults.value = []
        pagination.value = null
        return
      }
      
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
    if (!pagination.value || !pagination.value.total_pages) return []
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
    if (typeof page === 'number' && 
        page !== pagination.value?.current_page && 
        page > 0 && 
        page <= pagination.value?.total_pages) {
      handleSearch(page)
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
  :root {
    --primary: #1a1a1a; /* Deep black */
    --primary-light: #2d2d2d; /* Lighter black */
    --accent: #4a4a4a; /* Cool gray */
    --neutral: #232323; /* Off-black */
    --background: #fafafa; /* Almost white */
    --highlight: #e5e5e5; /* Light gray for highlights */
  }

  /* Clean, minimal styling matching the original */
  .email-header {
    @apply bg-slate-50 rounded-xl p-6 mb-6;
  }

  .header-row {
    @apply flex gap-4 mb-2;
  }

  .header-label {
    @apply w-24 font-medium text-gray-700;
  }

  .header-value {
    @apply flex-1 text-gray-600;
  }

  .content-block {
    @apply my-4 leading-relaxed text-gray-600;
  }

  /* Simple highlight styling */
  :deep(em) {
    @apply bg-neutral-100 text-neutral-900 px-1 rounded not-italic;
  }

  .doc-id {
    @apply font-mono text-sm text-gray-500 my-2;
  }

  /* Clean, minimal scrollbar */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }

  ::-webkit-scrollbar-track {
    background: transparent;
  }

  ::-webkit-scrollbar-thumb {
    @apply bg-gray-200 rounded;
  }

  ::-webkit-scrollbar-thumb:hover {
    @apply bg-gray-300;
  }

  /* Update existing color classes */
  .bg-red-500 {
    @apply bg-neutral-900;
  }

  .text-red-500 {
    @apply text-neutral-900;
  }

  .bg-red-50 {
    background-color: #f5f5f5;
  }

  .border-red-500 {
    @apply border-neutral-900;
  }

  .hover\:text-red-500:hover {
    @apply text-neutral-900;
  }

  .focus\:ring-red-500:focus {
    @apply ring-neutral-900;
  }
  </style>