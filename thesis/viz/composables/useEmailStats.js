import { ref, computed } from 'vue'

export function useEmailStats() {
  const rawDomainData = ref([])
  const networkData = ref(null)
  const heatmapData = ref(null)
  
  const fetchData = async () => {
  }


  return {
    fetchData,
    
  }
} 