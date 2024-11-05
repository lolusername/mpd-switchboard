<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Sidebar -->
    <div class="fixed left-0 top-0 h-full w-16 bg-white border-r border-gray-100 flex flex-col items-center py-4 space-y-6">
      <div class="text-red-500 font-bold text-xs tracking-wider">
        D4BL
      </div>
      <div class="p-2 bg-gray-100 rounded-full">
        <svg class="w-6 h-6 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </div>
      <NuxtLink to="/search" class="p-2 hover:bg-gray-100 rounded-full">
        <svg class="w-6 h-6 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </NuxtLink>
    </div>

    <!-- Main Content -->
    <div class="ml-16 p-8">
      <!-- Header -->
      <div class="flex justify-between items-start mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Email Analytics Dashboard</h1>
          <p class="text-gray-500 mt-1">Analyzing communication patterns across DC.gov domains</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-3 gap-4 mb-8" v-if="stats">
        <!-- Email Communications -->
        <div class="bg-red-50/50 rounded-2xl p-6 border border-gray-100">
          <div class="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <svg class="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
            </svg>
            <span>Email Communications</span>
          </div>
          <div class="text-4xl font-bold text-gray-900 mb-1">{{ stats.emailStats.total }}</div>
          <div class="text-sm text-gray-600">Total Emails</div>
          
          <div class="mt-4 space-y-2">
            <div class="flex justify-between items-center text-sm">
              <span class="text-gray-600">Internal (DC.gov)</span>
              <span class="font-medium text-gray-900">{{ stats.emailStats.internal }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-gray-600">External</span>
              <span class="font-medium text-gray-900">{{ stats.emailStats.external }}</span>
            </div>
          </div>
        </div>

        <!-- Media Communications -->
        <div class="bg-green-50/50 rounded-2xl p-6 border border-gray-100">
          <div class="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
            <svg class="w-5 h-5 text-green-500" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 7.5a2.25 2.25 0 100 4.5 2.25 2.25 0 000-4.5z" />
              <path fill-rule="evenodd" d="M1.5 4.875C1.5 3.839 2.34 3 3.375 3h17.25c1.035 0 1.875.84 1.875 1.875v9.75c0 1.036-.84 1.875-1.875 1.875H3.375A1.875 1.875 0 011.5 14.625v-9.75zM8.25 9.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0zM18.75 9a.75.75 0 00-.75.75v.008c0 .414.336.75.75.75h.008a.75.75 0 00.75-.75V9.75a.75.75 0 00-.75-.75h-.008zM4.5 9.75A.75.75 0 015.25 9h.008a.75.75 0 01.75.75v.008a.75.75 0 01-.75.75H5.25a.75.75 0 01-.75-.75V9.75z" />
            </svg>
            <span>Media Communications</span>
          </div>
          <div class="text-4xl font-bold text-gray-900 mb-1">{{ stats.mediaStats.totalMediaEmails }}</div>
          <div class="text-sm text-gray-600">Total Media Outlet Emails</div>
          
          <div class="mt-4 space-y-2">
            <div class="flex justify-between items-center text-sm">
              <span class="text-gray-600">Top Media Outlet</span>
              <span class="font-medium text-gray-900">{{ stats.mediaStats.topMediaOutlet.domain }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-gray-600">Active Media Outlets</span>
              <span class="font-medium text-gray-900">{{ stats.mediaStats.mediaOutletCount }}</span>
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
        
        <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Domain Communication Network</h3>
          <DomainNetwork class="h-[400px]" />
        </div>
        
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