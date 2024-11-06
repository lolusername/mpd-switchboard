import { ref, computed } from 'vue'

export function useEmailStats() {
  const rawDomainData = ref([])
  const networkData = ref(null)
  const heatmapData = ref(null)
  
  const fetchData = async () => {
    const [domainResponse, networkResponse, heatmapResponse] = await Promise.all([
      fetch('/d3_data/domain_bar_chart.json'),
      fetch('/d3_data/domain_network.json'),
      fetch('/d3_data/domain_heatmap.json')
    ])
    
    rawDomainData.value = await domainResponse.json()
    networkData.value = await networkResponse.json()
    heatmapData.value = await heatmapResponse.json()
  }

  const stats = computed(() => {
    if (!rawDomainData.value.length) return null

    // Total email stats
    const dcGovEmails = rawDomainData.value.find(d => d.domain === 'dc.gov')?.count || 0
    const totalEmails = rawDomainData.value.reduce((sum, d) => sum + d.count, 0)

    // Media organization stats
    const mediaOrgs = ['nbcuni.com', 'cnn.com', 'politico.com', 'wusa9.com', 'bloomberg.net']
    const mediaStats = rawDomainData.value
      .filter(d => mediaOrgs.includes(d.domain))
      .sort((a, b) => b.count - a.count)
    
    // Communication patterns
    const directConnections = networkData.value?.links.length || 0
    const topConnectedPair = networkData.value?.links[0] || null

    return {
      emailStats: {
        total: totalEmails,
        internal: dcGovEmails,
        external: totalEmails - dcGovEmails
      },
      mediaStats: {
        totalMediaEmails: mediaStats.reduce((sum, d) => sum + d.count, 0),
        topMediaOutlet: mediaStats[0],
        mediaOutletCount: mediaStats.length
      },
      networkStats: {
        connections: directConnections,
        topConnection: topConnectedPair,
        topDomain: rawDomainData.value[0]
      }
    }
  })

  return {
    fetchData,
    stats
  }
} 