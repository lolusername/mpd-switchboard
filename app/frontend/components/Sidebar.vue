<template>
  <div class="fixed left-0 top-0 h-full w-48 bg-white border-r border-gray-100 flex flex-col py-4">
    <!-- Logo section -->
    <div class="w-full px-6">
      <NuxtLink to="/" class="logo-wrapper block mb-3">
        <img 
          src="/logo.png" 
          alt="D4BL Logo" 
          class="w-full object-contain logo-main"
        />
      </NuxtLink>
      <div class="brand-label w-full flex justify-center">
        <span class="font-mono pt-1 font-bold bold text-[11px] tracking-[0.25em] text-neutral-600 uppercase">Switchboard</span>
      </div>
    </div>

    <!-- Divider -->
    <div class="mt-6 mb-8">
      <div class="h-px w-full bg-gradient-to-r from-transparent via-neutral-200 to-transparent"></div>
    </div>

    <!-- Navigation section -->
    <div class="flex flex-col items-center gap-3">
      <NuxtLink 
        to="/" 
        :class="[
          'w-full px-6 py-2.5 rounded-lg transition-colors flex items-center gap-3',
          $route.path === '/' ? 'bg-[--viz-primary]/10' : 'hover:bg-gray-50'
        ]"
      >
        <svg 
          class="w-5 h-5" 
          :class="$route.path === '/' ? 'text-[--viz-primary]' : 'text-gray-400'"
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor"
        >
          <path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span :class="$route.path === '/' ? 'text-[--viz-primary]' : 'text-gray-600'">Home</span>
      </NuxtLink>

      <NuxtLink 
        to="/search" 
        :class="[
          'w-full px-6 py-2.5 rounded-lg transition-colors flex items-center gap-3',
          $route.path === '/search' ? 'bg-[--viz-primary]/10' : 'hover:bg-gray-50'
        ]"
      >
        <svg 
          class="w-5 h-5" 
          :class="$route.path === '/search' ? 'text-[--viz-primary]' : 'text-gray-400'"
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor"
        >
          <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span :class="$route.path === '/search' ? 'text-[--viz-primary]' : 'text-gray-600'">Search</span>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.logo-wrapper {
  position: relative;
  overflow: hidden;
}

.logo-main {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  filter: brightness(1);
}

.logo-wrapper:hover .logo-main {
  filter: brightness(1.1);
  transform: scale(1.02);
}

.brand-label {
  position: relative;
  height: 22px;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 3px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  margin: 0 -2px; /* Negative margin to compensate for padding */
}

.brand-label span {
  transform: translateY(-1px);
  font-feature-settings: "tnum", "zero";
}

/* Subtle interaction */


.brand-label:hover span {
  color: #000000;
}
</style> 