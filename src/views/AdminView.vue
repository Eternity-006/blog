<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { renderMarkdown } from '@/utils/markdown'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { api } from '@/api'

const route = useRoute()
const router = useRouter()
const { user, logout, authHeaders } = useAuth()
const toast = useToast()

const slug = ref('')
const title = ref('')
const date = ref(new Date().toISOString().split('T')[0])
const category = ref('')
const tags = ref('')
const excerpt = ref('')
const body = ref('')
const publishStatus = ref<'published' | 'draft'>('published')
const saving = ref(false)
const deleting = ref(false)

const isEdit = computed(() => !!route.params.slug)

const previewHtml = computed(() => {
  if (!body.value.trim()) return ''
  try {
    return renderMarkdown(body.value)
  } catch {
    return '<p style="color:red">Markdown 解析错误</p>'
  }
})

watch(title, (val) => {
  if (!isEdit.value && val) {
    slug.value = val
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9\-_一-鿿]/g, '')
  }
})

const myPosts = ref<{ slug: string; title: string; status: string }[]>([])

onMounted(async () => {
  // Load my posts for quick edit
  try {
    const res = await api('/api/my/posts', { headers: authHeaders() })
    if (res.ok) {
      const posts = await res.json()
      myPosts.value = posts.map((p: { slug: string; title: string; status: string }) => ({
        slug: p.slug, title: p.title, status: p.status,
      }))
    }
  } catch { /* ignore */ }

  // Load existing post data if editing
  if (isEdit.value) {
    try {
      const res = await api(`/api/posts/${route.params.slug}`)
      if (res.ok) {
        const data = await res.json()
        title.value = data.title
        date.value = data.date
        category.value = data.category
        tags.value = Array.isArray(data.tags) ? data.tags.join(', ') : data.tags
        excerpt.value = data.excerpt
        body.value = data.content
        slug.value = data.slug
        publishStatus.value = data.status || 'published'
      }
    } catch { /* ignore */ }
  }
})

function buildPayload() {
  return {
    slug: slug.value,
    title: title.value,
    date: date.value,
    category: category.value,
    tags: tags.value.split(/[,，]/).map(t => t.trim()).filter(Boolean),
    excerpt: excerpt.value,
    content: body.value,
    status: publishStatus.value,
  }
}

async function handleSave() {
  if (!slug.value || !title.value || !body.value) {
    toast.error('请填写标题、Slug 和正文内容')
    return
  }

  saving.value = true

  try {
    const isNew = !isEdit.value
    const url = isNew ? '/api/posts' : `/api/posts/${slug.value}`
    const method = isNew ? 'POST' : 'PUT'

    const res = await api(url, {
      method,
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify(buildPayload()),
    })
    const data = await res.json()

    if (res.ok) {
      const statusText = publishStatus.value === 'draft' ? '（草稿）' : ''
      toast.success(`文章保存成功！${statusText}`)
      if (isNew) {
        router.replace(`/admin/${data.slug}`)
      }
    } else {
      toast.error(`保存失败：${data.error}`)
    }
  } catch {
    toast.error('网络错误，请确保后端已启动')
  } finally {
    saving.value = false
  }
}

async function handleDelete() {
  if (!isEdit.value) return
  if (!confirm(`确定要删除文章「${title.value}」吗？`)) return

  deleting.value = true
  try {
    const res = await api(`/api/posts/${slug.value}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    const data = await res.json()
    if (data.ok) {
      toast.success('文章已删除')
      router.replace('/admin')
      newPost()
    } else {
      toast.error(`删除失败：${data.error}`)
    }
  } catch {
    toast.error('网络错误')
  } finally {
    deleting.value = false
  }
}

function newPost() {
  slug.value = ''
  title.value = ''
  date.value = new Date().toISOString().split('T')[0]
  category.value = ''
  tags.value = ''
  excerpt.value = ''
  body.value = ''
  publishStatus.value = 'published'
  router.replace('/admin')
}

function handleLogout() {
  logout()
  router.replace('/')
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold">{{ isEdit ? '编辑文章' : '写新文章' }}</h1>
        <p class="text-xs text-gray-500 mt-1">作者：{{ user?.username }}</p>
      </div>
      <div class="flex gap-3">
        <button @click="handleLogout" class="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          退出登录
        </button>
        <button @click="newPost" class="px-3 py-1.5 text-sm border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
          新建文章
        </button>
        <button
          @click="handleSave"
          :disabled="saving"
          class="px-4 py-1.5 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <!-- My posts quick select -->
    <div v-if="myPosts.length > 0" class="mb-6">
      <label class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2 block">我的文章</label>
      <select
        class="w-full sm:w-80 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
        @change="(e) => { const sel = (e.target as HTMLSelectElement).value; if (sel) router.push(`/admin/${sel}`) }"
      >
        <option value="">-- 选择文章 --</option>
        <option v-for="p in myPosts" :key="p.slug" :value="p.slug">
          {{ p.status === 'draft' ? '[草稿]' : '' }} {{ p.title }}
        </option>
      </select>
    </div>

    <!-- Frontmatter form -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Slug *</label>
        <input
          v-model="slug"
          :disabled="isEdit"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          placeholder="my-article-slug"
        />
      </div>
      <div class="sm:col-span-2">
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">标题 *</label>
        <input
          v-model="title"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="文章标题"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">日期</label>
        <input
          v-model="date"
          type="date"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">分类</label>
        <input
          v-model="category"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="前端"
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">标签（逗号分隔）</label>
        <input
          v-model="tags"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="vue, typescript"
        />
      </div>
      <div class="sm:col-span-2">
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">摘要</label>
        <input
          v-model="excerpt"
          class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
          placeholder="文章简短描述..."
        />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">状态</label>
        <select v-model="publishStatus" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm">
          <option value="published">发布</option>
          <option value="draft">草稿</option>
        </select>
      </div>
    </div>

    <!-- Editor + Preview -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">正文（Markdown）*</label>
        <textarea
          v-model="body"
          class="w-full h-[500px] px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-mono resize-none"
          placeholder="## 开始写文章..."
        ></textarea>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">实时预览</label>
        <div class="h-[500px] overflow-y-auto rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 p-4">
          <div v-if="body.trim()" class="prose max-w-none text-sm" v-html="previewHtml"></div>
          <p v-else class="text-gray-400 text-sm">在左侧输入 Markdown，这里将实时显示预览...</p>
        </div>
      </div>
    </div>

    <div class="mt-6 flex gap-3">
      <button
        @click="handleSave"
        :disabled="saving"
        class="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
      >
        {{ saving ? '保存中...' : (publishStatus === 'draft' ? '保存草稿' : '发布文章') }}
      </button>
      <button @click="newPost" class="px-6 py-2 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
        清空重写
      </button>
      <button
        v-if="isEdit"
        @click="handleDelete"
        :disabled="deleting"
        class="px-6 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50"
      >
        {{ deleting ? '删除中...' : '删除文章' }}
      </button>
      <router-link v-if="slug && publishStatus === 'published'" :to="`/post/${slug}`" target="_blank" class="px-6 py-2 text-center border border-green-300 text-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors">
        查看文章 &rarr;
      </router-link>
    </div>
  </div>
</template>
