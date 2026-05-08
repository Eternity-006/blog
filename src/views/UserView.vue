<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'

const route = useRoute()
const username = route.params.username as string
const posts = ref<PostMeta[]>([])
const userInfo = ref<{ username: string; bio: string; created_at: string } | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await fetch(`/api/users/${encodeURIComponent(username)}`)
    if (res.ok) {
      const data = await res.json()
      userInfo.value = data.user
      posts.value = data.posts
    } else {
      error.value = '用户不存在'
    }
  } catch {
    error.value = '加载失败，请检查后端是否启动'
  }
  loading.value = false
})
</script>

<template>
  <div v-if="loading" class="text-center py-20 text-gray-500">加载中...</div>

  <div v-else-if="error" class="text-center py-20">
    <p class="text-red-500 text-lg mb-4">{{ error }}</p>
    <router-link to="/" class="text-primary hover:underline">&larr; 返回首页</router-link>
  </div>

  <div v-else>
    <router-link to="/" class="text-sm text-gray-500 hover:text-primary transition-colors mb-4 inline-block">
      &larr; 返回首页
    </router-link>

    <section class="mb-8">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-2xl font-bold text-primary">
          {{ username.charAt(0).toUpperCase() }}
        </div>
        <div>
          <h1 class="text-2xl font-bold">{{ username }}</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            加入于 {{ userInfo ? new Date(userInfo.created_at).toLocaleDateString('zh-CN') : '' }}
          </p>
        </div>
      </div>
      <p v-if="userInfo?.bio" class="text-gray-600 dark:text-gray-400">{{ userInfo.bio }}</p>
    </section>

    <h2 class="text-lg font-bold mb-4">文章 ({{ posts.length }})</h2>
    <PostList :posts="posts" />
  </div>
</template>
