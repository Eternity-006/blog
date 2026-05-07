<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { renderMarkdown } from '@/utils/markdown'

const route = useRoute()
const router = useRouter()

// Form state
const slug = ref('')
const title = ref('')
const date = ref(new Date().toISOString().split('T')[0])
const category = ref('')
const tags = ref('')
const excerpt = ref('')
const body = ref('')
const saving = ref(false)
const message = ref('')

const isEdit = computed(() => !!route.params.slug)

// Live preview
const previewHtml = computed(() => {
  if (!body.value.trim()) return ''
  try {
    return renderMarkdown(body.value)
  } catch {
    return '<p style="color:red">Markdown 解析错误</p>'
  }
})

// Auto-generate slug from title
watch(title, (val) => {
  if (!isEdit.value && val) {
    slug.value = val
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-z0-9\-_一-鿿]/g, '')
  }
})

// Pull existing posts for quick edit
const existingPosts = ref<{ slug: string; title: string }[]>([])
onMounted(async () => {
  try {
    const res = await fetch('/api/list-posts')
    existingPosts.value = await res.json()
  } catch { /* dev-only */ }

  // Load existing post if editing
  if (isEdit.value) {
    try {
      const res = await fetch(`/api/get-post?slug=${route.params.slug}`)
      const { content } = await res.json()

      // Parse frontmatter
      const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)/)
      if (fmMatch) {
        const fm = fmMatch[1]
        body.value = fmMatch[2]

        const getField = (name: string) => {
          const m = fm.match(new RegExp(`${name}:\\s*"(.+?)"`))
          return m ? m[1] : ''
        }
        const getArray = (name: string) => {
          const m = fm.match(new RegExp(`${name}:\\s*\\[([^\\]]+)\\]`))
          return m ? m[1].split(',').map((s: string) => s.trim().replace(/"/g, '').replace(/'/g, '')).join(', ') : ''
        }

        title.value = getField('title')
        date.value = getField('date') || date.value
        category.value = getField('category')
        tags.value = getArray('tags')
        excerpt.value = getField('excerpt')
        slug.value = route.params.slug as string
      }
    } catch { /* will fail if post doesn't exist */ }
  }
})

// Build full markdown content
function buildContent(): string {
  const tagsArr = tags.value
    .split(/[,，]/)
    .map(t => t.trim())
    .filter(Boolean)
    .map(t => `"${t}"`)

  return [
    '---',
    `title: "${title.value}"`,
    `date: "${date.value}"`,
    `category: "${category.value}"`,
    `tags: [${tagsArr.join(', ')}]`,
    `excerpt: "${excerpt.value}"`,
    '---',
    '',
    body.value,
  ].join('\n')
}

async function handleSave() {
  if (!slug.value || !title.value || !body.value) {
    message.value = '请填写标题、Slug 和正文内容'
    return
  }

  saving.value = true
  message.value = ''

  try {
    const res = await fetch('/api/save-post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slug: slug.value, content: buildContent() }),
    })
    const data = await res.json()
    if (data.ok) {
      message.value = '文章保存成功！'
      if (!isEdit.value) {
        // Redirect to edit mode
        router.replace(`/admin/${data.slug}`)
      }
    } else {
      message.value = `保存失败：${data.error}`
    }
  } catch (e) {
    message.value = `请求失败：${String(e)}`
  } finally {
    saving.value = false
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
  message.value = ''
  router.replace('/admin')
}
</script>

<template>
  <div class="max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">{{ isEdit ? '编辑文章' : '写新文章' }}</h1>
      <div class="flex gap-3">
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

    <p v-if="message" :class="message.includes('成功') ? 'text-green-600' : 'text-red-500'" class="mb-4 text-sm">
      {{ message }}
    </p>

    <!-- Existing posts quick select -->
    <div v-if="existingPosts.length > 0" class="mb-6">
      <label class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2 block">编辑已有文章</label>
      <select
        class="w-full sm:w-80 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
        @change="(e) => { const sel = (e.target as HTMLSelectElement).value; if (sel) router.push(`/admin/${sel}`) }"
      >
        <option value="">-- 选择文章 --</option>
        <option v-for="p in existingPosts" :key="p.slug" :value="p.slug">{{ p.title }}</option>
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
        <div
          class="h-[500px] overflow-y-auto rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 p-4"
        >
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
        {{ saving ? '保存中...' : '保存文章' }}
      </button>
      <button @click="newPost" class="px-6 py-2 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
        清空重写
      </button>
      <router-link v-if="slug" :to="`/post/${slug}`" target="_blank" class="px-6 py-2 text-center border border-green-300 text-green-600 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors">
        查看文章 →
      </router-link>
    </div>
  </div>
</template>
