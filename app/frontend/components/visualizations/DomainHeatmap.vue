<template>
  <div class="relative w-full h-full flex flex-col">
    <div ref="chartContainer" class="h-[500px]"></div>
    
    <!-- Legend -->
    <div class="flex items-center justify-start gap-8 p-3 mt-2 bg-white rounded-lg text-xs border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="flex items-center gap-1">
          <div class="w-4 h-4 bg-red-100"></div>
          <div class="w-4 h-4 bg-red-300"></div>
          <div class="w-4 h-4 bg-red-500"></div>
          <div class="w-4 h-4 bg-red-700"></div>
        </div>
        <div>
          <span class="font-medium">Email Volume:</span>
          <span class="text-gray-600 ml-1">Darker = More communications</span>
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
  
  // Process matrix data into the format we need
  const matrixData = []
  data.matrix.forEach((row, i) => {
    row.forEach((value, j) => {
      if (value > 0) {  // Only include non-zero values
        matrixData.push({
          source: data.domains[i],
          target: data.domains[j],
          value: value
        })
      }
    })
  })
  
  // Filter for top communicating domains (e.g., top 10)
  const domainCounts = {}
  matrixData.forEach(d => {
    domainCounts[d.source] = (domainCounts[d.source] || 0) + d.value
    domainCounts[d.target] = (domainCounts[d.target] || 0) + d.value
  })
  
  const topDomains = Object.entries(domainCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(d => d[0])

  // Filter matrix data for top domains
  const significantData = matrixData.filter(d => 
    topDomains.includes(d.source) && topDomains.includes(d.target)
  )

  const width = chartContainer.value.clientWidth
  const height = chartContainer.value.clientHeight
  const margin = { top: 50, right: 50, bottom: 120, left: 120 }
  
  // Clear existing content
  d3.select(chartContainer.value).selectAll('*').remove()
  
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // Create scales
  const x = d3.scaleBand()
    .range([0, width - margin.left - margin.right])
    .domain(topDomains)
    .padding(0.05)

  const y = d3.scaleBand()
    .range([0, height - margin.top - margin.bottom])
    .domain(topDomains)
    .padding(0.05)

  // Create color scale
  const maxValue = d3.max(significantData, d => d.value)
  const color = d3.scaleSequential()
    .interpolator(d3.interpolateReds)
    .domain([0, maxValue])

  // Create the heatmap cells
  svg.selectAll('rect')
    .data(significantData)
    .join('rect')
    .attr('x', d => x(d.source))
    .attr('y', d => y(d.target))
    .attr('width', x.bandwidth())
    .attr('height', y.bandwidth())
    .style('fill', d => color(d.value))
    .attr('rx', 2)
    .on('mouseover', function(event, d) {
      d3.select(this).style('stroke', '#000').style('stroke-width', 2)
      // Show tooltip
      const tooltip = d3.select(chartContainer.value)
        .append('div')
        .attr('class', 'tooltip')
        .style('position', 'absolute')
        .style('background', 'white')
        .style('padding', '8px')
        .style('border-radius', '4px')
        .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .html(`
          <strong>${d.source}</strong> → <strong>${d.target}</strong><br/>
          ${d.value} emails
        `)
        .style('left', `${event.pageX + 10}px`)
        .style('top', `${event.pageY - 10}px`)
    })
    .on('mouseout', function() {
      d3.select(this).style('stroke', 'none')
      d3.selectAll('.tooltip').remove()
    })

  // Add value labels
  svg.selectAll('.value-label')
    .data(significantData)
    .join('text')
    .attr('class', 'value-label')
    .attr('x', d => x(d.source) + x.bandwidth()/2)
    .attr('y', d => y(d.target) + y.bandwidth()/2)
    .attr('dy', '.35em')
    .attr('text-anchor', 'middle')
    .style('fill', d => d.value > maxValue/2 ? 'white' : 'black')
    .style('font-size', '11px')
    .text(d => d.value)

  // Add axes
  svg.append('g')
    .style('font-size', '12px')
    .call(d3.axisLeft(y))
    .selectAll('text')
    .attr('transform', 'rotate(-30)')
    .style('text-anchor', 'end')

  svg.append('g')
    .style('font-size', '12px')
    .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .attr('transform', 'rotate(-30)')
    .style('text-anchor', 'end')

  // Add axis labels
  svg.append('text')
    .attr('x', -height/2 + margin.top)
    .attr('y', -margin.left + 20)
    .attr('transform', 'rotate(-90)')
    .style('text-anchor', 'middle')
    .style('font-size', '14px')
    .text('From Domain')

  svg.append('text')
    .attr('x', width/2 - margin.left)
    .attr('y', height - margin.top - margin.bottom + 80)
    .style('text-anchor', 'middle')
    .style('font-size', '14px')
    .text('To Domain')
})
</script>

<style scoped>
.value-label {
  pointer-events: none;
}
</style> 