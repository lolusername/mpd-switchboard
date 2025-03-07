// https://nuxt.com/docs/api/configuration/nuxt-config
import { defineNuxtConfig } from 'nuxt/config'
import type { NuxtConfig } from '@nuxt/types'
import fs from 'fs'

export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
  css: ['~/assets/css/main.css', '~/assets/css/variables.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NODE_ENV === 'production' 
        ? 'https://switchboard.miski.studio/api'
        : 'http://localhost:3000/api'
    }
  },
  modules: [],  // Remove auth module for now
  routeRules: {
    '/': { middleware: ['auth'] },
    '/login': { middleware: [] }
  },
  server: process.env.HTTPS ? {
    https: {
      key: fs.readFileSync(process.env.SSL_KEY_FILE || ''),
      cert: fs.readFileSync(process.env.SSL_CRT_FILE || '')
    }
  } : undefined
})
