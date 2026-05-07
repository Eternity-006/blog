<script setup lang="ts">
import { ref } from 'vue'
import SearchBox from './SearchBox.vue'
import ThemeToggle from './ThemeToggle.vue'

const mobileMenuOpen = ref(false)
</script>

<template>
  <header class="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-700">
    <nav class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14">
        <router-link to="/" class="text-xl font-bold text-primary hover:text-primary-dark transition-colors">
          我的博客
        </router-link>

        <!-- Desktop nav -->
        <div class="hidden sm:flex items-center gap-6">
          <SearchBox />
          <router-link to="/" class="text-sm hover:text-primary transition-colors">首页</router-link>
          <router-link to="/about" class="text-sm hover:text-primary transition-colors">关于</router-link>
          <router-link to="/admin" class="text-sm hover:text-primary transition-colors">写文章</router-link>
          <a href="/rss.xml" class="text-sm hover:text-primary transition-colors" target="_blank">RSS</a>
          <ThemeToggle />
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
          <router-link to="/" @click="mobileMenuOpen = false" class="text-sm hover:text-primary transition-colors">首页</router-link>
          <router-link to="/about" @click="mobileMenuOpen = false" class="text-sm hover:text-primary transition-colors">关于</router-link>
          <router-link to="/admin" @click="mobileMenuOpen = false" class="text-sm hover:text-primary transition-colors">写文章</router-link>
          <a href="/rss.xml" class="text-sm hover:text-primary transition-colors" target="_blank">RSS</a>
        </div>
      </div>
    </nav>
  </header>
</template>
