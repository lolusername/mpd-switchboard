import { useFetch } from '#app'

export function useApi() {
  const config = useRuntimeConfig()

  const search = async (query) => {
    const { data, error } = await useFetch(`${config.public.apiBase}/search`, {
      method: 'POST',
      body: JSON.stringify({ query }),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (error.value) {
      console.error('API Error:', error.value)
      throw error.value
    }

    return data.value
  }

  return {
    search,
  }
}