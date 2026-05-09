<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PostMeta } from '@/types/post'
import { api } from '@/api'

const props = defineProps<{ slug: string }>()

const related = ref<PostMeta[]>([])

onMounted(async () => {
  try {
    const res = await api(`/api/posts/${encodeURIComponent(props.slug)}/related`)
    if (res.ok) {
      related.value = await res.json()
    }
  } catch { /* ignore */ }
})
</script>

<template>
  <div v-if="related.length > 0" class="mt-12 border-t border-gray-200 dark:border-gray-700 pt-8">
    <h3 class="text-lg font-bold mb-4">相关推荐</h3>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <router-link
        v-for="r in related"
        :key="r.slug"
        :to="`/post/${r.slug}`"
        class="p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary/30 dark:hover:border-primary/30 transition-all hover:shadow-sm"
      >
        <h4 class="font-medium text-sm mb-1 line-clamp-2">{{ r.title }}</h4>
        <p class="text-xs text-gray-400">{{ r.date }}</p>
        <div class="flex flex-wrap gap-1 mt-2">
          <span v-for="t in r.tags.slice(0, 2)" :key="t" class="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-500">{{ t }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>
