---
title: "从零实现 Markdown 博客系统"
date: "2026-04-28"
category: "教程"
tags: ["vite", "markdown", "blog"]
excerpt: "手把手还原本博客的完整实现过程：构建脚本设计、Markdown 渲染管线、代码高亮配置、全文搜索及部署全流程。"
---

## 整体架构

```
posts/*.md                    ← 你写文章的地方
    │
    ▼
scripts/generate-posts-json.ts  ← 构建时运行
    │  gray-matter 解析 frontmatter
    │  markdown-it 渲染 HTML
    │  highlight.js 处理代码块
    │
    ▼
public/posts-index.json        ← 单文件，含全部文章数据和 HTML
    │
    ▼
Vue App（运行时 fetch 这个 JSON）
    ├── 首页：文章列表 + 分页
    ├── 详情页：直接渲染预生成的 HTML
    ├── 分类/标签页：前端过滤
    └── 搜索页：Fuse.js 模糊搜索
```

不需要数据库，不需要后端 API。一次构建生成一个 JSON，CDN 一丢就上线。

## 构建脚本核心实现

以下是 `scripts/generate-posts-json.ts` 的完整逻辑：

```typescript
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const postsDir = path.resolve(__dirname, '../posts')
const outputFile = path.resolve(__dirname, '../public/posts-index.json')

// 初始化 markdown-it，挂载 highlight.js
const md = new MarkdownIt({
  html: true,          // 允许 HTML 标签
  linkify: true,       // 自动识别链接
  typographer: true,   // 智能引号、破折号
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, {
          language: lang,
        }).value
      } catch { /* fall through */ }
    }
    return '' // 让 markdown-it 走默认转义
  },
})

interface PostEntry {
  slug: string
  title: string
  date: string
  category: string
  tags: string[]
  excerpt: string
  html: string
}

const files = fs.readdirSync(postsDir).filter(f => f.endsWith('.md'))

const posts: PostEntry[] = files.map(file => {
  const raw = fs.readFileSync(path.join(postsDir, file), 'utf-8')
  const { data, content } = matter(raw)          // 分离 frontmatter 和正文
  const html = md.render(content)                 // 正文 → HTML

  return {
    slug: file.replace(/\.md$/, ''),
    title: data.title || slug,
    date: data.date || '1970-01-01',
    category: data.category || '未分类',
    tags: data.tags || [],
    excerpt: data.excerpt || '',
    html,                                         // 预渲染的 HTML
  }
})

// 按日期倒序排列
posts.sort((a, b) =>
  new Date(b.date).getTime() - new Date(a.date).getTime()
)

fs.writeFileSync(outputFile, JSON.stringify(posts, null, 2))
console.log(`生成完成：${posts.length} 篇文章`)
```

关键决策点：
- **构建时渲染**而非运行时渲染——文章详情页零 JS 计算，直出 HTML
- **单 JSON 文件**——博客内容量级不会太大，一个文件足够，省去多次请求
- **slug 来自文件名**——URL 美观且稳定，SEO 友好

## 在 package.json 中挂载

```json
{
  "scripts": {
    "generate-posts": "npx tsx scripts/generate-posts-json.ts",
    "build": "npm run generate-posts && vue-tsc -b && vite build"
  }
}
```

`tsx` 可以直接执行 TypeScript，不用先编译脚本。

## Vue 端如何使用

**首页**只需 fetch JSON，拿元数据渲染列表：

```typescript
// HomeView.vue
const posts = ref<PostMeta[]>([])

onMounted(async () => {
  const res = await fetch('/posts-index.json')
  posts.value = await res.json()
})
```

**文章详情页**根据 URL 中的 slug 查找对应文章，直接输出预渲染的 HTML：

```typescript
// PostView.vue
const route = useRoute()
const post = ref<Post | null>(null)

onMounted(async () => {
  const slug = route.params.slug as string
  const res = await fetch('/posts-index.json')
  const posts: Post[] = await res.json()
  post.value = posts.find(p => p.slug === slug) || null

  document.title = `${post.value?.title} | 我的博客`
})
```

```html
<!-- 模板中直接 v-html 渲染 -->
<div class="prose max-w-none" v-html="post?.html"></div>
```

## 全文搜索实现

用 Fuse.js 在前端做模糊搜索，无需后端：

```typescript
// useSearch.ts
import { ref, computed } from 'vue'
import Fuse from 'fuse.js'
import type { PostMeta } from '@/types/post'

const searchQuery = ref('')
const posts = ref<PostMeta[]>([])

export function useSearch() {
  const fuse = computed(() =>
    new Fuse(posts.value, {
      keys: ['title', 'excerpt', 'tags', 'category'],
      threshold: 0.3,          // 0=完全匹配，1=宽松匹配
      includeScore: true,
    })
  )

  const results = computed(() => {
    if (!searchQuery.value.trim()) return []
    return fuse.value.search(searchQuery.value).map(r => r.item)
  })

  function setPosts(p: PostMeta[]) {
    posts.value = p
  }

  return { searchQuery, results, setPosts }
}
```

`threshold: 0.3` 是一个折中值——既能容忍拼写偏差，又不至于返回一堆无关结果。

## 部署配置

项目根目录加一个 `vercel.json`：

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": null
}
```

推送到 GitHub，Vercel 后台导入仓库即自动部署。每次推送自动触发构建。

## 总结

这个方案的精髓在于**把复杂度推到构建时**：
- 构建时做 Markdown 解析、代码高亮、HTML 生成
- 运行时只是一个轻量的 Vue SPA，读 JSON 渲染

几百篇文章以内都用不着数据库，一个静态 JSON 文件完全够用。
