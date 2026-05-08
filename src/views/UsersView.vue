<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface UserInfo {
  id: number; username: string; bio: string; is_admin: boolean; created_at: string
}

const users = ref<UserInfo[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch('/api/users')
    if (res.ok) users.value = await res.json()
  } catch { /* ignore */ }
  loading.value = false
})
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold mb-2">用户</h1>
    <p class="text-gray-500 dark:text-gray-400 mb-8">浏览平台上的所有用户</p>

    <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <router-link
        v-for="u in users"
        :key="u.id"
        :to="`/user/${u.username}`"
        class="p-6 rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:border-primary/30 transition-all bg-white dark:bg-gray-800"
      >
        <div class="flex items-center gap-3 mb-3">
          <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-lg font-bold text-primary">
            {{ u.username.charAt(0).toUpperCase() }}
          </div>
          <div>
            <div class="font-medium flex items-center gap-2">
              {{ u.username }}
              <span v-if="u.is_admin" class="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-600 px-1.5 py-0.5 rounded">管理</span>
            </div>
            <div class="text-xs text-gray-500">{{ new Date(u.created_at).toLocaleDateString('zh-CN') }} 加入</div>
          </div>
        </div>
        <p v-if="u.bio" class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{{ u.bio }}</p>
        <p v-else class="text-sm text-gray-400 italic">暂无简介</p>
      </router-link>
    </div>

    <p v-if="!loading && users.length === 0" class="text-center py-12 text-gray-400">
      暂无用户。
    </p>
  </div>
</template>
