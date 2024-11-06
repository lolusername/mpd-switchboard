import { ref } from 'vue'

export function useFinancialStats() {
  const financialData = ref(null)
  const isLoading = ref(false)

  async function fetchFinancialData() {
    isLoading.value = true
    try {
      const response = await fetch('/d3_data/financial_data.json')
      financialData.value = await response.json()
    } catch (error) {
      console.error('Error fetching financial data:', error)
    } finally {
      isLoading.value = false
    }
  }

  return {
    financialData,
    isLoading,
    fetchFinancialData
  }
} 