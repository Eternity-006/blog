<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import { api } from '@/api'

const route = useRoute()
const posts = ref<PostMeta[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)

const category = computed(() => route.params.category as string)

async function fetchPosts(page: number) {
  loading.value = true
  try {
    const res = await api(`/api/posts?category=${encodeURIComponent(category.value)}&page=${page}&per_page=5`)
    if (res.ok) {
      const data = await res.json()
      if (data.posts) {
        posts.value = data.posts
        totalPages.value = data.total_pages
        currentPage.value = data.page
      } else {
        posts.value = data
      }
    }
  } catch {
    try {
      const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
      const all = await res.json()
      posts.value = all.filter((p: PostMeta) => p.category === category.value)
    } catch { /* ignore */ }
  } finally {
    loading.value = false
  }
}

function onPageChange(page: number) {
  window.scrollTo({ top: 0, behavior: 'smooth' })
  fetchPosts(page)
}

onMounted(() => fetchPosts(1))

watch(() => route.params.category, () => {
  fetchPosts(1)
})
</script>

<template>
  <div>
    <router-link to="/" class="text-sm text-gray-500 hover:text-primary transition-colors mb-4 inline-block">
      &larr; 返回首页
    </router-link>
    <h1 class="text-3xl font-bold mb-2">分类：{{ category }}</h1>
    <p class="text-gray-500 dark:text-gray-400 mb-8">浏览此分类下的文章</p>

    <div v-if="loading" class="space-y-6">
      <SkeletonCard v-for="i in 2" :key="i" />
    </div>
    <PostList
      v-else
      :posts="posts"
      :current-page="currentPage"
      :total-pages="totalPages"
      @page-change="onPageChange"
    />
  </div>
</template>
