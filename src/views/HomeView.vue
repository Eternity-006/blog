<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'
import SkeletonCard from '@/components/SkeletonCard.vue'
import { api } from '@/api'

const posts = ref<PostMeta[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)
const pageSize = 5

async function fetchFromJson() {
  const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
  const data = await res.json()
  posts.value = data.sort((a: PostMeta, b: PostMeta) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

async function fetchPosts(page: number) {
  try {
    const res = await api(`/api/posts?page=${page}&per_page=${pageSize}`)
    if (res.ok) {
      const data = await res.json()
      if (data.posts) {
        posts.value = data.posts
        totalPages.value = data.total_pages
        total.value = data.total
        currentPage.value = data.page
      } else {
        posts.value = data
      }
    } else {
      await fetchFromJson()
    }
  } catch {
    await fetchFromJson()
  } finally {
    loading.value = false
  }
}

function onPageChange(page: number) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
  fetchPosts(page)
}

onMounted(() => {
  fetchPosts(1)
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
      <p v-if="total > 0" class="text-sm text-gray-400 mt-1">共 {{ total }} 篇文章</p>
    </section>

    <div v-if="loading" class="space-y-6">
      <SkeletonCard v-for="i in 3" :key="i" />
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
