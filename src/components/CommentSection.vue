<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useToast } from '@/composables/useToast'
import { api } from '@/api'

const props = defineProps<{ postSlug: string }>()

interface Comment {
  id: number
  post_slug: string
  author: string
  content: string
  created_at: string
  parent_id: number | null
}

const { isLoggedIn, authHeaders } = useAuth()
const toast = useToast()

const comments = ref<Comment[]>([])
const loading = ref(true)
const author = ref('')
const content = ref('')
const submitting = ref(false)
const replyTo = ref<number | null>(null)
const replyAuthor = ref('')
const replyContent = ref('')

const topLevelComments = computed(() => comments.value.filter(c => !c.parent_id))
const repliesFor = (parentId: number) => comments.value.filter(c => c.parent_id === parentId)

async function fetchComments() {
  try {
    const res = await api(`/api/comments/${props.postSlug}`)
    if (res.ok) comments.value = await res.json()
  } catch { /* backend unavailable */ }
  loading.value = false
}

onMounted(fetchComments)

async function submitComment() {
  if (!content.value.trim()) {
    toast.error('请输入评论内容')
    return
  }
  submitting.value = true
  try {
    const res = await api(`/api/comments/${props.postSlug}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author: author.value.trim(), content: content.value.trim() }),
    })
    if (res.ok) {
      const newComment = await res.json()
      comments.value.push(newComment)
      content.value = ''
      author.value = ''
    } else {
      const data = await res.json()
      toast.error(data.error || '评论失败')
    }
  } catch {
    toast.error('网络错误，请稍后再试')
  }
  submitting.value = false
}

async function submitReply(parentId: number) {
  if (!replyContent.value.trim()) {
    toast.error('请输入回复内容')
    return
  }
  try {
    const res = await api(`/api/comments/${props.postSlug}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: replyAuthor.value.trim(),
        content: replyContent.value.trim(),
        parent_id: parentId,
      }),
    })
    if (res.ok) {
      const newComment = await res.json()
      comments.value.push(newComment)
      replyContent.value = ''
      replyAuthor.value = ''
      replyTo.value = null
    } else {
      const data = await res.json()
      toast.error(data.error || '回复失败')
    }
  } catch {
    toast.error('网络错误，请稍后再试')
  }
}

async function deleteComment(id: number) {
  try {
    const res = await api(`/api/comments/${id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    })
    if (res.ok) {
      comments.value = comments.value.filter(c => c.id !== id && c.parent_id !== id)
    }
  } catch { /* ignore */ }
}

function formatDate(d: string): string {
  return new Date(d).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="mt-12 border-t border-gray-200 dark:border-gray-700 pt-8">
    <h3 class="text-lg font-bold mb-6">评论 ({{ comments.length }})</h3>

    <div v-if="loading" class="text-sm text-gray-500">加载评论中...</div>

    <div v-else class="space-y-4 mb-8">
      <template v-for="c in topLevelComments" :key="c.id">
        <div class="p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="font-medium text-sm">{{ c.author }}</span>
              <span class="text-xs text-gray-400">{{ formatDate(c.created_at) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="replyTo = replyTo === c.id ? null : c.id"
                class="text-xs text-gray-400 hover:text-primary transition-colors"
              >
                {{ replyTo === c.id ? '取消回复' : '回复' }}
              </button>
              <button
                v-if="isLoggedIn"
                @click="deleteComment(c.id)"
                class="text-xs text-red-500 hover:text-red-600 opacity-60 hover:opacity-100 transition-opacity"
              >
                删除
              </button>
            </div>
          </div>
          <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ c.content }}</p>

          <!-- Reply form -->
          <div v-if="replyTo === c.id" class="mt-3 ml-4 space-y-2">
            <input
              v-model="replyAuthor"
              type="text"
              placeholder="你的昵称（选填）"
              maxlength="30"
              class="w-full px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-xs"
            />
            <textarea
              v-model="replyContent"
              rows="2"
              placeholder="写下你的回复..."
              maxlength="2000"
              class="w-full px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-xs resize-none"
            ></textarea>
            <button
              @click="submitReply(c.id)"
              class="px-3 py-1 text-xs bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
            >
              提交回复
            </button>
          </div>
        </div>

        <!-- Replies -->
        <div v-for="reply in repliesFor(c.id)" :key="reply.id" class="ml-8 p-4 rounded-lg bg-gray-50/50 dark:bg-gray-800/30 border-l-2 border-primary/30">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="font-medium text-sm">{{ reply.author }}</span>
              <span class="text-xs text-gray-400">{{ formatDate(reply.created_at) }}</span>
            </div>
            <button
              v-if="isLoggedIn"
              @click="deleteComment(reply.id)"
              class="text-xs text-red-500 hover:text-red-600 opacity-60 hover:opacity-100 transition-opacity"
            >
              删除
            </button>
          </div>
          <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ reply.content }}</p>
        </div>
      </template>

      <p v-if="comments.length === 0" class="text-sm text-gray-400 dark:text-gray-500">
        暂无评论，来发表第一条评论吧。
      </p>
    </div>

    <!-- Comment form -->
    <div class="space-y-3">
      <input
        v-model="author"
        type="text"
        placeholder="你的昵称（选填，默认「匿名」）"
        maxlength="30"
        class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
      />
      <textarea
        v-model="content"
        rows="3"
        placeholder="写下你的评论..."
        maxlength="2000"
        class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm resize-none"
      ></textarea>
      <div class="flex items-center justify-between">
        <span class="text-xs text-gray-400">{{ content.length }}/2000</span>
        <button
          @click="submitComment"
          :disabled="submitting"
          class="px-4 py-1.5 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
        >
          {{ submitting ? '提交中...' : '发表评论' }}
        </button>
      </div>
    </div>
  </div>
</template>
