<template>
  <div class="relative w-full h-full flex flex-col">
    <!-- Main visualization container with explicit height -->
    <div ref="chartContainer" class="h-[500px]"></div>
    
    <!-- Legend at bottom, not overlapping -->
    <div class="flex items-center justify-start gap-8 p-3 mt-2 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-white">73</div>
        <div>
          <span class="font-medium">Email Domain Size:</span>
          <span class="text-gray-600 ml-1">Number of emails sent from domain</span>
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <div class="w-8 h-[2px] bg-red-500"></div>
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
  
  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight
  const padding = 80
  
  // Clear any existing SVG
  d3.select(chartContainer.value).selectAll('*').remove()
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width/2},${height/2})`)

  // Scale node sizes based on container size
  const maxSize = d3.max(data.nodes, d => d.size)
  const sizeScale = d3.scaleSqrt()
    .domain([0, maxSize])
    .range([20, Math.min(width, height) / 12])

  // Modified simulation with adjusted forces
  const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.links)
      .id(d => d.id)
      .distance(180))
    .force('charge', d3.forceManyBody().strength(-800))
    .force('collision', d3.forceCollide().radius(d => sizeScale(d.size) + 30))
    .force('center', d3.forceCenter(0, 0))
    .force('x', d3.forceX().strength(0.1))
    .force('y', d3.forceY().strength(0.1))

  // Create links
  const link = svg.append('g')
    .selectAll('line')
    .data(data.links)
    .join('line')
    .attr('stroke', '#ef4444')
    .attr('stroke-opacity', 0.4)
    .attr('stroke-width', d => Math.sqrt(d.value))

  // Create node groups
  const node = svg.append('g')
    .selectAll('g')
    .data(data.nodes)
    .join('g')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))

  // Add circles to nodes
  node.append('circle')
    .attr('r', d => sizeScale(d.size))
    .attr('fill', '#ef4444')
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)

  // Add email count labels
  node.append('text')
    .text(d => d.size)
    .attr('text-anchor', 'middle')
    .attr('dy', '0.3em')
    .attr('fill', '#ffffff')
    .style('font-size', '12px')
    .style('font-weight', '600')

  // Add domain labels with background
  node.append('text')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', d => sizeScale(d.size) + 20)
    .attr('fill', '#1f2937')
    .style('font-size', '12px')
    .style('font-weight', '500')
    .clone(true)
    .lower()
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 3)

  // Center dc.gov
  const dcGov = data.nodes.find(n => n.id === 'dc.gov')
  if (dcGov) {
    dcGov.fx = 0
    dcGov.fy = 0
  }

  simulation.on('tick', () => {
    // Constrain nodes to container bounds
    node.attr('transform', d => {
      d.x = Math.max(-width/2 + padding, Math.min(width/2 - padding, d.x))
      d.y = Math.max(-height/2 + padding, Math.min(height/2 - padding, d.y))
      return `translate(${d.x},${d.y})`
    })

    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
  })

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart()
    d.fx = d.x
    d.fy = d.y
  }

  function dragged(event, d) {
    d.fx = event.x
    d.fy = event.y
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0)
    if (d.id !== 'dc.gov') {
      d.fx = null
      d.fy = null
    }
  }
})
</script>

<style scoped>
text {
  pointer-events: none;
}
</style> 