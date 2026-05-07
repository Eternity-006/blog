<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { PostMeta } from '@/types/post'
import { useSearch } from '@/composables/useSearch'
import PostCard from '@/components/PostCard.vue'
import TagBadge from '@/components/TagBadge.vue'

const route = useRoute()
const { searchQuery, results, setPosts } = useSearch()
const allPosts = ref<PostMeta[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
    allPosts.value = await res.json()
    setPosts(allPosts.value)
  } finally {
    loading.value = false
  }

  // Get query from URL
  const q = route.query.q as string
  if (q) {
    searchQuery.value = q
  }
})

watch(() => route.query.q, (q) => {
  searchQuery.value = (q as string) || ''
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-6">搜索</h1>

    <div class="mb-8">
      <input
        v-model="searchQuery"
        type="search"
        placeholder="搜索文章..."
        class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-lg"
        autofocus
      />
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>

    <div v-else>
      <p v-if="searchQuery" class="text-sm text-gray-500 dark:text-gray-400 mb-4">
        共 {{ results.length }} 条结果
      </p>

      <div class="space-y-6">
        <PostCard v-for="post in results" :key="post.slug" :post="post" />
      </div>

      <div v-if="searchQuery && results.length === 0" class="text-center py-12 text-gray-500">
        <p class="text-lg">未找到与 "{{ searchQuery }}" 相关的结果</p>
      </div>
    </div>
  </div>
</template>
