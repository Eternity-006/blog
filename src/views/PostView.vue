<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { extractHeadings } from '@/utils/markdown'
import type { Post } from '@/types/post'
import TagBadge from '@/components/TagBadge.vue'
import TOC from '@/components/TOC.vue'
import CommentSection from '@/components/CommentSection.vue'

const route = useRoute()
const post = ref<Post | null>(null)
const headings = ref<{ id: string; text: string; level: number }[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    const res = await fetch(import.meta.env.BASE_URL + 'posts-index.json')
    const posts: Post[] = await res.json()
    const found = posts.find(p => p.slug === slug)

    if (!found) {
      error.value = '文章未找到。'
      return
    }

    post.value = found

    await nextTick()
    headings.value = extractHeadings(found.html)

    // Add IDs to headings in the DOM for anchor links
    document.querySelectorAll<HTMLElement>('.prose h1, .prose h2, .prose h3').forEach((el) => {
      const text = el.textContent || ''
      const id = text
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^a-z0-9一-鿿\-]/g, '')
      el.id = id
    })

    document.title = `${found.title} | 我的博客`
  } catch {
    error.value = '文章加载失败。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="loading" class="text-center py-20 text-gray-500">加载文章中...</div>

  <div v-else-if="error" class="text-center py-20">
    <p class="text-red-500 text-lg mb-4">{{ error }}</p>
    <router-link to="/" class="text-primary hover:underline">← 返回首页</router-link>
  </div>

  <article v-else class="max-w-3xl mx-auto">
    <header class="mb-8">
      <router-link to="/" class="text-sm text-gray-500 hover:text-primary transition-colors mb-4 inline-block">
        ← 返回首页
      </router-link>
      <h1 class="text-3xl sm:text-4xl font-bold mb-4">{{ post?.title }}</h1>
      <div class="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
        <router-link :to="`/category/${post?.category}`" class="text-primary hover:underline font-medium">
          {{ post?.category }}
        </router-link>
        <span>|</span>
        <time :datetime="post?.date">{{ post?.date }}</time>
        <span>|</span>
        <span class="flex flex-wrap gap-1.5">
          <TagBadge v-for="tag in post?.tags" :key="tag" :tag="tag" :clickable="true" />
        </span>
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

        <CommentSection
          repo="yourusername/yourrepo"
          repo-id="R_kgDOGXXXXX"
          category="Announcements"
          category-id="DIC_kwDOGXXXXX"
        />
      </div>
    </div>
  </article>
</template>
