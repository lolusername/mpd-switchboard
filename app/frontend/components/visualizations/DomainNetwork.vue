<template>
  <div class="relative w-full h-full flex flex-col">
    <h3 class="text-sm font-medium text-gray-900 mb-4">Domain Communication Heatmap</h3>
    <div ref="chartContainer" class="h-[300px] bg-blue-50 rounded-lg"></div>
    
    <!-- Legend -->
    <div class="flex items-center justify-start gap-8 p-3 mt-2 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1">
          <div class="w-3 h-3 rounded-full bg-emerald-600"></div>
          <div class="w-4 h-4 rounded-full bg-emerald-600"></div>
          <div class="w-5 h-5 rounded-full bg-emerald-600"></div>
        </div>
        <div>
          <span class="font-medium">Domain Size:</span>
          <span class="text-gray-600 ml-1">Number of emails in domain</span>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <div class="w-8 h-[2px] bg-emerald-600"></div>
        <div>
          <span class="font-medium">Connections:</span>
          <span class="text-gray-600 ml-1">Email communication between domains</span>
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
  const data = await fetch('/d3_data/domain_network.json').then(res => res.json())
  
  // Set dimensions
  const margin = { top: 20, right: 20, bottom: 20, left: 20 }
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = 300 - margin.top - margin.bottom
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

  // Create force simulation
  const simulation = d3.forceSimulation(data.nodes)
    .force('charge', d3.forceManyBody().strength(-400))
    .force('center', d3.forceCenter(centerX, centerY))
    .force('collision', d3.forceCollide().radius(45))
    .on('tick', ticked)

  // Add links
  const links = svg.selectAll('line')
    .data(data.links)
    .join('line')
    .attr('stroke', '#059669')
    .attr('stroke-opacity', 0.2)
    .attr('stroke-width', 1)

  // Add nodes
  const nodes = svg.selectAll('g')
    .data(data.nodes)
    .join('g')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))

  // Add circles to nodes
  nodes.append('circle')
    .attr('r', d => Math.sqrt(d.value) * 4)
    .attr('fill', d => d.id === 'dc.gov' ? '#059669' : 'white')
    .attr('fill-opacity', d => d.id === 'dc.gov' ? 1 : 0.1)
    .attr('stroke', '#059669')
    .attr('stroke-width', 1)

  // Add count labels
  nodes.append('text')
    .text(d => d.value)
    .attr('text-anchor', 'middle')
    .attr('dy', '.3em')
    .attr('font-size', '12px')
    .attr('fill', d => d.id === 'dc.gov' ? 'white' : '#059669')

  // Add domain labels
  nodes.append('text')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', d => Math.sqrt(d.value) * 4 + 15)
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
text {
  pointer-events: none;
}
</style> 