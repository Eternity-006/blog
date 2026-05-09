# 博客平台

多用户博客平台 — 注册登录、Markdown 写作、评论互动、管理后台、暗色模式。

**本地运行即可完整体验所有功能**，无需任何线上部署。

---

## 快速开始

```bash
# 1. 安装前端依赖（仅首次）
npm install

# 2. 安装后端依赖（仅首次）
cd backend && pip install -r requirements.txt && cd ..

# 3. 启动后端（终端1）
cd backend && python app.py
# → http://localhost:5000

# 4. 启动前端（终端2）
npm run dev
# → http://localhost:5173
```

浏览器打开 `http://localhost:5173` 即可使用。

首次启动后端会自动：
- 创建 SQLite 数据库 `backend/blog.db`
- 创建管理员账号 `admin` / `admin`
- 将 `posts/` 目录下的 Markdown 文章迁移到数据库（归属 admin）

---

## 设计思路

### 为什么做这个项目

市面上博客方案很多，但要么太重（WordPress），要么太轻（纯静态生成器），要么需要注册第三方服务。这个项目的目标是：**本地一条命令就能跑起来的完整博客系统**，同时兼顾真实多用户场景。

### 几个关键决策

**1. "动态后端 + 静态兜底"双模运行**

正常模式下前端调 Flask API，所有数据实时读写。一旦后端不可用（比如部署到 GitHub Pages 时），前端自动降级为从 `posts-index.json` 读预构建的静态数据，首页和文章详情仍然可浏览。这个机制让同一份代码既能全功能运行，也能作为纯静态站点部署。

**2. Markdown 原文存储，客户端渲染**

后端数据库存 Markdown 原文，不做预渲染。前端请求到原文后用 markdown-it 在浏览器端渲染。好处是：
- 写作体验纯粹，编辑器里看到的就是原始 Markdown
- 构建速度不受文章数量影响
- 随时可以切换渲染器或调整样式

**3. SQLite 单文件数据库**

零配置、零进程、备份就是复制文件。对于一个个人或小团队博客，SQLite 在 10 万篇文章以内性能完全够用。WAL 模式保证读写并发，`flask g` 按请求管理连接。

**4. Hash 路由**

Vue Router 用 Hash 模式（`#/post/slug`）而非 History 模式。这样做的好处是前端部署不需要服务端 fallback 配置，直接把 `dist/` 扔到任意静态服务器就能工作。

**5. JWT 无状态认证**

不用 session，不用 Redis。登录后签发一个 7 天有效的 JWT，存 localStorage。每次请求带 `Authorization: Bearer <token>`，后端装饰器自动验签、注入用户信息。简单、轻量、可水平扩展。

### 不做什么

- 不做图片上传（封面图用 URL 引用）
- 不做邮件通知（保持依赖极简）
- 不做 OAuth / 第三方登录（注册 3 个字段的事，不需要引入社交账号体系）
- 不做多级评论嵌套（只做两级：评论 + 回复，再深可读性反而下降）

---

## 架构设计

### 整体架构

```
┌──────────────────────────────────────────────────┐
│                     浏览器                        │
│           Vue 3 SPA（Hash 路由 #/xxx）             │
│    api('/api/...') → 自动拼接后端 URL 或空路径      │
└───────────────────┬──────────────────────────────┘
                    │
           ┌────────▼─────────┐
           │   Flask 后端      │
           │  (端口 5000)      │
           │                  │
           │  /api/auth/*     │  认证模块（登录/注册）
           │  /api/posts/*    │  文章 CRUD
           │  /api/comments/* │  评论系统
           │  /api/favorites/*│  收藏系统
           │  /api/users/*    │  用户发现
           │  /api/admin/*    │  管理后台
           │  /api/rss        │  RSS 订阅
           │  /api/my/*       │  我的文章/收藏
           │  /*              │  生产模式 serve dist/
           └────────┬─────────┘
                    │
           ┌────────▼─────────┐
           │     SQLite        │
           │   (blog.db)       │
           │                   │
           │  users            │  用户 + 角色 + 状态
           │  posts            │  文章 + 归属 + 状态 + 封面 + 置顶
           │  comments         │  评论 + 嵌套回复
           │  favorites        │  用户收藏
           │  post_views       │  阅读量统计
           └───────────────────┘
```

### 开发模式 vs 生产模式

```
开发模式 (npm run dev)              生产模式 (python app.py + dist/)
┌──────────┐  /api/*   ┌────────┐  ┌──────────┐       ┌────────┐
│ Vite 5173 │ ──────→ │ Flask   │  │ 浏览器    │ ────→ │ Flask   │
│ 热更新 ✓  │ ←────── │ :5000   │  │          │ ←──── │ :5000   │
│ HMR ✓    │  proxy  │         │  │  所有请求  │       │ serve   │
└──────────┘         └────────┘  └──────────┘       │ dist/   │
                                                     └────────┘
```

开发时 Vite dev server 把 `/api/*` 代理到 Flask 的 5000 端口，享受毫秒级热更新。生产时 Flask 直接 serve 前端构建产物，单进程同时提供 API 和静态文件。

### 数据流

```
用户写文章
  │
  ▼
AdminView.vue（Markdown 编辑器 + 实时预览 + 封面图 + slug 自动生成）
  │  POST /api/posts  { slug, title, content, tags, cover_image, status, ... }
  ▼
Flask 解析 → SQLite INSERT
  │
  ▼  读者请求 /post/:slug
  │  GET /api/posts/:slug → SQLite → JSON { content: "## 标题\n...", ... }
  ▼
PostView.vue → markdown-it 客户端渲染 → v-html 展示
  │
  ▼  同时记录阅读量 + 可收藏 + 看相关推荐
  INSERT INTO post_views  /  INSERT INTO favorites
```

### 数据库设计

```sql
-- 用户表：多角色 + 封禁状态
users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,          -- werkzeug bcrypt
  is_admin INTEGER DEFAULT 0,          -- 0=普通 1=管理员
  bio TEXT DEFAULT '',
  status TEXT DEFAULT 'active',        -- active / banned
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 文章表：Markdown 原文存储 + 封面图 + 置顶
posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT UNIQUE NOT NULL,            -- URL 友好标识
  title TEXT NOT NULL,
  content TEXT NOT NULL,                -- Markdown 原文
  category TEXT DEFAULT '',
  tags TEXT DEFAULT '',                 -- CSV 逗号分隔
  excerpt TEXT DEFAULT '',
  cover_image TEXT DEFAULT '',          -- 封面图 URL
  date TEXT NOT NULL,
  user_id INTEGER NOT NULL REFERENCES users(id),
  status TEXT DEFAULT 'published',      -- published / draft
  pinned INTEGER DEFAULT 0,            -- 0=普通 1=置顶
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 评论表：支持嵌套回复
comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_slug TEXT NOT NULL,
  author TEXT NOT NULL,
  content TEXT NOT NULL,
  parent_id INTEGER,                   -- NULL=顶级评论, 其他=回复某评论
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

-- 收藏表：用户-文章多对多
favorites (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  post_slug TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, post_slug)
)

-- 阅读统计：每次访问记录一条
post_views (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  post_slug TEXT NOT NULL,
  viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 权限模型

| 操作 | 未登录 | 普通用户 | 管理员 |
|------|:---:|:---:|:---:|
| 浏览文章、看评论 | ✓ | ✓ | ✓ |
| 发表评论/回复 | ✓ | ✓ | ✓ |
| 收藏文章 | | ✓ | ✓ |
| 注册、登录 | ✓ | ✓ | ✓ |
| 写文章 | | ✓ | ✓ |
| 编辑/删除自己的文章 | | ✓ | ✓ |
| 置顶文章 | | | ✓ |
| 编辑/删除任意文章 | | | ✓ |
| 删除任意评论 | | | ✓ |
| 管理用户（封禁/角色/密码） | | | ✓ |
| 删除用户 | | | ✓ |

---

## 项目结构

```
blog/
├── backend/
│   ├── app.py                  # Flask 入口 + 全部 API 路由
│   ├── auth.py                 # JWT 生成/验证 + 装饰器
│   ├── db.py                   # SQLite 连接 + 初始化 + 迁移
│   ├── requirements.txt        # flask, flask-cors, pyjwt, werkzeug, gunicorn
│   └── blog.db                 # SQLite 数据库文件（gitignore）
│
├── posts/                      # Markdown 文章源文件（首次启动迁移到 DB）
│
├── scripts/
│   └── generate-posts-json.ts  # 构建脚本：MD → posts-index.json + RSS（静态兜底用）
│
├── src/
│   ├── main.ts                 # Vue 应用入口
│   ├── App.vue                 # 根组件（布局 + Toast 容器 + 页面过渡动画）
│   ├── api.ts                  # API 请求封装（读取 VITE_API_URL 拼接地址）
│   │
│   ├── router/index.ts         # 路由表 + 导航守卫（auth / admin 校验）
│   ├── types/post.ts           # PostMeta / Post / PaginatedResponse 类型
│   │
│   ├── utils/
│   │   └── markdown.ts         # markdown-it 渲染 + TOC 提取 + 阅读时长
│   │
│   ├── composables/
│   │   ├── useAuth.ts          # 认证状态：token、登录、注册、登出
│   │   ├── useToast.ts         # Toast 通知：success / error / info
│   │   ├── useCodeCopy.ts      # 代码块一键复制
│   │   ├── useSearch.ts        # Fuse.js 客户端模糊搜索
│   │   └── useDarkMode.ts      # 暗色模式切换 + localStorage 持久化
│   │
│   ├── components/
│   │   ├── AppHeader.vue       # 顶部导航（响应式 + 汉堡菜单）
│   │   ├── PostCard.vue        # 文章卡片（封面图 + 置顶角标 + 标签）
│   │   ├── PostList.vue        # 文章列表 + 分页（支持双模：服务端/客户端）
│   │   ├── Pagination.vue      # 通用分页控件
│   │   ├── SkeletonCard.vue    # 骨架屏占位卡片
│   │   ├── CommentSection.vue  # 评论系统（嵌套回复 + 两级结构）
│   │   ├── RelatedPosts.vue    # 相关文章推荐
│   │   ├── TagBadge.vue        # 标签徽章
│   │   ├── SearchBox.vue       # 导航栏搜索框
│   │   ├── TOC.vue             # 文章目录（sticky 侧栏）
│   │   ├── Toast.vue           # Toast 通知容器
│   │   └── ThemeToggle.vue     # 暗色模式切换按钮
│   │
│   ├── views/
│   │   ├── HomeView.vue        # 首页：文章列表 + 骨架屏 + 分页
│   │   ├── PostView.vue        # 文章详情：进度条 + 封面 + 收藏 + 推荐 + 评论
│   │   ├── CategoryView.vue    # 分类过滤 + 分页
│   │   ├── TagView.vue         # 标签过滤
│   │   ├── SearchView.vue      # 全文模糊搜索 + 骨架屏
│   │   ├── AboutView.vue       # 关于页
│   │   ├── LoginView.vue       # 登录页
│   │   ├── RegisterView.vue    # 注册页
│   │   ├── UserView.vue        # 用户主页（文章列表 + 收藏 tab）
│   │   ├── UsersView.vue       # 用户发现页
│   │   ├── AdminView.vue       # 文章编辑器（Markdown + 预览 + 封面图）
│   │   └── AdminDashboard.vue  # 管理后台（统计 + 用户表 + 文章表 + 置顶）
│   │
│   └── styles/
│       └── main.css            # Tailwind 4 入口 + prose 样式 + highlight.js 暗色
│
├── .github/workflows/deploy.yml  # GitHub Pages 自动部署
├── vercel.json                   # Vercel 部署配置
├── render.yaml                   # Render 部署配置
├── vite.config.ts                # Vite 配置（别名、代理、插件）
└── package.json
```

---

## 功能清单

### 内容
- Markdown 写作 + 实时预览 + 代码语法高亮
- 文章草稿 / 发布状态管理
- 文章封面图（URL 引用）
- 文章分类 / 标签 / 分页
- 文章置顶（管理员）
- 全文模糊搜索（标题 + 摘要 + 标签 + 分类）
- 文章目录（TOC，sticky 侧栏）
- 相关文章推荐（按标签匹配）
- RSS 动态订阅

### 用户
- 注册 / 登录（JWT 无状态认证）
- 多用户创作（每人独立管理自己的文章）
- 文章收藏（登录后一键收藏/取消）
- 用户发现（浏览所有注册用户）
- 用户主页（文章 + 收藏 tab）

### 评论
- 自有评论系统（无需第三方）
- 嵌套回复（两级：评论 + 回复）
- 匿名评论（未填昵称默认"匿名"）
- 登录用户可删除评论

### 管理
- 统计面板（用户 / 文章 / 草稿 / 评论 / 阅读量）
- 用户管理（封禁 / 解封 / 角色设置 / 密码重置 / 删除）
- 文章管理（查看全部含草稿，可置顶 / 删除）

### UI/UX
- 骨架屏加载（列表页灰色占位 + pulse 动画）
- Toast 通知（右上角弹出，3 秒自动消失）
- 代码块一键复制
- 阅读时长估算（中英文分别计算）
- 文章阅读进度条（顶部渐变色条）
- 暗色模式（localStorage 记忆 + 系统偏好检测）
- 响应式布局（移动端汉堡菜单）
- 页面过渡动画（fade）

### 容错
- 后端不可用时自动回退到 `posts-index.json` 静态模式
- 首页和文章详情仍可正常浏览

---

## API 参考

### 认证

| Method | Path | Auth | 说明 |
|--------|------|:---:|------|
| POST | /api/auth/register | — | 注册，返回 `{ token, user }` |
| POST | /api/auth/login | — | 登录，返回 `{ token, user }` |
| GET | /api/auth/me | Bearer | 获取当前用户信息 |

### 文章

| Method | Path | Auth | 说明 |
|--------|------|:---:|------|
| GET | /api/posts | — | 已发布文章列表，支持 `?page=&per_page=&author=&category=&tag=` |
| GET | /api/posts/:slug | — | 单篇文章详情 + 阅读量 |
| GET | /api/posts/:slug/related | — | 相关文章推荐（最多 3 篇） |
| GET | /api/my/posts | Bearer | 当前用户的全部文章（含草稿） |
| POST | /api/posts | Bearer | 创建文章 |
| PUT | /api/posts/:slug | Bearer | 更新文章（仅作者或管理员） |
| DELETE | /api/posts/:slug | Bearer | 删除文章（仅作者或管理员） |

分页响应格式：`{ posts: [], total, page, per_page, total_pages }`

### 评论

| Method | Path | Auth | 说明 |
|--------|------|:---:|------|
| GET | /api/comments/:slug | — | 文章评论列表（含 parent_id） |
| POST | /api/comments/:slug | — | 发表评论或回复，可选 `parent_id` |
| DELETE | /api/comments/:id | Bearer | 删除评论 |

### 收藏

| Method | Path | Auth | 说明 |
|--------|------|:---:|------|
| POST | /api/favorites/:slug | Bearer | Toggle 收藏/取消，返回 `{ favorited: bool }` |
| GET | /api/favorites/:slug | Bearer | 检查是否已收藏 `{ favorited: bool }` |
| GET | /api/my/favorites | Bearer | 收藏文章列表 |

### 用户

| Method | Path | Auth | 说明 |
|--------|------|:---:|------|
| GET | /api/users | — | 所有活跃用户列表 |
| GET | /api/users/:username | — | 用户信息 + 其已发布文章 |

### 管理后台（需管理员）

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/admin/stats | 统计数据（用户/文章/草稿/评论/阅读量） |
| GET | /api/admin/users | 所有用户列表（含文章数） |
| PUT | /api/admin/users/:id | 修改用户：角色、状态、密码 |
| DELETE | /api/admin/users/:id | 删除用户及其文章、评论 |
| GET | /api/admin/posts | 所有文章（含草稿），支持 `?page=&per_page=` |
| POST | /api/admin/posts/:slug/pin | Toggle 文章置顶 |

### 其他

| Method | Path | 说明 |
|--------|------|------|
| GET | /api/rss | RSS 2.0 订阅（最近 20 篇已发布） |

---

## 部署

### 本地运行（推荐零成本体验）

不需要部署，本地即可完整体验所有功能：

```bash
# 终端1：启动后端
cd backend && python app.py

# 终端2：启动前端
npm run dev
```

### Vercel + PythonAnywhere（免费线上部署）

如需公网访问：

**第一步：部署后端到 PythonAnywhere**

1. 注册 [pythonanywhere.com](https://pythonanywhere.com)（免费账号）
2. Consoles → Bash → 克隆仓库：
   ```bash
   git clone https://github.com/你的用户名/blog.git
   ```
3. Web → Add a new web app → Flask + Python 3.11
4. 路径填 `/home/你的用户名/blog/backend`
5. 编辑 WSGI 文件为：
   ```python
   import sys
   sys.path.insert(0, '/home/你的用户名/blog/backend')
   from app import app as application
   ```
6. Bash 安装依赖：`pip install --user -r ~/blog/backend/requirements.txt`
7. 点击 Reload，后端地址：`https://你的用户名.pythonanywhere.com`

**第二步：部署前端到 Vercel**

1. 注册 [vercel.com](https://vercel.com)，关联 GitHub
2. Import 仓库 → Environment Variables 添加：
   - `VITE_API_URL` = `https://你的用户名.pythonanywhere.com`
3. Deploy，之后每次 push 自动更新

### Render（全栈一键部署）

参考 `render.yaml`，支持前后端单服务部署。设置环境变量 `FLASK_ENV=production`。

### GitHub Pages（仅静态前端）

推送代码到 `master` 分支，GitHub Actions 自动构建部署。仅展示静态内容——登录、评论、收藏等功能不可用，自动降级到 `posts-index.json` 加载。

---

## 技术栈

| 层面 | 方案 | 选型理由 |
|------|------|---------|
| 前端框架 | Vue 3（Composition API） | 逻辑复用方便，TypeScript 支持好 |
| 构建工具 | Vite 8 | 秒级热更新，开发体验极佳 |
| 路由 | Vue Router 4（Hash 模式） | 无需服务端配置，任意静态服务器可用 |
| 样式方案 | Tailwind CSS 4 | 原子化 CSS，暗色模式内置支持 |
| Markdown 渲染 | markdown-it + highlight.js | 代码高亮丰富，插件生态好 |
| 搜索 | Fuse.js | 客户端模糊搜索，无需后端参与 |
| 后端框架 | Flask | 轻量极简，单文件即可启动 |
| 数据库 | SQLite（原生 sqlite3） | 零配置，单文件，备份即复制 |
| 认证 | JWT（PyJWT） | 无状态，token 存 localStorage |
| 密码加密 | werkzeug.security | bcrypt 级别安全 |
