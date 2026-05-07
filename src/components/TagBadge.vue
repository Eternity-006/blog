<script setup lang="ts">
defineProps<{ tag: string; clickable?: boolean }>()
</script>

<template>
  <router-link
    v-if="clickable"
    :to="`/tag/${tag}`"
    class="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
  >
    #{{ tag }}
  </router-link>
  <span
    v-else
    class="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
  >
    #{{ tag }}
  </span>
</template>
