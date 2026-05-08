<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { api } from '@/api'

const { isAdmin, authHeaders } = useAuth()

interface Stats {
  users: number; posts: number; published: number; drafts: number
  comments: number; views: number
}
interface AdminUser {
  id: number; username: string; is_admin: boolean; status: string
  created_at: string; post_count: number
}
interface AdminPost {
  slug: string; title: string; author: string; status: string; date: string
  category: string
}

const stats = ref<Stats>({ users: 0, posts: 0, published: 0, drafts: 0, comments: 0, views: 0 })
const users = ref<AdminUser[]>([])
const allPosts = ref<AdminPost[]>([])
const loading = ref(true)
const activeTab = ref<'users' | 'posts'>('users')
const message = ref('')

async function fetchData() {
  try {
    const h = authHeaders()
    const [statsRes, usersRes, postsRes] = await Promise.all([
      api('/api/admin/stats', { headers: h }),
      api('/api/admin/users', { headers: h }),
      api('/api/admin/posts', { headers: h }),
    ])
    if (statsRes.ok) stats.value = await statsRes.json()
    if (usersRes.ok) users.value = await usersRes.json()
    if (postsRes.ok) allPosts.value = await postsRes.json()
  } catch { /* ignore */ }
  loading.value = false
}

onMounted(fetchData)

async function toggleBan(user: AdminUser) {
  const newStatus = user.status === 'active' ? 'banned' : 'active'
  try {
    const res = await api(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus }),
    })
    if (res.ok) {
      user.status = newStatus
      message.value = `用户「${user.username}」已${newStatus === 'banned' ? '封禁' : '解封'}`
    }
  } catch { /* ignore */ }
}

async function toggleAdmin(user: AdminUser) {
  if (user.is_admin && !confirm('确定要取消该用户的管理员权限吗？')) return
  try {
    const res = await api(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_admin: !user.is_admin }),
    })
    if (res.ok) {
      user.is_admin = !user.is_admin
      message.value = `用户「${user.username}」${user.is_admin ? '已设为管理员' : '已取消管理员'}`
    }
  } catch { /* ignore */ }
}

async function deleteUser(user: AdminUser) {
  if (!confirm(`确定删除用户「${user.username}」及其所有文章吗？此操作不可撤销！`)) return
  try {
    const res = await api(`/api/admin/users/${user.id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (res.ok) {
      users.value = users.value.filter(u => u.id !== user.id)
      message.value = `用户「${user.username}」已删除`
      await fetchData()
    }
  } catch { /* ignore */ }
}

async function resetPassword(user: AdminUser) {
  const pw = prompt('输入新密码（至少3个字符）：')
  if (!pw || pw.length < 3) return
  try {
    await api(`/api/admin/users/${user.id}`, {
      method: 'PUT',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: pw }),
    })
    message.value = `已重置「${user.username}」的密码`
  } catch { /* ignore */ }
}

async function deletePost(post: AdminPost) {
  if (!confirm(`确定删除文章「${post.title}」吗？`)) return
  try {
    const res = await api(`/api/posts/${post.slug}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (res.ok) {
      allPosts.value = allPosts.value.filter(p => p.slug !== post.slug)
      message.value = '文章已删除'
      await fetchData()
    }
  } catch { /* ignore */ }
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-2xl font-bold mb-2">管理后台</h1>
    <p class="text-sm text-gray-500 mb-6">仅管理员可访问</p>

    <p v-if="message" class="mb-4 text-sm text-green-600">{{ message }}</p>
    <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>

    <template v-else>
      <!-- Stats cards -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
        <div class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ stats.users }}</div>
          <div class="text-xs text-gray-500 mt-1">用户</div>
        </div>
        <div class="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 text-center">
          <div class="text-2xl font-bold text-green-600">{{ stats.posts }}</div>
          <div class="text-xs text-gray-500 mt-1">文章</div>
        </div>
        <div class="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-center">
          <div class="text-2xl font-bold text-emerald-600">{{ stats.published }}</div>
          <div class="text-xs text-gray-500 mt-1">已发布</div>
        </div>
        <div class="p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 text-center">
          <div class="text-2xl font-bold text-yellow-600">{{ stats.drafts }}</div>
          <div class="text-xs text-gray-500 mt-1">草稿</div>
        </div>
        <div class="p-4 rounded-xl bg-purple-50 dark:bg-purple-900/20 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ stats.comments }}</div>
          <div class="text-xs text-gray-500 mt-1">评论</div>
        </div>
        <div class="p-4 rounded-xl bg-orange-50 dark:bg-orange-900/20 text-center">
          <div class="text-2xl font-bold text-orange-600">{{ stats.views }}</div>
          <div class="text-xs text-gray-500 mt-1">阅读量</div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        <button
          @click="activeTab = 'users'"
          :class="activeTab === 'users' ? 'border-b-2 border-primary text-primary' : 'text-gray-500'"
          class="pb-2 px-1 text-sm font-medium"
        >
          用户管理 ({{ users.length }})
        </button>
        <button
          @click="activeTab = 'posts'"
          :class="activeTab === 'posts' ? 'border-b-2 border-primary text-primary' : 'text-gray-500'"
          class="pb-2 px-1 text-sm font-medium"
        >
          文章管理 ({{ allPosts.length }})
        </button>
      </div>

      <!-- Users table -->
      <div v-if="activeTab === 'users'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
              <th class="py-2 pr-4 font-medium">用户名</th>
              <th class="py-2 pr-4 font-medium">角色</th>
              <th class="py-2 pr-4 font-medium">文章数</th>
              <th class="py-2 pr-4 font-medium">状态</th>
              <th class="py-2 pr-4 font-medium">注册时间</th>
              <th class="py-2 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" class="border-b border-gray-100 dark:border-gray-800">
              <td class="py-3 pr-4">
                <router-link :to="`/user/${u.username}`" class="text-primary hover:underline font-medium">
                  {{ u.username }}
                </router-link>
              </td>
              <td class="py-3 pr-4">
                <span :class="u.is_admin ? 'text-purple-600' : 'text-gray-500'">{{ u.is_admin ? '管理员' : '用户' }}</span>
              </td>
              <td class="py-3 pr-4 text-gray-500">{{ u.post_count }}</td>
              <td class="py-3 pr-4">
                <span :class="u.status === 'active' ? 'text-green-600' : 'text-red-500'">
                  {{ u.status === 'active' ? '正常' : '已封禁' }}
                </span>
              </td>
              <td class="py-3 pr-4 text-gray-500 text-xs">{{ new Date(u.created_at).toLocaleDateString('zh-CN') }}</td>
              <td class="py-3">
                <div class="flex gap-2">
                  <button @click="toggleAdmin(u)" class="text-xs text-purple-500 hover:underline">
                    {{ u.is_admin ? '取消管理' : '设为管理' }}
                  </button>
                  <button @click="toggleBan(u)" class="text-xs hover:underline" :class="u.status === 'active' ? 'text-red-500' : 'text-green-500'">
                    {{ u.status === 'active' ? '封禁' : '解封' }}
                  </button>
                  <button @click="resetPassword(u)" class="text-xs text-blue-500 hover:underline">重置密码</button>
                  <button v-if="!u.is_admin" @click="deleteUser(u)" class="text-xs text-red-400 hover:underline">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Posts table -->
      <div v-if="activeTab === 'posts'" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700 text-left">
              <th class="py-2 pr-4 font-medium">标题</th>
              <th class="py-2 pr-4 font-medium">作者</th>
              <th class="py-2 pr-4 font-medium">分类</th>
              <th class="py-2 pr-4 font-medium">状态</th>
              <th class="py-2 pr-4 font-medium">日期</th>
              <th class="py-2 font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in allPosts" :key="p.slug" class="border-b border-gray-100 dark:border-gray-800">
              <td class="py-3 pr-4">
                <router-link :to="`/post/${p.slug}`" class="text-primary hover:underline font-medium">
                  {{ p.title }}
                </router-link>
              </td>
              <td class="py-3 pr-4">
                <router-link :to="`/user/${p.author}`" class="text-gray-500 hover:text-primary">{{ p.author }}</router-link>
              </td>
              <td class="py-3 pr-4 text-gray-500">{{ p.category }}</td>
              <td class="py-3 pr-4">
                <span :class="p.status === 'published' ? 'text-green-600' : 'text-yellow-600'">
                  {{ p.status === 'published' ? '已发布' : '草稿' }}
                </span>
              </td>
              <td class="py-3 pr-4 text-gray-500 text-xs">{{ p.date }}</td>
              <td class="py-3">
                <button @click="deletePost(p)" class="text-xs text-red-400 hover:underline">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>
