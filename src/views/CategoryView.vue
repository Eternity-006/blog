<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'

const route = useRoute()
const allPosts = ref<PostMeta[]>([])
const loading = ref(true)

const category = computed(() => route.params.category as string)

const posts = computed(() =>
  allPosts.value
    .filter(p => p.category === category.value)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
)

onMounted(async () => {
  try {
    const res = await fetch('/posts-index.json')
    allPosts.value = await res.json()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <router-link to="/" class="text-sm text-gray-500 hover:text-primary transition-colors mb-4 inline-block">
      ← 返回首页
    </router-link>
    <h1 class="text-3xl font-bold mb-2">分类：{{ category }}</h1>
    <p class="text-gray-500 dark:text-gray-400 mb-8">共 {{ posts.length }} 篇文章</p>

    <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>
    <PostList v-else :posts="posts" />
  </div>
</template>
