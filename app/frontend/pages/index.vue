<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Sidebar -->
    <div class="fixed left-0 top-0 h-full w-16 bg-white border-r border-gray-100 flex flex-col items-center py-4 space-y-6">
      <div class="text-red-500 font-bold text-xs tracking-wider">
        D4BL
      </div>
      <button class="p-2">
        <svg class="w-6 h-6 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <button class="p-2">
        <svg class="w-6 h-6 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2z" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <!-- Main Content -->
    <div class="ml-16 p-8">
      <!-- Header -->
      <div class="flex justify-between items-start mb-8">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">FOIA Documents</h1>
        </div>
        <div class="flex items-center gap-4">
         
          <div class="flex gap-2">
            <button class="p-2 hover:bg-gray-100 rounded-full">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M12 6v6m0 0v6m0-6h6m-6 0H6" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
            <NuxtLink to="/search" class="p-2 hover:bg-gray-100 rounded-full">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-4 gap-4 mb-8">
        <!-- Total Emails -->
        <div class="bg-red-50 rounded-2xl p-4">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span class="text-sm font-medium text-red-900">Total Documents</span>
          </div>
          <div class="font-mono font-bold text-xl text-red-500">135,646</div>
          <div class="mt-2 h-1 w-full bg-red-100 rounded-full">
            <div class="h-full bg-red-500 rounded-full" style="width: 75%"></div>
          </div>
        </div>

        <!-- Active Domains -->
        <div class="bg-blue-50 rounded-2xl p-4">
          <div class="flex items-center gap-2 mb-2">
            <svg class="w-4 h-4 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" stroke-width="2"/>
            </svg>
            <span class="text-sm font-medium text-blue-900">Active Domains</span>
          </div>
          <div class="font-mono font-bold text-xl text-blue-500">142</div>
          <div class="mt-2 h-1 w-full bg-blue-100 rounded-full">
            <div class="h-full bg-blue-500 rounded-full" style="width: 60%"></div>
          </div>
        </div>

        <!-- Peak Traffic -->


        <!-- Connected Agencies -->
 
      </div>

      <!-- Visualization Grid -->
      <div class="grid grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl border border-gray-100 p-6">
          <h3 class="text-sm font-medium text-gray-900 mb-4">Email Domain Distribution</h3>
          <DomainBarChart class="h-[400px]" />
        </div>
        
        <div class="bg-white rounded-2xl border border-gray-100 p-6"">
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
import DomainBarChart from '~/components/visualizations/DomainBarChart.vue'
import DomainNetwork from '~/components/visualizations/DomainNetwork.vue'
import DomainHeatmap from '~/components/visualizations/DomainHeatmap.vue'
import EntityNetwork from '~/components/visualizations/EntityNetwork.vue'
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