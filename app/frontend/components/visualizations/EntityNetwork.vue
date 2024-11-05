<template>
  <div ref="chartContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)

onMounted(async () => {
  const data = await fetch('/d3_data/entity_network.json').then(res => res.json())
  
  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight
  const padding = 50 // Padding from container edges
  
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
    .range([5, Math.min(width, height) / 15])

  // Create simulation with adjusted forces
  const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.links)
      .id(d => d.id)
      .distance(d => sizeScale(d.source.size) + sizeScale(d.target.size) + 60)) // Dynamic distance based on node sizes
    .force('charge', d3.forceManyBody().strength(-200))
    .force('collision', d3.forceCollide().radius(d => sizeScale(d.size) + 30)) // Add padding between nodes
    .force('center', d3.forceCenter(0, 0))
    .force('x', d3.forceX().strength(0.1))
    .force('y', d3.forceY().strength(0.1))

  // Create links
  const link = svg.append('g')
    .selectAll('line')
    .data(data.links)
    .join('line')
    .attr('stroke', '#ef4444')
    .attr('stroke-opacity', 0.2)
    .attr('stroke-width', d => Math.sqrt(d.value/10000)) // Adjusted link thickness

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
    .attr('stroke-width', 1.5)

  // Add labels with background
  const labels = node.append('g')
    .attr('class', 'label')

  // Add white background for labels
  labels.append('text')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', d => sizeScale(d.size) + 15)
    .attr('fill', '#1f2937')
    .attr('stroke', '#ffffff')
    .attr('stroke-width', 4)
    .attr('stroke-linejoin', 'round')
    .style('font-size', '10px')
    .style('font-weight', '500')

  // Add text over background
  labels.append('text')
    .text(d => d.id)
    .attr('text-anchor', 'middle')
    .attr('dy', d => sizeScale(d.size) + 15)
    .attr('fill', '#1f2937')
    .style('font-size', '10px')
    .style('font-weight', '500')

  // Add tooltips
  node.append('title')
    .text(d => `${d.id}\nSize: ${d.size}`)

  // Update positions on simulation tick
  simulation.on('tick', () => {
    // Constrain nodes to container
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

  // Drag functions
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
    d.fx = null
    d.fy = null
  }
})
</script>

<style scoped>
.label text {
  pointer-events: none;
}
</style> 