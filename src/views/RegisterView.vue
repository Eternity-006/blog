<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  if (password.value.length < 3) {
    error.value = '密码至少 3 个字符'
    return
  }
  loading.value = true
  error.value = ''
  const err = await register(username.value, password.value)
  if (err) {
    error.value = err
  } else {
    router.replace('/admin')
  }
  loading.value = false
}
</script>

<template>
  <div class="max-w-sm mx-auto mt-12">
    <h1 class="text-2xl font-bold mb-6 text-center">注册</h1>

    <div v-if="error" class="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
      {{ error }}
    </div>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">用户名</label>
        <input
          v-model="username"
          type="text"
          maxlength="30"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="2-30个字符，字母数字下划线"
          autocomplete="username"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">密码</label>
        <input
          v-model="password"
          type="password"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="至少 3 个字符"
          autocomplete="new-password"
        />
      </div>
      <button
        type="submit"
        :disabled="loading"
        class="w-full py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
      >
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>

    <p class="mt-6 text-center text-sm text-gray-500 space-x-4">
      <router-link to="/login" class="text-primary hover:underline">已有账号？登录</router-link>
      <router-link to="/" class="hover:underline">← 返回首页</router-link>
    </p>
  </div>
</template>
