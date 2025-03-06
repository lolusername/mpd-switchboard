<template>
  <div class="min-h-screen bg-[#F5F5F5]">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content - Adjust margin for desktop only -->
    <div class="p-4 md:ml-48 md:p-8">
      <!-- Stats Cards - Stack on mobile -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8" v-if="stats">


  
      </div>

      <!-- Visualization Grid - Single column on mobile -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 md:gap-6">
        <!-- Each visualization takes full width on mobile -->
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Entity Relationship Network</h3>
          <EntityNetwork />
        </div>
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Email Domain Communication Flow</h3>
          <DomainHeatmap />
        </div>
        <div class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Email Domain Distribution</h3>
          <DomainBarChart />
        </div>
        
        <!-- Topic Visualizations -->
        <div v-if="showDebugViz" class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic UMAP Analysis</h3>
          <TopicUMAP />
        </div>
        <div v-if="showDebugViz" class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic t-SNE Analysis</h3>
          <TopicTSNE />
        </div>
        <div v-if="showDebugViz" class="bg-white rounded border border-gray-100 p-4 md:p-6 col-span-1 md:col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic Similarity Network</h3>
          <TopicSimilarityNetwork />
        </div>
      </div>

      <div class="flex justify-end p-4">
        <button 
          @click="handleLogout" 
          class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, onUnmounted } from 'vue'
import DomainBarChart from '~/components/visualizations/DomainBarChart.vue'
import DomainHeatmap from '~/components/visualizations/DomainHeatmap.vue'
import EntityNetwork from '~/components/visualizations/EntityNetwork.vue'
import TopicUMAP from '~/components/visualizations/TopicUMAP.vue'
import TopicTSNE from '~/components/visualizations/TopicTSNE.vue'
import TopicSimilarityNetwork from '~/components/visualizations/TopicSimilarityNetwork.vue'
import Sidebar from '~/components/Sidebar.vue'
import { useAuth } from '~/composables/useAuth'
import { useRouter } from 'vue-router'

const auth = useAuth()
const router = useRouter()

const showDebugViz = ref(false)

const handleKeyDown = (e) => {
  if (e.shiftKey && e.key.toLowerCase() === 'd') {
    showDebugViz.value = !showDebugViz.value
  }
}

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)

  if (!auth.isAuthenticated.value) {
    router.push('/login')
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.rounded {
  transition: all 0.2s ease-in-out;
}

/* Modern scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}

/* Bauhaus-inspired typography scale */
.font-display {
  font-feature-settings: "ss01", "ss02";
  letter-spacing: -0.02em;
}


h1:hover {
  background-position: 0 100%;
}
</style>