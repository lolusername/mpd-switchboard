<template>
  <div ref="chartContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)

onMounted(async () => {
  const data = await fetch('/d3_data/domain_heatmap.json').then(res => res.json())
  
  const width = chartContainer.value.clientWidth
  const height = 400
  const margin = { top: 50, right: 50, bottom: 100, left: 100 }
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleBand()
    .range([0, width - margin.left - margin.right])
    .domain(data.domains)
    .padding(0.05)

  const y = d3.scaleBand()
    .range([0, height - margin.top - margin.bottom])
    .domain(data.domains)
    .padding(0.05)

  const color = d3.scaleSequential()
    .interpolator(d3.interpolateReds)
    .domain([0, d3.max(data.matrix.flat())])

  // Create the heatmap cells
  for (let i = 0; i < data.domains.length; i++) {
    for (let j = 0; j < data.domains.length; j++) {
      svg.append('rect')
        .attr('x', x(data.domains[i]))
        .attr('y', y(data.domains[j]))
        .attr('width', x.bandwidth())
        .attr('height', y.bandwidth())
        .style('fill', color(data.matrix[i][j]))
    }
  }

  // Add the axes
  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end')

  svg.append('g')
    .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end')
})
</script> 