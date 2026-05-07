<script setup lang="ts">
import type { PostMeta } from '@/types/post'
import TagBadge from './TagBadge.vue'

defineProps<{ post: PostMeta }>()
</script>

<template>
  <article class="p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-primary/30 dark:hover:border-primary/30 transition-all bg-white dark:bg-gray-800">
    <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mb-3">
      <router-link
        :to="`/category/${post.category}`"
        class="font-medium text-primary hover:underline"
      >
        {{ post.category }}
      </router-link>
      <span>|</span>
      <time :datetime="post.date">{{ post.date }}</time>
    </div>

    <h2 class="text-xl font-bold mb-2">
      <router-link :to="`/post/${post.slug}`" class="hover:text-primary transition-colors">
        {{ post.title }}
      </router-link>
    </h2>

    <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3 leading-relaxed">
      {{ post.excerpt }}
    </p>

    <div class="flex flex-wrap items-center gap-2">
      <TagBadge v-for="tag in post.tags" :key="tag" :tag="tag" :clickable="true" />
    </div>

    <router-link
      :to="`/post/${post.slug}`"
      class="inline-block mt-4 text-sm font-medium text-primary hover:underline"
    >
      阅读全文 →
    </router-link>
  </article>
</template>
