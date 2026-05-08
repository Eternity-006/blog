<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
import Toast from '@/components/Toast.vue'
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1 w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="border-t border-gray-200 dark:border-gray-700 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
      <p>&copy; {{ new Date().getFullYear() }} 博客平台 — 基于 Vue + Flask 构建</p>
    </footer>
    <Toast />
  </div>
</template>
