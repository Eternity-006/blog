<script setup lang="ts">
defineProps<{ headings: { id: string; text: string; level: number }[] }>()
</script>

<template>
  <nav v-if="headings.length > 0" class="toc p-4 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
    <h4 class="text-sm font-semibold mb-3 text-gray-700 dark:text-gray-300">目录</h4>
    <ul class="space-y-1.5">
      <li v-for="h in headings" :key="h.id" :style="{ paddingLeft: (h.level - 1) * 12 + 'px' }">
        <a
          :href="'#' + h.id"
          class="text-sm text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary transition-colors block py-0.5"
        >
          {{ h.text }}
        </a>
      </li>
    </ul>
  </nav>
</template>
