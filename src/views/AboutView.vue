<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  document.title = '关于 | 我的博客'
})
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-8">关于</h1>

    <div class="prose dark:prose-invert max-w-none">
      <p>
        你好！欢迎来到我的个人博客。我是一名前端开发者，热爱 Vue.js、TypeScript
        以及构建优雅的 Web 体验。
      </p>

      <h2>关于本站</h2>
      <p>
        本站使用 Vue 3、Vite 和 Tailwind CSS 构建。文章使用 Markdown 编写，
        构建时预渲染为静态页面，加载速度快，部署简单。
      </p>

      <h2>联系方式</h2>
      <ul>
        <li>GitHub：<a href="https://github.com/yourusername" target="_blank">@yourusername</a></li>
        <li>邮箱：your.email@example.com</li>
      </ul>

      <h2>技术栈</h2>
      <ul>
        <li>Vue 3（Composition API）</li>
        <li>TypeScript</li>
        <li>Vite</li>
        <li>Vue Router</li>
        <li>Tailwind CSS</li>
        <li>markdown-it 渲染 Markdown</li>
        <li>Fuse.js 全文搜索</li>
        <li>Giscus 评论系统</li>
      </ul>
    </div>
  </div>
</template>
