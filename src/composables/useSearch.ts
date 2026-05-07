import { ref, computed } from 'vue'
import Fuse from 'fuse.js'
import type { PostMeta } from '@/types/post'

const searchQuery = ref('')
const posts = ref<PostMeta[]>([])

export function useSearch() {
  const fuse = computed(() => {
    return new Fuse(posts.value, {
      keys: ['title', 'excerpt', 'tags', 'category'],
      threshold: 0.3,
      includeScore: true,
    })
  })

  const results = computed(() => {
    if (!searchQuery.value.trim()) return []
    return fuse.value.search(searchQuery.value).map(r => r.item)
  })

  function setPosts(p: PostMeta[]) {
    posts.value = p
  }

  return { searchQuery, results, setPosts }
}
