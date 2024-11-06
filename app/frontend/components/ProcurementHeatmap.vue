<template>
  <div class="procurement-heatmap">
    <h3>Procurement Activity Heatmap</h3>
    <div ref="heatmapContainer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const heatmapContainer = ref(null)
const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

onMounted(() => {
  const margin = { top: 30, right: 30, bottom: 50, left: 150 }
  const width = 600 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  const svg = d3.select(heatmapContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Convert procurement summary to array
  const data = Object.entries(props.data.procurement_summary)
    .map(([term, count]) => ({ term, count }))
    .sort((a, b) => b.count - a.count)

  // Color scale
  const colorScale = d3.scaleSequential()
    .domain([0, d3.max(data, d => d.count)])
    .interpolator(d3.interpolateBlues)

  // Create cells
  svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('y', (d, i) => i * 30)
    .attr('width', d => (d.count / d3.max(data, d => d.count)) * width)
    .attr('height', 25)
    .attr('fill', d => colorScale(d.count))

  // Add labels
  svg.selectAll('text')
    .data(data)
    .enter()
    .append('text')
    .attr('x', -10)
    .attr('y', (d, i) => i * 30 + 15)
    .attr('text-anchor', 'end')
    .text(d => d.term)
})
</script> 