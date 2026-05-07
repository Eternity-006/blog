<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const query = ref('')

function goSearch() {
  if (query.value.trim()) {
    router.push({ name: 'search', query: { q: query.value.trim() } })
  }
}
</script>

<template>
  <form @submit.prevent="goSearch" class="relative">
    <input
      v-model="query"
      type="search"
      placeholder="搜索文章..."
      class="w-full sm:w-48 lg:w-64 px-3 py-1.5 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
    />
    <button type="submit" class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </button>
  </form>
</template>
