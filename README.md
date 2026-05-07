# 我的博客

基于 Vue 3 + Vite + Tailwind CSS 的 Markdown 静态博客。

**线上地址**：https://eternity-006.github.io/blog/

---

## 快速开始

```bash
# 安装依赖（仅首次）
npm install

# 本地开发
npm run dev
# 然后打开 http://localhost:5173

# 生产构建
npm run build
# 输出在 dist/ 目录
```

## 写文章

1. `npm run dev` 启动开发服务器
2. 访问 `http://localhost:5173/admin`
3. 填写标题、分类、标签、摘要等元信息
4. 左侧写 Markdown，右侧实时预览
5. 点「保存文章」，自动写入 `posts/` 目录

也可以直接在 `posts/` 目录下手动创建 `.md` 文件，格式如下：

```markdown
---
title: "文章标题"
date: "2026-05-07"
category: "前端"
tags: ["vue", "typescript"]
excerpt: "文章摘要，显示在列表页。"
---

## 正文标题

正文内容，支持 Markdown 语法和代码高亮。
```

## 部署到 GitHub Pages

推送代码到 GitHub 仓库即可自动部署：

```bash
git add .
git commit -m "更新内容"
git push
```

GitHub Actions 会自动构建并部署，约 1-2 分钟后生效。

---

## 架构设计

### 数据流

```
posts/*.md                     ← 用户写文章（Markdown + YAML 头部）
    │
    ▼ 构建时执行
scripts/generate-posts-json.ts
    │  gray-matter 解析元数据
    │  markdown-it 渲染 HTML
    │  highlight.js 代码高亮
    │
    ▼
public/
  ├── posts-index.json         ← 单文件，含所有文章的元数据 + HTML
  └── rss.xml                  ← RSS 订阅源
    │
    ▼ 运行时
Vue App（fetch JSON）
  ├── 首页     → 文章列表 + 分页
  ├── 详情页   → 直接 v-html 渲染预生成的 HTML
  ├── 分类/标签 → 前端过滤
  └── 搜索页   → Fuse.js 模糊搜索
```

### 设计决策

| 决策 | 理由 |
|------|------|
| **构建时渲染 Markdown** | 文章详情页零 JS 计算，直出 HTML，首屏更快 |
| **单 JSON 文件存储全部文章** | 博客内容量级不会太大，一个文件够用，省去多次网络请求 |
| **预生成 HTML 而非运行时渲染** | highlight.js 体积大（~1MB），只在构建时用，读者不下载 |
| **Hash 路由模式** | GitHub Pages 不支持服务端路由，`/#/post/xxx` 零配置可用 |
| **Fuse.js 客户端搜索** | 无需后端，构建为独立 chunk，不影响首页加载 |
| **Tailwind CSS v4** | 按需生成样式，CSS 体积 ~6KB gzipped |
| **暗色模式 class 策略** | 用户可手动切换，刷新后保持，同时尊重系统偏好 |

### 写文章 API（仅开发环境）

Vite dev server 提供了三个 API 端点支持在线编辑器：

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/save-post` | POST | 保存文章到 `posts/` 目录 |
| `/api/list-posts` | GET | 获取已有文章列表 |
| `/api/get-post?slug=xxx` | GET | 获取单篇文章原始 Markdown |

这些接口只在 `npm run dev` 时可用，生产环境不需要。

---

## 项目结构

```
blog/
├── posts/                          # Markdown 文章
├── scripts/
│   ├── generate-posts-json.ts      # 构建脚本：MD → JSON + RSS
│   └── post-api.ts                 # 开发服务器 API 插件
├── public/
│   ├── posts-index.json            # 构建生成的索引（含 HTML）
│   └── rss.xml                     # 构建生成的 RSS
├── src/
│   ├── main.ts                     # 入口
│   ├── App.vue                     # 根组件（布局框架）
│   ├── router/index.ts             # 路由配置
│   ├── types/post.ts               # 类型定义
│   ├── utils/markdown.ts           # Markdown 渲染 + 工具函数
│   ├── composables/
│   │   ├── useDarkMode.ts          # 暗色模式
│   │   └── useSearch.ts            # Fuse.js 搜索
│   ├── components/
│   │   ├── AppHeader.vue           # 顶部导航
│   │   ├── PostCard.vue            # 文章卡片
│   │   ├── PostList.vue            # 文章列表 + 分页
│   │   ├── TagBadge.vue            # 标签组件
│   │   ├── SearchBox.vue           # 搜索框
│   │   ├── TOC.vue                 # 文章目录
│   │   ├── CommentSection.vue      # Giscus 评论
│   │   └── ThemeToggle.vue         # 暗色模式开关
│   ├── views/
│   │   ├── HomeView.vue            # 首页
│   │   ├── PostView.vue            # 文章详情
│   │   ├── CategoryView.vue        # 分类页
│   │   ├── TagView.vue             # 标签页
│   │   ├── SearchView.vue          # 搜索结果
│   │   ├── AboutView.vue           # 关于页
│   │   └── AdminView.vue           # 文章编辑器
│   └── styles/main.css             # 全局样式 + Tailwind
├── .github/workflows/deploy.yml    # 自动部署配置
├── vite.config.ts                  # Vite 配置
├── vercel.json                     # Vercel 部署（备选）
└── package.json
```

## 技术栈

| 层面 | 方案 |
|------|------|
| 框架 | Vue 3（Composition API + `<script setup>`） |
| 构建 | Vite 8 |
| 路由 | Vue Router 4（Hash 模式） |
| 样式 | Tailwind CSS 4 |
| 内容 | Markdown + gray-matter |
| 渲染 | markdown-it + highlight.js |
| 搜索 | Fuse.js |
| 评论 | Giscus（需配置 GitHub 仓库） |
| 部署 | GitHub Pages + GitHub Actions |

## 功能清单

- Markdown 文章渲染 + 代码语法高亮
- 文章分类 / 标签 / 归档
- 全文模糊搜索（标题 + 摘要 + 标签）
- 分页
- 文章目录（TOC）
- 暗色模式
- 响应式布局（移动端适配）
- RSS 订阅
- 在线 Markdown 编辑器（实时预览）
- 自动部署（推送即上线）
