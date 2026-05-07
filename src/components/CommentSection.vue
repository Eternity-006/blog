<script setup lang="ts">
import { onMounted, ref } from 'vue'

const props = defineProps<{
  repo: string
  repoId: string
  category: string
  categoryId: string
}>()

const container = ref<HTMLElement>()

onMounted(() => {
  if (!container.value) return
  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.setAttribute('data-repo', props.repo)
  script.setAttribute('data-repo-id', props.repoId)
  script.setAttribute('data-category', props.category)
  script.setAttribute('data-category-id', props.categoryId)
  script.setAttribute('data-mapping', 'pathname')
  script.setAttribute('data-strict', '0')
  script.setAttribute('data-reactions-enabled', '1')
  script.setAttribute('data-emit-metadata', '0')
  script.setAttribute('data-input-position', 'bottom')
  script.setAttribute('data-theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light')
  script.setAttribute('data-lang', 'en')
  script.setAttribute('crossorigin', 'anonymous')
  script.async = true
  container.value.appendChild(script)
})
</script>

<template>
  <div ref="container" class="mt-12"></div>
</template>
