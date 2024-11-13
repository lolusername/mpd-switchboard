<template>
  <div class="relative w-full h-full flex flex-col">
    <div ref="chartContainer" class="h-[calc(100%-80px)] rounded-lg"></div>
    
    <!-- Vertical legend -->
    <div class="flex flex-col gap-2 p-2 mt-1 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-1.5">
        <div class="flex items-center gap-0.5">
          <div class="w-2.5 h-2.5 rounded-full bg-[var(--viz-secondary)]"></div>
          <div class="w-3.5 h-3.5 rounded-full bg-[var(--viz-secondary)]"></div>
          <div class="w-4.5 h-4.5 rounded-full bg-[var(--viz-secondary)]"></div>
        </div>
        <div class="whitespace-nowrap">
          <span class="font-medium">Domain Size:</span>
          <span class="text-gray-600 ml-1">Emails in domain</span>
        </div>
      </div>
      
      <div class="flex items-center gap-1.5">
        <div class="w-6 h-[2px] bg-[var(--viz-secondary)]"></div>
        <div class="whitespace-nowrap">
          <span class="font-medium">Connections:</span>
          <span class="text-gray-600 ml-1">Email communication</span>
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
  // Get connection data
  const connectionData = await fetch('/d3_data/domain_heatmap.json').then(res => res.json())
  
  // Get domain stats
  let domainStats = await fetch('/d3_data/domain_bar_chart.json').then(res => res.json())
  
  // Fix all .corn domains to .com and deduplicate in one step
  domainStats = Array.from(new Map(
    domainStats.map(node => [
      node.domain.replace('.corn', '.com'),
      {
        ...node,
        domain: node.domain.replace('.corn', '.com')
      }
    ])
  ).values())

  // Also fix domains in the connection matrix
  connectionData.domains = connectionData.domains.map(domain => domain.replace('.corn', '.com'))

  // Now use connectionData.matrix for the links and domainStats for the nodes

  // Set up dimensions
  const margin = { top: 20, right: 20, bottom: 20, left: 20 }
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = 350 - margin.top - margin.bottom
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
    .domain([0, d3.max(domainStats, d => d.count)])
    .range([4, 30])

  const flowWidth = d3.scaleLinear()
    .domain([0, d3.max(connectionData.matrix.flat())])
    .range([2, 20])

  // Adjust force simulation to radiate from center
  const simulation = d3.forceSimulation(domainStats)
    .force('charge', d3.forceManyBody().strength(-200)) // Reduced strength for less repulsion
    .force('center', d3.forceCenter(centerX, centerY))
    .force('collision', d3.forceCollide().radius(45)) // Fixed radius for more even spacing
    .force('radial', d3.forceRadial(120, centerX, centerY).strength(0.6)) // Adjusted radius and strength for better circle
    .on('tick', ticked)

  // Keep dc.gov fixed in center but let others move
  domainStats.forEach(node => {
    if (node.domain === 'dc.gov') {
      node.fx = centerX
      node.fy = centerY
    } else {
      node.fx = null
      node.fy = null
    }
  })

  // Add links
  const links = svg.selectAll('line')
    .data(connectionData.matrix.flatMap((row, i) => 
      row.map((value, j) => ({
        source: domainStats[i],
        target: domainStats[j],
        value: value
      })).filter(d => d.value > 0)
    ))
    .join('line')
    .attr('stroke', 'var(--viz-secondary)')
    .attr('stroke-opacity', 0.2)
    .attr('stroke-width', d => flowWidth(d.value))

  // Add nodes
  const nodes = svg.selectAll('g')
    .data(domainStats)
    .join('g')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))

  // Add circles to nodes
  nodes.append('circle')
    .attr('r', d => Math.sqrt(d.count) * 4)
    .attr('fill', d => d.domain === 'dc.gov' ? 'var(--viz-secondary)' : 'white')
    .attr('fill-opacity', d => d.domain === 'dc.gov' ? 1 : 0.1)
    .attr('stroke', 'var(--viz-secondary)')
    .attr('stroke-width', 1)

  // Add count labels
  nodes.append('text')
    .text(d => d.count)
    .attr('text-anchor', 'middle')
    .attr('dy', '.3em')
    .attr('font-size', '12px')
    .attr('fill', d => d.domain === 'dc.gov' ? 'white' : 'var(--viz-secondary)')

  // Add domain labels
  nodes.append('text')
    .text(d => d.domain)
    .attr('text-anchor', 'middle')
    .attr('dy', d => Math.sqrt(d.count) * 4 + 20)
    .attr('font-size', '12px')
    .attr('fill', '#666')

  function ticked() {
    links
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)

    nodes
      .attr('transform', d => `translate(${d.x},${d.y})`)
  }

  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    event.subject.fx = event.subject.x
    event.subject.fy = event.subject.y
  }

  function dragged(event) {
    event.subject.fx = event.x
    event.subject.fy = event.y
  }

  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0)
    event.subject.fx = null
    event.subject.fy = null
  }
})
</script>

<style scoped>
.domain-heatmap {
  width: 100%;
  height: 100%;
}
</style> 