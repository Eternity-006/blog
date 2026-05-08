<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'

const posts = ref<PostMeta[]>([])
const loading = ref(true)

async function fetchFromJson() {
  const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
  const data = await res.json()
  posts.value = data.sort((a: PostMeta, b: PostMeta) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

onMounted(async () => {
  try {
    const res = await fetch('/api/posts')
    if (res.ok) {
      posts.value = await res.json()
    } else {
      await fetchFromJson()
    }
  } catch {
    await fetchFromJson()
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
