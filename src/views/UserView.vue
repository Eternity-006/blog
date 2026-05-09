<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { PostMeta } from '@/types/post'
import PostList from '@/components/PostList.vue'
import { api } from '@/api'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const username = route.params.username as string
const posts = ref<PostMeta[]>([])
const userInfo = ref<{ username: string; bio: string; created_at: string } | null>(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref<'posts' | 'favorites'>('posts')
const favorites = ref<PostMeta[]>([])
const favLoading = ref(false)
const { isLoggedIn } = useAuth()

onMounted(async () => {
  try {
    const res = await api(`/api/users/${encodeURIComponent(username)}`)
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

async function loadFavorites() {
  if (!isLoggedIn.value || favLoading.value) return
  favLoading.value = true
  try {
    const res = await api('/api/my/favorites', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` },
    })
    if (res.ok) {
      favorites.value = await res.json()
    }
  } catch { /* ignore */ }
  favLoading.value = false
}

function switchTab(tab: 'posts' | 'favorites') {
  activeTab.value = tab
  if (tab === 'favorites') loadFavorites()
}
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

    <!-- Tabs -->
    <div class="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
      <button
        @click="switchTab('posts')"
        :class="activeTab === 'posts' ? 'border-b-2 border-primary text-primary' : 'text-gray-500'"
        class="pb-2 px-1 text-sm font-medium"
      >
        文章 ({{ posts.length }})
      </button>
      <button
        @click="switchTab('favorites')"
        :class="activeTab === 'favorites' ? 'border-b-2 border-primary text-primary' : 'text-gray-500'"
        class="pb-2 px-1 text-sm font-medium"
      >
        收藏的文章
      </button>
    </div>

    <PostList v-if="activeTab === 'posts'" :posts="posts" />

    <div v-if="activeTab === 'favorites'">
      <div v-if="favLoading" class="text-center py-8 text-gray-500">加载中...</div>
      <div v-else-if="favorites.length === 0" class="text-center py-8 text-gray-400">暂无收藏的文章</div>
      <PostList v-else :posts="favorites" />
    </div>
  </div>
</template>
