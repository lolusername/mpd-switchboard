<template>
  <div ref="chartContainer" class="w-full h-full"></div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'

const chartContainer = ref(null)

onMounted(async () => {
  const data = await fetch('/d3_data/domain_bar_chart.json').then(res => res.json())
  
  const width = chartContainer.value.clientWidth
  const height = 400
  const margin = { top: 20, right: 20, bottom: 30, left: 120 }
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const x = d3.scaleLinear()
    .range([0, width - margin.left - margin.right])
    .domain([0, d3.max(data, d => d.count)])

  const y = d3.scaleBand()
    .range([0, height - margin.top - margin.bottom])
    .domain(data.map(d => d.domain))
    .padding(0.1)

  svg.selectAll('rect')
    .data(data)
    .join('rect')
    .attr('y', d => y(d.domain))
    .attr('x', 0)
    .attr('height', y.bandwidth())
    .attr('width', d => x(d.count))
    .attr('fill', 'var(--viz-primary)')
    .attr('opacity', 0.9)
    .attr('rx', 4)

  svg.append('g')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .style('font-size', '12px')

  svg.append('g')
    .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
    .call(d3.axisBottom(x))
})
</script> 