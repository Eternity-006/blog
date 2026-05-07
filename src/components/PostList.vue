<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PostMeta } from '@/types/post'
import PostCard from './PostCard.vue'

const props = defineProps<{ posts: PostMeta[]; pageSize?: number }>()

const pageSize = props.pageSize || 5
const currentPage = ref(1)

const totalPages = computed(() => Math.ceil(props.posts.length / pageSize))

const paginatedPosts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return props.posts.slice(start, start + pageSize)
})

function goPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const visiblePages = computed(() => {
  const pages: (number | string)[] = []
  const total = totalPages.value
  const cur = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('...')
    for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) {
      pages.push(i)
    }
    if (cur < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})
</script>

<template>
  <div>
    <div v-if="posts.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <p class="text-lg">暂无文章。</p>
    </div>

    <div v-else class="space-y-6">
      <PostCard v-for="post in paginatedPosts" :key="post.slug" :post="post" />
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1" class="flex justify-center items-center gap-2 mt-10">
      <button
        @click="goPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="px-3 py-1.5 rounded-lg text-sm border border-gray-300 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        ← 上一页
      </button>
      <template v-for="page in visiblePages" :key="page">
        <span v-if="page === '...'" class="px-2 text-gray-400">...</span>
        <button
          v-else
          @click="goPage(page as number)"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm border transition-colors',
            currentPage === page
              ? 'bg-primary text-white border-primary'
              : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800',
          ]"
        >
          {{ page }}
        </button>
      </template>
      <button
        @click="goPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="px-3 py-1.5 rounded-lg text-sm border border-gray-300 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        下一页 →
      </button>
    </nav>
  </div>
</template>
