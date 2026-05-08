<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SearchBox from './SearchBox.vue'
import ThemeToggle from './ThemeToggle.vue'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isLoggedIn, isAdmin, user, logout } = useAuth()
const mobileMenuOpen = ref(false)

function handleLogout() {
  logout()
  mobileMenuOpen.value = false
  router.replace('/')
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-700">
    <nav class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14">
        <router-link to="/" class="text-xl font-bold text-primary hover:text-primary-dark transition-colors">
          博客平台
        </router-link>

        <!-- Desktop nav -->
        <div class="hidden sm:flex items-center gap-5">
          <SearchBox />
          <router-link to="/" class="text-sm hover:text-primary transition-colors">首页</router-link>
          <router-link to="/about" class="text-sm hover:text-primary transition-colors">关于</router-link>
          <router-link to="/users" class="text-sm hover:text-primary transition-colors">用户</router-link>
          <ThemeToggle />

          <template v-if="isLoggedIn">
            <router-link to="/admin" class="text-sm hover:text-primary transition-colors">写文章</router-link>
            <router-link v-if="isAdmin" to="/dashboard" class="text-sm hover:text-primary transition-colors" title="管理后台">⚙</router-link>
            <router-link :to="`/user/${user?.username}`" class="text-sm text-gray-500 hover:text-primary transition-colors">
              {{ user?.username }}
            </router-link>
            <button @click="handleLogout" class="text-sm text-gray-400 hover:text-red-500 transition-colors">退出</button>
          </template>
          <template v-else>
            <router-link to="/login" class="text-sm text-gray-400 hover:text-primary transition-colors">登录</router-link>
            <router-link to="/register" class="text-sm bg-primary text-white px-3 py-1 rounded-lg hover:bg-primary-dark transition-colors">注册</router-link>
          </template>
        </div>

        <!-- Mobile menu button -->
        <div class="flex sm:hidden items-center gap-2">
          <ThemeToggle />
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700"
            aria-label="展开菜单"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="sm:hidden pb-4 space-y-4">
        <SearchBox />
        <div class="flex flex-col gap-3">
          <router-link to="/" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">首页</router-link>
          <router-link to="/about" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">关于</router-link>
          <router-link to="/users" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">用户</router-link>
          <template v-if="isLoggedIn">
            <router-link to="/admin" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">写文章</router-link>
            <router-link v-if="isAdmin" to="/dashboard" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">管理后台</router-link>
            <router-link :to="`/user/${user?.username}`" @click="mobileMenuOpen = false" class="text-sm text-gray-500 hover:text-primary">
              {{ user?.username }}
            </router-link>
            <button @click="handleLogout" class="text-sm text-left text-red-400 hover:text-red-500">退出登录</button>
          </template>
          <template v-else>
            <router-link to="/login" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">登录</router-link>
            <router-link to="/register" @click="mobileMenuOpen = false" class="text-sm hover:text-primary">注册</router-link>
          </template>
        </div>
      </div>
    </nav>
  </header>
</template>
