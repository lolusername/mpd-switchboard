<template>
  <div class="grid grid-cols-2 gap-4">
    <!-- Email Communication Stats -->
    <div class="bg-red-50/50 rounded-2xl p-6 border border-gray-100">
      <div class="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="currentColor">
          <path d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
          <path d="M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" />
        </svg>
        <span>Email Communications</span>
      </div>
      <div class="text-4xl font-bold text-gray-900 mb-1">76</div>
      <div class="text-sm text-gray-600">Internal DC.gov Emails</div>
      
      <div class="mt-4 space-y-2">
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-600">External Communications</span>
          <span class="font-medium text-gray-900">9 emails</span>
        </div>
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-600">Top External Domain</span>
          <span class="font-medium text-gray-900">nbcuni.com (73)</span>
        </div>
      </div>
    </div>

    <!-- Entity Mentions -->
    <div class="bg-blue-50/50 rounded-2xl p-6 border border-gray-100">
      <div class="flex items-center gap-2 text-sm font-medium text-gray-900 mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="currentColor">
          <path fill-rule="evenodd" d="M8.25 6.75a3.75 3.75 0 117.5 0 3.75 3.75 0 01-7.5 0zM15.75 9.75a3 3 0 116 0 3 3 0 01-6 0zM2.25 9.75a3 3 0 116 0 3 3 0 01-6 0zM6.31 15.117A6.745 6.745 0 0112 12a6.745 6.745 0 016.709 7.498.75.75 0 01-.372.568A12.696 12.696 0 0112 21.75c-2.305 0-4.47-.612-6.337-1.684a.75.75 0 01-.372-.568 6.787 6.787 0 011.019-4.38z" clip-rule="evenodd" />
          <path d="M5.082 14.254a8.287 8.287 0 00-1.308 5.135 9.687 9.687 0 01-1.764-.44l-.115-.04a.563.563 0 01-.373-.487l-.01-.121a3.75 3.75 0 013.57-4.047zM20.226 19.389a8.287 8.287 0 00-1.308-5.135 3.75 3.75 0 013.57 4.047l-.01.121a.563.563 0 01-.373.486l-.115.04c-.567.2-1.156.349-1.764.441z" />
        </svg>
        <span>Top Entity Mentions</span>
      </div>
      <div class="space-y-3">
        <div>
          <div class="text-sm text-gray-600">DC Government</div>
          <div class="text-xl font-bold text-gray-900">135,628</div>
        </div>
        <div>
          <div class="text-sm text-gray-600">OCTO</div>
          <div class="text-xl font-bold text-gray-900">135,297</div>
        </div>
        <div>
          <div class="text-sm text-gray-600">USA</div>
          <div class="text-xl font-bold text-gray-900">130,742</div>
        </div>
      </div>
    </div>
  </div>
</template> 