<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PostMeta } from '@/types/post'
import PostCard from './PostCard.vue'
import Pagination from './Pagination.vue'

const props = defineProps<{
  posts: PostMeta[]
  pageSize?: number
  totalPages?: number
  currentPage?: number
}>()

const emit = defineEmits<{
  'page-change': [page: number]
}>()

const localPageSize = props.pageSize || 5
const localCurrentPage = ref(1)

const isServerPaginated = computed(() => props.totalPages !== undefined && props.currentPage !== undefined)

const displayPosts = computed(() => {
  if (isServerPaginated.value) return props.posts
  const start = (localCurrentPage.value - 1) * localPageSize
  return props.posts.slice(start, start + localPageSize)
})

const displayTotalPages = computed(() => {
  if (isServerPaginated.value) return props.totalPages!
  return Math.ceil(props.posts.length / localPageSize)
})

const displayCurrentPage = computed(() => {
  if (isServerPaginated.value) return props.currentPage!
  return localCurrentPage.value
})

function onPageChange(page: number) {
  if (isServerPaginated.value) {
    emit('page-change', page)
  } else {
    localCurrentPage.value = page
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}
</script>

<template>
  <div>
    <div v-if="posts.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
      <p class="text-lg">暂无文章。</p>
    </div>

    <div v-else class="space-y-6">
      <PostCard v-for="post in displayPosts" :key="post.slug" :post="post" />
    </div>

    <Pagination
      v-if="displayTotalPages > 1"
      :current-page="displayCurrentPage"
      :total-pages="displayTotalPages"
      @page-change="onPageChange"
    />
  </div>
</template>
