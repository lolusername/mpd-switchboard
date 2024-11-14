<template>
  <div class="min-h-screen bg-[#F5F5F5]">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="ml-48 p-8">

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 gap-4 mb-8" v-if="stats">
        <!-- Email Communications -->
        <div class="bg-[#9ca756] rounded-2xl p-5 border border-[#FA7358]/10 hover:shadow-lg transition-all">
          <div class="flex items-center gap-2 text-sm font-medium text-[#F5F5F5] mb-3">
            <svg class="w-5 h-5 text-[#F5F5F5]" viewBox="0 0 24 24" fill="#003366">
              <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
            </svg>
            <span class="font-semibold text-[#003366]">Email Communications</span>
          </div>

          <div class="text-5xl font-bold text-[#F5F5F5] mb-2 font-display tracking-tight">{{ stats.emailStats.total }}</div>
          <div class="text-sm text-[#F5F5F5]/80 font-medium mb-4">Total Emails</div>

          <div class="grid grid-cols-2 gap-3">
            <div class="bg-[#7e9dbf] p-3 rounded-xl hover:bg-[#FF6B35]/15 transition-all">
              <div class="text-[#003366] text-sm font-medium mb-1">Internal (DC.gov)</div>
              <div class="font-semibold text-[#003366] text-lg">{{ stats.emailStats.internal }}</div>
            </div>
            <div class="bg-[#7e9dbf] p-3 rounded-xl hover:bg-[#FF6B35]/15 transition-all">
              <div class="text-[#003366] text-sm font-medium mb-1">External</div>
              <div class="font-semibold text-[#003366] text-lg">{{ stats.emailStats.external }}</div>
            </div>
          </div>
        </div>

        <!-- Media Communications -->
        <div class="bg-[#dd8373] rounded-2xl p-5 border border-[#2AB7CA]/10 hover:shadow-lg transition-all">
          <div class="flex items-center gap-2 text-sm font-medium text-[#F5F5F5] mb-3">
            <svg class="w-5 h-5 text-[#F5F5F5]" viewBox="0 0 24 24" fill="#003366">
              <path d="M12 7.5a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" />
              <path fill-rule="evenodd" d="M1.5 4.875C1.5 3.839 2.34 3 3.375 3h17.25c1.035 0 1.875.84 1.875 1.875v9.75c0 1.036-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 011.5 14.625v-9.75zM8.25 9.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0z" />
            </svg>
            <span class="font-semibold text-[#003366]">Media Communications</span>
          </div>

          <div class="text-5xl font-bold text-[#F5F5F5] mb-2 font-display tracking-tight">{{ stats.mediaStats.totalMediaEmails }}</div>
          <div class="text-sm text-[#F5F5F5] font-medium mb-4">Total Media Outlet Emails</div>

          <div class="grid grid-cols-2 gap-3">
            <div class="bg-[#7e9dbf] p-3 rounded-xl hover:bg-[#2AB7CA]/15 transition-all">
              <div class="text-[#003366] text-sm font-medium mb-1">Top Media Outlet</div>
              <div class="font-semibold text-[#003366] text-lg">{{ stats.mediaStats.topMediaOutlet.domain }}</div>
            </div>
            <div class="bg-[#7e9dbf] p-3 rounded-xl hover:bg-[#2AB7CA]/15 transition-all">
              <div class="text-[#003366] text-sm font-medium mb-1">Active Media Outlets</div>
              <div class="font-semibold text-[#003366] text-lg">{{ stats.mediaStats.mediaOutletCount }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Visualization Grid -->
      <div class="grid grid-cols-4 gap-6">
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Entity Relationship Network</h3>
          <EntityNetwork />
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Domain Communication Heatmap</h3>
          <DomainHeatmap />
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Email Domain Distribution</h3>
          <DomainBarChart />
        </div>
        
        <!-- New Topic Visualizations -->
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic UMAP Analysis</h3>
          <TopicUMAP />
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic t-SNE Analysis</h3>
          <TopicTSNE />
        </div>
        <div class="bg-white rounded-2xl border border-gray-100 p-6 col-span-2">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Topic Similarity Network</h3>
          <TopicSimilarityNetwork />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEmailStats } from '~/composables/useEmailStats'
import DomainBarChart from '~/components/visualizations/DomainBarChart.vue'
import DomainHeatmap from '~/components/visualizations/DomainHeatmap.vue'
import EntityNetwork from '~/components/visualizations/EntityNetwork.vue'
import TopicUMAP from '~/components/visualizations/TopicUMAP.vue'
import TopicTSNE from '~/components/visualizations/TopicTSNE.vue'
import TopicSimilarityNetwork from '~/components/visualizations/TopicSimilarityNetwork.vue'
import Sidebar from '~/components/Sidebar.vue'

const { fetchData, stats } = useEmailStats()

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.rounded-2xl {
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