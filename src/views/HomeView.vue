<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'

const posts = ref<PostMeta[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('/posts-index.json')
    posts.value = await res.json()
    posts.value.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  } catch {
    console.error('Failed to load posts index')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <section class="mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold mb-3">欢迎来到我的博客</h1>
      <p class="text-gray-600 dark:text-gray-400 text-lg">
        记录前端开发、技术探索与生活随想。
      </p>
    </section>

    <div v-if="loading" class="text-center py-12 text-gray-500">
      <p>加载文章中...</p>
    </div>

    <PostList v-else :posts="posts" />
  </div>
</template>
