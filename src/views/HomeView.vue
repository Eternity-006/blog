<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import { api } from '@/api'

const posts = ref<PostMeta[]>([])
const loading = ref(true)

async function fetchFromJson() {
  const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
  const data = await res.json()
  posts.value = data.sort((a: PostMeta, b: PostMeta) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

onMounted(async () => {
  try {
    const res = await api('/api/posts')
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
      <h1 class="text-3xl sm:text-4xl font-bold mb-3 bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
        博客平台
      </h1>
      <p class="text-gray-600 dark:text-gray-400 text-lg">
        分享技术，记录生活，发现更多有趣的内容。
      </p>
    </section>

    <div v-if="loading" class="space-y-6">
      <SkeletonCard v-for="i in 3" :key="i" />
    </div>

    <PostList v-else :posts="posts" />
  </div>
</template>
