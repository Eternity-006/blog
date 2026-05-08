import { ref, computed } from 'vue'
import { api } from '@/api'

interface User {
  id: number
  username: string
  is_admin: boolean
}

const token = ref(localStorage.getItem('auth_token') || '')
const user = ref<User | null>(
  JSON.parse(localStorage.getItem('auth_user') || 'null')
)

export function useAuth() {
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin === true)

  async function login(username: string, password: string): Promise<string | null> {
    try {
      const res = await api('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        return data.error || '登录失败'
      }
      token.value = data.token
      user.value = data.user
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('auth_user', JSON.stringify(data.user))
      return null
    } catch {
      return '网络错误，请检查后端是否启动'
    }
  }

  async function register(username: string, password: string): Promise<string | null> {
    try {
      const res = await api('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      const data = await res.json()
      if (!res.ok) {
        return data.error || '注册失败'
      }
      token.value = data.token
      user.value = data.user
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('auth_user', JSON.stringify(data.user))
      return null
    } catch {
      return '网络错误，请检查后端是否启动'
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  async function checkAuth(): Promise<boolean> {
    if (!token.value) return false
    try {
      const res = await api('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token.value}` },
      })
      if (!res.ok) {
        logout()
        return false
      }
      const data = await res.json()
      user.value = data.user
      return true
    } catch {
      return !!token.value
    }
  }

  function authHeaders(): Record<string, string> {
    return token.value ? { 'Authorization': `Bearer ${token.value}` } : {}
  }

  return { token, user, isLoggedIn, isAdmin, login, register, logout, checkAuth, authHeaders }
}
