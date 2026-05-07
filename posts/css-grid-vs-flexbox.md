---
title: "CSS Grid 与 Flexbox 实战布局指南"
date: "2026-04-15"
category: "CSS"
tags: ["css", "layout"]
excerpt: "用四个真实页面布局案例，彻底掌握 Grid 和 Flexbox 的配合之道：经典三段式、卡片瀑布流、仪表盘栅格及居中方案全对比。"
---

## 案例一：经典后台管理布局（Grid 主攻）

几乎所有后台系统都长这样：侧栏 + 头部 + 内容区 + 底部。Grid 的 `grid-template-areas` 是描述这种布局最自然的方式：

```css
.admin-layout {
  display: grid;
  grid-template-areas:
    "sidebar header"
    "sidebar main"
    "sidebar footer";
  grid-template-columns: 240px 1fr;
  grid-template-rows: 56px 1fr auto;
  min-height: 100vh;
}

.sidebar { grid-area: sidebar; }
.header  { grid-area: header; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

```html
<div class="admin-layout">
  <aside class="sidebar">侧栏导航</aside>
  <header class="header">顶部栏</header>
  <main class="main">内容区域</main>
  <footer class="footer">状态栏</footer>
</div>
```

优势一目了然：CSS 即文档——看 `grid-template-areas` 的 ASCII 排列就能脑补出页面结构，维护时不用去 HTML 里翻找。

**侧栏内部**再用 Flexbox 处理导航项：

```css
.sidebar {
  background: #1e293b;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  transition: background 0.2s;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-spacer {
  flex: 1;  /* 把底部项推到底部 */
}
```

## 案例二：自适应卡片网格（Grid 主攻）

文章列表、商品展示、项目卡片——这类需求的核心是"不知道一行该放几个，但每个卡片不能太窄"：

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

`minmax(280px, 1fr)` 是关键——每个卡片最少 280px，如果空间有余则均分。配合 `auto-fill`，浏览器自动计算列数，不需要任何媒体查询就能实现响应式。

完整的卡片样式：

```css
.card {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #fff;
  transition: box-shadow 0.3s, transform 0.3s;
}

.card:hover {
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.card-body {
  flex: 1;                   /* 撑满剩余空间 */
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

## 案例三：仪表盘数据面板（Grid + Flexbox 混合）

仪表盘的特点是：有跨越多个列的大图表、有标准尺寸的小指标卡、排列必须精确对齐：

```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 160px;
  gap: 1rem;
}

/* 统计卡片占 1 列 × 1 行 */
.stat-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-radius: 0.75rem;
  padding: 1.25rem;
}

.stat-card .value {
  font-size: 2rem;
  font-weight: 700;
}

.stat-card .label {
  font-size: 0.875rem;
  opacity: 0.8;
}

/* 大图表占 2 列 × 3 行 */
.chart-large {
  grid-column: span 2;
  grid-row: span 3;
  background: #fff;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

/* 中等图表占 2 列 × 2 行 */
.chart-medium {
  grid-column: span 2;
  grid-row: span 2;
  background: #fff;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}

/* 活动列表占 1 列 × 2 行 */
.activity-list {
  grid-row: span 2;
  background: #fff;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
}
```

```html
<div class="dashboard">
  <div class="stat-card"><span class="value">12,845</span><span class="label">访问量</span></div>
  <div class="stat-card"><span class="value">3,201</span><span class="label">订单数</span></div>
  <div class="stat-card"><span class="value">¥86.4K</span><span class="label">营收</span></div>
  <div class="stat-card"><span class="value">94.2%</span><span class="label">转化率</span></div>

  <div class="chart-large">趋势图</div>
  <div class="activity-list">
    <div class="activity-item" v-for="...">最新订单</div>
  </div>
  <div class="chart-medium">来源分布</div>
</div>
```

直接看 CSS 就能数出页面布局——这就是 Grid 的表达力。

## 案例四：居中的艺术（Flexbox 碾压一切）

面试常问的"垂直水平居中"，Flexbox 三行搞定所有场景：

```css
/* 方案 1：父容器一行搞定 */
.center-flex {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

/* 方案 2：子元素用 margin auto（单项居中） */
.center-margin {
  display: flex;
  min-height: 100vh;
}
.center-margin > .box {
  margin: auto;   /* Flex 容器内 margin:auto 吸收所有剩余空间 */
}
```

Grid 也能做居中，但没 Flexbox 简洁：

```css
/* Grid 方案 —— 三行，无显著优势 */
.center-grid {
  display: grid;
  place-items: center;   /* justify-items + align-items 的简写 */
  min-height: 100vh;
}
```

## 选型清单

| 你的需求 | 用这个 | 理由 |
|----------|--------|------|
| 页面整体框架（多区域排列） | Grid | `grid-template-areas` 语义清晰 |
| 一行导航、一排按钮 | Flexbox | 一维排列是 Flexbox 的原生优势 |
| 自适应卡片网格 | Grid + `auto-fill` | 不用媒体查询自动换行列 |
| 内容垂直居中 | Flexbox | 三行代码，可读性最高 |
| 仪表盘（跨行跨列） | Grid | `span` 是描述跨行列最自然的方式 |
| 列表内元素两端对齐 | Flexbox + `space-between` | 语义精确、代码极简 |
| 复杂表单（标签和控件对线） | Grid | 天然的两列对齐能力 |

## 总结

Grid 解决"页面长什么样"（宏观），Flexbox 解决"内容怎么流"（微观）。它们不是竞争关系——Grid 画骨架，Flexbox 填肌肉，配合使用才是正道。
