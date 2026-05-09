<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import { renderMarkdown, extractHeadings, estimateReadingTime } from '@/utils/markdown'
import type { Post } from '@/types/post'
import TagBadge from '@/components/TagBadge.vue'
import TOC from '@/components/TOC.vue'
import CommentSection from '@/components/CommentSection.vue'
import RelatedPosts from '@/components/RelatedPosts.vue'
import { api } from '@/api'
import { useCodeCopy } from '@/composables/useCodeCopy'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const { isLoggedIn, authHeaders } = useAuth()
const toast = useToast()
const post = ref<Post | null>(null)
const headings = ref<{ id: string; text: string; level: number }[]>([])
const loading = ref(true)
const error = ref('')
const progress = ref(0)
const favorited = ref(false)
const favoriteToggling = ref(false)

const readingTime = computed(() => {
  if (!post.value?.content) return 1
  return estimateReadingTime(post.value.content)
})

function onScroll() {
  const scrollTop = window.scrollY
  const docHeight = document.documentElement.scrollHeight - window.innerHeight
  progress.value = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0
}

async function checkFavorite(slug: string) {
  if (!isLoggedIn.value) return
  try {
    const res = await api(`/api/favorites/${slug}`, { headers: authHeaders() })
    if (res.ok) {
      const data = await res.json()
      favorited.value = data.favorited
    }
  } catch { /* ignore */ }
}

async function toggleFavorite() {
  if (!isLoggedIn.value) {
    toast.info('请先登录')
    return
  }
  favoriteToggling.value = true
  try {
    const res = await api(`/api/favorites/${route.params.slug as string}`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (res.ok) {
      const data = await res.json()
      favorited.value = data.favorited
      toast.success(data.favorited ? '已收藏' : '已取消收藏')
    }
  } catch {
    toast.error('操作失败')
  }
  favoriteToggling.value = false
}

onMounted(async () => {
  const slug = route.params.slug as string

  try {
    const res = await api(`/api/posts/${slug}`)
    if (res.ok) {
      const data = await res.json()
      const html = renderMarkdown(data.content)
      post.value = { ...data, html }
    } else if (res.status === 404) {
      error.value = '文章未找到。'
      loading.value = false
      return
    }
  } catch {
    try {
      const fallback = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
      const posts: Post[] = await fallback.json()
      post.value = posts.find(p => p.slug === slug) || null
    } catch { /* ignore */ }
  }

  if (!post.value) {
    if (!error.value) error.value = '文章未找到。'
    loading.value = false
    return
  }

  await nextTick()
  headings.value = extractHeadings(post.value.html)

  document.querySelectorAll<HTMLElement>('.prose h1, .prose h2, .prose h3').forEach((el) => {
    const text = el.textContent || ''
    const id = text.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9一-鿿\-]/g, '')
    el.id = id
  })

  useCodeCopy()
  document.title = `${post.value.title} | 博客平台`
  loading.value = false
  window.addEventListener('scroll', onScroll, { passive: true })

  checkFavorite(slug)
})
</script>

<template>
  <div class="fixed top-0 left-0 h-0.5 bg-gradient-to-r from-primary to-purple-500 z-[60] transition-all duration-150" :style="{ width: progress + '%' }" />

  <div v-if="loading" class="text-center py-20">
    <div class="animate-pulse space-y-4 max-w-2xl mx-auto">
      <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
      <div class="h-8 w-3/4 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
      <div class="h-4 w-1/2 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
      <div class="h-64 bg-gray-100 dark:bg-gray-800 rounded-xl mt-8" />
    </div>
  </div>

  <div v-else-if="error" class="text-center py-20">
    <p class="text-red-500 text-lg mb-4">{{ error }}</p>
    <router-link to="/" class="text-primary hover:underline">&larr; 返回首页</router-link>
  </div>

  <article v-else class="max-w-3xl mx-auto">
    <header class="mb-8">
      <router-link to="/" class="text-sm text-gray-500 hover:text-primary transition-colors mb-4 inline-block">
        &larr; 返回首页
      </router-link>

      <img
        v-if="post?.cover_image"
        :src="post.cover_image"
        :alt="post?.title"
        class="w-full max-h-80 object-cover rounded-xl mb-6"
      />

      <h1 class="text-3xl sm:text-4xl font-bold mb-4">{{ post?.title }}</h1>
      <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
        <router-link
          v-if="post?.author"
          :to="`/user/${post.author}`"
          class="text-primary hover:underline font-medium"
        >
          {{ post.author }}
        </router-link>
        <span v-if="post?.author">|</span>
        <router-link :to="`/category/${post?.category}`" class="text-primary hover:underline font-medium">
          {{ post?.category || '未分类' }}
        </router-link>
        <span>|</span>
        <time :datetime="post?.date">{{ post?.date }}</time>
        <span>|</span>
        <span>约 {{ readingTime }} 分钟</span>
        <span v-if="post?.views !== undefined">|</span>
        <span v-if="post?.views !== undefined">{{ post.views }} 次阅读</span>
        <span>|</span>
        <button
          @click="toggleFavorite"
          :disabled="favoriteToggling"
          class="inline-flex items-center gap-1 text-sm transition-colors"
          :class="favorited ? 'text-red-500' : 'text-gray-400 hover:text-red-400'"
        >
          <span>{{ favorited ? '♥' : '♡' }}</span>
          <span>{{ favorited ? '已收藏' : '收藏' }}</span>
        </button>
      </div>
      <div class="mt-3 flex flex-wrap gap-1.5">
        <TagBadge v-for="tag in post?.tags" :key="tag" :tag="tag" :clickable="true" />
      </div>
    </header>

    <div class="lg:flex lg:gap-8">
      <aside class="hidden lg:block lg:w-48 lg:flex-shrink-0">
        <div class="sticky top-20">
          <TOC :headings="headings" />
        </div>
      </aside>

      <div class="min-w-0 flex-1">
        <div class="prose max-w-none" v-html="post?.html"></div>
        <RelatedPosts :slug="post?.slug || ''" />
        <CommentSection :post-slug="post?.slug || ''" />
      </div>
    </div>
  </article>
</template>
