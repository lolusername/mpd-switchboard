<template>
  <div class="min-h-screen bg-[#F5F5F5]">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="ml-16 p-8">
      <!-- Header -->
      <div class="flex justify-between items-start mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-600">Email Analytics Dashboard</h1>
          <p class="text-gray-500 mt-1">Analyzing communication patterns across DC.gov domains</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-3 gap-4 mb-8" v-if="stats">
        <!-- Email Communications -->
        <div class="bg-[#FDF1E6] rounded-2xl p-6 border border-[#FA7358]/10 hover:shadow-lg transition-all">
          <div class="flex items-center gap-2 text-sm font-medium text-[#FA7358] mb-4">
            <svg class="w-5 h-5 text-[#FA7358]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
            </svg>
            <span class="font-semibold">Email Communications</span>
          </div>

          <div class="text-6xl font-bold text-[#FA7358] mb-2 font-display tracking-tight">{{ stats.emailStats.total }}
          </div>
          <div class="text-sm text-[#FA7358]/80 font-medium">Total Emails</div>

          <div class="mt-6 space-y-3">
            <div
              class="flex justify-between items-center text-sm bg-[#FAD4C2]/10 p-3 rounded-xl hover:bg-[#FF6B35]/15 transition-all">
              <span class="text-[#D35C36] font-medium">Internal (DC.gov)</span>
              <span class="font-semibold text-[#D35C36]">{{ stats.emailStats.internal }}</span>
            </div>
            <div
              class="flex justify-between items-center text-sm bg-[#FAD4C2]/10 p-3 rounded-xl hover:bg-[#FF6B35]/15 transition-all">
              <span class="text-[#D35C36] font-medium">External</span>
              <span class="font-semibold text-[#D35C36]">{{ stats.emailStats.external }}</span>
            </div>
          </div>
        </div>

        <!-- Media Communications -->
        <div
          class="bg-[#E5F7F6] rounded-2xl p-6 border border-[#2AB7CA]/10 hover:shadow-lg transition-all">
          <div class="flex items-center gap-2 text-sm font-medium text-[#238A87] mb-4">
            <svg class="w-5 h-5 text-[#2AB7CA]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 7.5a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" />
              <path fill-rule="evenodd"
                d="M1.5 4.875C1.5 3.839 2.34 3 3.375 3h17.25c1.035 0 1.875.84 1.875 1.875v9.75c0 1.036-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 011.5 14.625v-9.75zM8.25 9.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0z" />
            </svg>
            <span class="font-semibold">Media Communications</span>
          </div>

          <div class="text-6xl font-bold text-[#238A87] mb-2 font-display tracking-tight">{{
            stats.mediaStats.totalMediaEmails }}</div>
          <div class="text-sm text-[#238A87]/80 font-medium">Total Media Outlet Emails</div>

          <div class="mt-6 space-y-3">
            <div
              class="flex justify-between items-center text-sm bg-[#CDEDF0]/10 p-3 rounded-xl hover:bg-[#2AB7CA]/15 transition-all">
              <span class="text-[#238A87] font-medium">Top Media Outlet</span>
              <span class="font-semibold text-[#238A87]">{{ stats.mediaStats.topMediaOutlet.domain }}</span>
            </div>
            <div
              class="flex justify-between items-center text-sm bg-[#CDEDF0]/10 p-3 rounded-xl hover:bg-[#2AB7CA]/15 transition-all">
              <span class="text-[#238A87] font-medium">Active Media Outlets</span>
              <span class="font-semibold text-[#238A87]">{{ stats.mediaStats.mediaOutletCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Visualization Grid -->
      <div class="grid grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Email Domain Distribution</h3>
          <DomainBarChart class="h-[400px]" />
        </div>

        <!-- <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Domain Communication Network</h3>
          <DomainNetwork class="h-[400px]" />
        </div> -->

        <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Domain Communication Heatmap</h3>
          <DomainHeatmap class="h-[400px]" />
        </div>

        <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Entity Relationship Network</h3>
          <EntityNetwork class="h-[400px]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEmailStats } from '~/composables/useEmailStats'
import DomainBarChart from '~/components/visualizations/DomainBarChart.vue'
import DomainNetwork from '~/components/visualizations/DomainNetwork.vue'
import DomainHeatmap from '~/components/visualizations/DomainHeatmap.vue'
import EntityNetwork from '~/components/visualizations/EntityNetwork.vue'
import Sidebar from '../components/Sidebar.vue'

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
</style>