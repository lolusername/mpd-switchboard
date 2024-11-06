<template>
  <div class="relative w-full h-full flex flex-col">
    <div ref="chartContainer" class="h-[450px]"></div>
    
    <!-- Legend -->
    <div class="flex items-center justify-start gap-8 p-3 mt-auto bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="w-24 h-1 bg-[--viz-primary]"></div>
        <div>
          <span class="font-medium">Email Flow:</span>
          <span class="text-gray-600 ml-1">Width = Volume of communication</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div class="w-5 h-5 rounded-full border-2 border-red-500"></div>
        <div>
          <span class="font-medium">Domain Size:</span>
          <span class="text-gray-600 ml-1">Circle area = Total emails</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)

onMounted(async () => {
  const data = await fetch('/d3_data/domain_heatmap.json').then(res => res.json())
  
  // Fix the typo'd domains
  data.domains = data.domains.map(domain => domain.replace('.corn', '.com'))
  
  const stats = await fetch('/d3_data/domain_bar_chart.json').then(res => res.json())
  
  // Set up dimensions
  const margin = { top: 20, right: 20, bottom: 40, left: 20 }
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = 450 - margin.top - margin.bottom
  const centerX = width / 2
  const centerY = height / 2

  // Clear existing
  d3.select(chartContainer.value).selectAll('*').remove()
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const size = d3.scaleSqrt()
    .domain([0, d3.max(stats, d => d.count)])
    .range([4, 30])

  const flowWidth = d3.scaleLinear()
    .domain([0, d3.max(data.matrix.flat())])
    .range([2, 20])

  // Calculate positions - dc.gov in center, others in orbit
  const angleStep = (2 * Math.PI) / (data.domains.length - 1)
  const radius = Math.min(width, height) / 3
  
  const positions = new Map()
  let currentAngle = -Math.PI / 2 // Start at top

  data.domains.forEach(domain => {
    if (domain === 'dc.gov') {
      positions.set(domain, { x: centerX, y: centerY })
    } else {
      positions.set(domain, {
        x: centerX + radius * Math.cos(currentAngle),
        y: centerY + radius * Math.sin(currentAngle)
      })
      currentAngle += angleStep
    }
  })

  // Draw flows first (under nodes)
  data.domains.forEach((source, i) => {
    data.domains.forEach((target, j) => {
      const value = data.matrix[i][j]
      if (value > 0) {
        const sourcePos = positions.get(source)
        const targetPos = positions.get(target)
        
        // Create gradient for flow
        const gradientId = `flow-gradient-${i}-${j}`
        const gradient = svg.append('defs')
          .append('linearGradient')
          .attr('id', gradientId)
          .attr('gradientUnits', 'userSpaceOnUse')
          .attr('x1', sourcePos.x)
          .attr('y1', sourcePos.y)
          .attr('x2', targetPos.x)
          .attr('y2', targetPos.y)

        gradient.append('stop')
          .attr('offset', '0%')
          .attr('stop-color', '#fee2e2') // red-100

        gradient.append('stop')
          .attr('offset', '100%')
          .attr('stop-color', '#327039') // red-600

        // Draw the flow
        svg.append('path')
          .attr('d', d3.linkHorizontal()({
            source: [sourcePos.x, sourcePos.y],
            target: [targetPos.x, targetPos.y]
          }))
          .attr('stroke', `url(#${gradientId})`)
          .attr('stroke-width', flowWidth(value))
          .attr('fill', 'none')
          .attr('opacity', 0.7)
      }
    })
  })

  // Helper function to check if domain is suspicious
  const isSuspiciousDomain = (domain) => {
    const originalDomain = domain.replace('.corn', '.com')
    return domain.endsWith('.corn') && data.domains.includes(originalDomain)
  }

  // Draw nodes
  data.domains.forEach(domain => {
    const pos = positions.get(domain)
    const domainStats = stats.find(d => d.domain === domain)
    const nodeSize = size(domainStats.count)
    const isSuspicious = isSuspiciousDomain(domain)

    // Node circle with conditional styling
    svg.append('circle')
      .attr('cx', pos.x)
      .attr('cy', pos.y)
      .attr('r', nodeSize)
      .attr('fill', domain === 'dc.gov' ? '#327039' : (isSuspicious ? '#fee2e2' : '#f3f4f6'))
      .attr('stroke', isSuspicious ? '#991b1b' : '#327039')
      .attr('stroke-width', isSuspicious ? 2 : 1.5)
      .attr('stroke-dasharray', isSuspicious ? '4,2' : 'none')

    // Domain label with conditional styling
    svg.append('text')
      .attr('x', pos.x)
      .attr('y', pos.y + nodeSize + 15)
      .attr('text-anchor', 'middle')
      .attr('font-size', '12px')
      .attr('fill', isSuspicious ? '#991b1b' : '#1f2937')
      .attr('font-weight', isSuspicious ? '600' : '400')
      .text(domain)
      
    // Add warning icon for suspicious domains
    if (isSuspicious) {
      svg.append('text')
        .attr('x', pos.x - nodeSize - 5)
        .attr('y', pos.y - nodeSize - 5)
        .attr('font-family', 'Arial')
        .attr('font-size', '14px')
        .attr('fill', '#991b1b')
        .attr('text-anchor', 'end')
        .text('⚠️')
        
      // Add "Possible typosquatting" label
      svg.append('text')
        .attr('x', pos.x)
        .attr('y', pos.y + nodeSize + 30)
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', '#991b1b')
        .attr('font-style', 'italic')
        .text('Possible typosquatting')
    }

    // Size label
    svg.append('text')
      .attr('x', pos.x)
      .attr('y', pos.y)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', '11px')
      .attr('fill', domain === 'dc.gov' ? 'white' : (isSuspicious ? '#991b1b' : '#4b5563'))
      .text(domainStats.count)
  })

  // Update legend to include suspicious domain indicator
  const legend = d3.select(chartContainer.value)
    .select('.legend')
    .append('div')
    .attr('class', 'flex items-center gap-2 ml-8')
    
  legend.append('div')
    .attr('class', 'w-5 h-5 rounded-full border-2 border-red-800 bg-red-50')
    .style('border-style', 'dashed')
    
  legend.append('div')
    .html(`
      <span class="font-medium">Suspicious Domain:</span>
      <span class="text-gray-600 ml-1">Possible typosquatting (.corn)</span>
    `)
})
</script>

<style scoped>
text {
  pointer-events: none;
}

/* Ensure the container properly contains all elements */
.relative {
  min-height: 500px;
}
</style> 