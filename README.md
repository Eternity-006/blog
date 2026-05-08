# 博客平台

多用户博客平台 — 支持注册登录、Markdown 写作、评论互动、管理后台。

**线上地址**：https://eternity-006.github.io/blog/（前端展示）
**后端 API**：部署于 [Render.com](https://render.com)（一体化部署后全功能可用）

---

## 快速开始

```bash
# 1. 安装前端依赖
npm install

# 2. 安装后端依赖
cd backend && pip install -r requirements.txt && cd ..

# 3. 启动后端（终端1）
cd backend && python app.py
# → http://localhost:5000

# 4. 启动前端（终端2）
npm run dev
# → http://localhost:5173（自动代理 /api 到后端）
```

首次启动后端会自动：
- 创建 SQLite 数据库 `backend/blog.db`
- 创建管理员账号 `admin` / `admin`
- 将 `posts/` 目录下的 Markdown 文章迁移到数据库

### 线上体验

- 访问首页，浏览所有用户发布的文章
- 点击「注册」创建自己的账号
- 登录后进入 `/admin` 写文章（支持草稿/发布）
- 在任意文章下发表评论
- 管理员登录后访问 `/dashboard` 进入管理后台

---

## 技术栈

| 层面 | 方案 |
|------|------|
| 前端框架 | Vue 3（Composition API + `<script setup>`） |
| 构建工具 | Vite 8 |
| 路由 | Vue Router 4（Hash 模式） |
| 样式 | Tailwind CSS 4 |
| 内容渲染 | markdown-it + highlight.js |
| 搜索 | Fuse.js（客户端模糊搜索） |
| 后端框架 | Flask |
| 数据库 | SQLite（零配置） |
| 认证 | JWT（PyJWT） |
| 密码加密 | werkzeug.security |
| 生产部署 | Render.com（一体化） / GitHub Pages（前端） |

---

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────┐
│                    浏览器                        │
│          Vue 3 SPA（Hash 路由）                   │
│    fetch('/api/...') → 同源或代理到 Flask         │
└──────────────────┬──────────────────────────────┘
                   │
          ┌────────▼────────┐
          │   Flask 后端     │
          │  (端口 5000)     │
          │                 │
          │  /api/auth/*    │  认证（登录/注册）
          │  /api/posts/*   │  文章 CRUD
          │  /api/comments/*│  评论
          │  /api/users/*   │  用户信息
          │  /api/admin/*   │  管理后台
          │  /              │  生产模式 serve 前端
          └────────┬────────┘
                   │
          ┌────────▼────────┐
          │    SQLite        │
          │  (blog.db)       │
          │                 │
          │  users           │
          │  posts           │
          │  comments        │
          │  post_views      │
          └─────────────────┘
```

### 数据库设计

```sql
-- 用户表
users (
  id, username, password_hash, is_admin, bio, status, created_at
)

-- 文章表
posts (
  id, slug, title, content, category, tags, excerpt,
  date, user_id → users.id, status, created_at, updated_at
)

-- 评论表
comments (
  id, post_slug, author, content, created_at
)

-- 阅读量统计
post_views (
  id, post_slug, viewed_at
)
```

### 数据流

```
用户写文章
  │
  ▼
AdminView.vue（Markdown 编辑器 + 实时预览）
  │  POST /api/posts  { slug, title, content, tags, ... }
  ▼
Flask → SQLite posts 表
  │
  ▼
GET /api/posts  →  JSON（content 为 Markdown 原文）
  │
  ▼
PostView.vue → markdown-it 客户端渲染 HTML
```

与旧架构的区别：旧架构在构建时预渲染所有文章 HTML 到一个 JSON 文件；新架构后端存储 Markdown 原文，前端按需请求 + 客户端渲染。这样支持动态内容（多用户、评论、阅读量）且构建速度不受文章数量影响。

### 权限模型

| 操作 | 未登录 | 普通用户 | 管理员 |
|------|--------|---------|--------|
| 浏览文章 | ✓ | ✓ | ✓ |
| 发表评论 | ✓ | ✓ | ✓ |
| 写文章 | | ✓（仅自己的） | ✓ |
| 编辑/删除文章 | | ✓（仅自己的） | ✓（所有） |
| 删除评论 | | ✓（仅自己文章下的） | ✓（所有） |
| 管理后台 | | | ✓ |
| 管理用户 | | | ✓ |

### API 设计

**认证**
| Method | Path | Auth | 说明 |
|--------|------|------|------|
| POST | /api/auth/register | — | 注册，返回 JWT |
| POST | /api/auth/login | — | 登录，返回 JWT |
| GET | /api/auth/me | Bearer | 当前用户信息 |

**文章**
| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | /api/posts | — | 已发布文章列表（`?author=&category=`） |
| GET | /api/posts/:slug | — | 单篇文章详情 + 阅读量 |
| GET | /api/my/posts | Bearer | 当前用户的文章（含草稿） |
| POST | /api/posts | Bearer | 创建文章 |
| PUT | /api/posts/:slug | Bearer | 更新（仅作者/管理员） |
| DELETE | /api/posts/:slug | Bearer | 删除（仅作者/管理员） |

**评论与用户**
| Method | Path | Auth | 说明 |
|--------|------|------|------|
| GET | /api/comments/:slug | — | 文章评论列表 |
| POST | /api/comments/:slug | — | 发表评论 |
| DELETE | /api/comments/:id | Bearer | 删除评论 |
| GET | /api/users | — | 用户列表 |
| GET | /api/users/:username | — | 用户主页 + 其文章 |

**管理后台（需管理员）**
| Method | Path | 说明 |
|--------|------|------|
| GET | /api/admin/stats | 统计数据（用户/文章/评论/阅读量） |
| GET | /api/admin/users | 所有用户列表 |
| PUT | /api/admin/users/:id | 修改用户（封禁/解封/角色/重置密码） |
| DELETE | /api/admin/users/:id | 删除用户及其内容 |
| GET | /api/admin/posts | 所有文章（含草稿） |

---

## 项目结构

```
blog/
├── backend/
│   ├── app.py              # Flask 入口 + 全部 API 路由
│   ├── auth.py             # JWT 生成/验证 + 权限装饰器
│   ├── db.py               # SQLite 初始化（4 张表）
│   ├── requirements.txt    # Python 依赖
│   └── blog.db             # SQLite 数据库（gitignore）
├── posts/                  # Markdown 文章源文件
├── scripts/
│   ├── generate-posts-json.ts  # 构建脚本：MD → JSON + RSS
│   └── post-api.ts             # Vite 插件（开发环境辅助 API）
├── src/
│   ├── main.ts             # 入口
│   ├── App.vue             # 根组件（布局框架）
│   ├── router/index.ts     # 路由 + 导航守卫
│   ├── types/post.ts       # 类型定义
│   ├── utils/markdown.ts   # Markdown 渲染 + 工具函数
│   ├── composables/
│   │   ├── useDarkMode.ts  # 暗色模式
│   │   ├── useSearch.ts    # Fuse.js 搜索
│   │   └── useAuth.ts      # 认证状态管理
│   ├── components/
│   │   ├── AppHeader.vue   # 顶部导航（登录状态/用户菜单）
│   │   ├── PostCard.vue    # 文章卡片
│   │   ├── PostList.vue    # 文章列表 + 分页
│   │   ├── TagBadge.vue    # 标签组件
│   │   ├── SearchBox.vue   # 搜索框
│   │   ├── TOC.vue         # 文章目录
│   │   ├── CommentSection.vue  # 自有评论系统
│   │   └── ThemeToggle.vue # 暗色模式开关
│   └── views/
│       ├── HomeView.vue        # 首页
│       ├── PostView.vue        # 文章详情
│       ├── CategoryView.vue    # 分类页
│       ├── TagView.vue         # 标签页
│       ├── SearchView.vue      # 搜索结果
│       ├── AboutView.vue       # 关于页
│       ├── LoginView.vue       # 登录页
│       ├── RegisterView.vue    # 注册页
│       ├── UserView.vue        # 用户主页
│       ├── UsersView.vue       # 用户列表
│       ├── AdminView.vue       # 文章编辑器（含草稿功能）
│       └── AdminDashboard.vue  # 管理后台（统计/用户管理/文章管理）
├── .github/workflows/deploy.yml   # GitHub Pages 自动部署
├── vercel.json                # Vercel 部署配置
├── vite.config.ts             # Vite 配置
├── vercel.json                # Vercel 部署（备选）
└── package.json
```

---

## 部署

本项目分两部分部署：**Vercel（前端）** + **PythonAnywhere（后端）**，两者都是免费的。

### 架构

```
用户浏览器
    │
    ├── https://your-blog.vercel.app     ← Vercel（前端静态文件）
    │       │
    │       └── fetch('/api/...') ──────→ https://your-app.pythonanywhere.com（后端 API）
    │
    └── 评论、登录、写文章等所有动态功能 → 后端处理
```

### 第一步：部署后端到 PythonAnywhere

1. 去 [pythonanywhere.com](https://www.pythonanywhere.com) 注册免费账号
2. 进入 **Consoles → Bash**，克隆仓库：
   ```bash
   git clone https://github.com/eternity-006/blog.git
   ```
3. 进入 **Web → Add a new web app**：
   - 选择 **Flask**
   - Python 版本选最新的（如 3.11）
   - 路径填：`/home/你的用户名/blog/backend`
4. 编辑 WSGI 配置文件（Web 页面有链接），替换为：
   ```python
   import sys
   sys.path.insert(0, '/home/你的用户名/blog/backend')
   from app import app as application
   ```
5. 在 Bash 中安装依赖：
   ```bash
   cd ~/blog/backend && pip install --user -r requirements.txt
   ```
6. 点击 Web 页面的 **Reload** 按钮

你的后端地址是：`https://你的用户名.pythonanywhere.com`

### 第二步：部署前端到 Vercel

1. 去 [vercel.com](https://vercel.com) 用 GitHub 注册
2. **Add New → Project**，导入你的博客仓库
3. **Environment Variables** 中添加：
   - `VITE_API_URL` = `https://你的用户名.pythonanywhere.com`
4. 点击 **Deploy**，等 1 分钟即可

之后每次 `git push`，Vercel 自动重新部署前端。

### 备选：GitHub Pages（仅前端）

仅部署静态前端，后端功能不可用。推送代码到 `master` 分支，GitHub Actions 自动部署到 `https://eternity-006.github.io/blog/`。

---

## 功能清单

- Markdown 写作 + 实时预览 + 代码语法高亮
- 文章草稿/发布状态管理
- 文章分类 / 标签 / 分页
- 全文模糊搜索（标题 + 摘要 + 标签 + 分类）
- 文章目录（TOC）
- 用户注册 / 登录（JWT 认证）
- 多用户博客（每人独立写作，仅可编辑自己的文章）
- 自有评论系统（无需第三方服务）
- 用户发现（浏览所有注册用户及文章）
- 阅读量统计
- 管理后台（统计面板 + 用户管理 + 文章管理）
- 用户管理（封禁/解封/角色设置/密码重置）
- 暗色模式
- 响应式布局（移动端适配）
- RSS 订阅
- Vercel + PythonAnywhere 免费部署

### 前端容错

当后端不可用时，前端自动回退到构建时生成的 `posts-index.json`，
首页和文章详情页仍然可以正常浏览（静态模式）。
