---
title: "Vue 3 Composition API 实战进阶"
date: "2026-05-01"
category: "前端"
tags: ["vue", "typescript"]
excerpt: "从实际场景出发，深入掌握 Vue 3 Composition API 的高级用法：数据请求、表单处理、事件总线组合函数及状态管理。"
---

## 从一个真实需求开始

假设我们要做一个后台管理页面：加载用户列表、支持搜索筛选、分页、以及表单弹窗编辑。如果用 Options API 写，一个组件会膨胀到几百行，四处散落着 `this.xxx`。而 Composition API 可以把它拆得干净利落。

## 封装通用的数据请求 Composable

这是最常用的模式之一——把加载状态、错误处理、数据缓存打包在一起：

```typescript
// useRequest.ts
import { ref, unref, type Ref, type MaybeRef } from 'vue'

interface UseRequestOptions<T> {
  immediate?: boolean
  onSuccess?: (data: T) => void
  onError?: (err: Error) => void
}

export function useRequest<T>(
  fetcher: (...args: any[]) => Promise<T>,
  options: UseRequestOptions<T> = {}
) {
  const { immediate = true, onSuccess, onError } = options

  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(...args: any[]) {
    loading.value = true
    error.value = null
    try {
      const result = await fetcher(...args)
      data.value = result
      onSuccess?.(result)
      return result
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      error.value = err
      onError?.(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  if (immediate) execute()

  return { data, loading, error, execute }
}
```

使用起来很简单：

```typescript
// 组件中
const { data: users, loading, execute: refresh } = useRequest(
  () => fetch('/api/users').then(r => r.json())
)
```

## 可搜索的分页列表

把筛选条件和分页逻辑再独立封装：

```typescript
// usePagination.ts
import { ref, computed, watch, type Ref } from 'vue'

interface PaginationState {
  page: number
  pageSize: number
  total: number
}

export function usePagination(pageSize = 10) {
  const state = ref<PaginationState>({
    page: 1,
    pageSize,
    total: 0,
  })

  const totalPages = computed(() => Math.ceil(state.value.total / state.value.pageSize))

  function setTotal(total: number) {
    state.value.total = total
  }

  function goTo(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      state.value.page = page
    }
  }

  function reset() {
    state.value.page = 1
  }

  return { state, totalPages, setTotal, goTo, reset }
}
```

配合搜索筛选：

```typescript
// useFilter.ts
import { ref, computed, type Ref } from 'vue'

export function useFilter<T extends Record<string, any>>(
  list: Ref<T[]>,
  filterKeys: (keyof T)[]
) {
  const search = ref('')

  const filtered = computed(() => {
    if (!search.value.trim()) return list.value
    const keyword = search.value.toLowerCase()
    return list.value.filter(item =>
      filterKeys.some(key => {
        const val = item[key]
        return typeof val === 'string' && val.toLowerCase().includes(keyword)
      })
    )
  })

  return { search, filtered }
}
```

## 表单弹窗 Composable

弹窗开关、表单数据、校验逻辑，全部收进一个函数：

```typescript
// useModal.ts
import { ref, reactive } from 'vue'

export function useModal<T extends Record<string, any>>(initialData: T) {
  const visible = ref(false)
  const form = reactive({ ...initialData }) as T
  const isEdit = ref(false)

  function open(data?: Partial<T>) {
    if (data) {
      Object.assign(form, initialData, data)
      isEdit.value = true
    } else {
      Object.assign(form, initialData)
      isEdit.value = false
    }
    visible.value = true
  }

  function close() {
    visible.value = false
  }

  return { visible, form, isEdit, open, close }
}
```

## 在组件中组装

把所有 Composable 组合在一起，逻辑清爽、一目了然：

```vue
<script setup lang="ts">
import { useRequest } from '@/composables/useRequest'
import { usePagination } from '@/composables/usePagination'
import { useFilter } from '@/composables/useFilter'
import { useModal } from '@/composables/useModal'

interface User {
  id: number
  name: string
  email: string
  role: string
}

// 数据请求
const { data: users, loading, execute: refresh } = useRequest<User[]>(
  () => fetch('/api/users').then(r => r.json())
)

// 搜索筛选
const { search, filtered } = useFilter(users, ['name', 'email'])

// 分页
const { state, totalPages, goTo, reset: resetPage } = usePagination(10)

// 编辑弹窗
const { visible, form, isEdit, open, close } = useModal<User>({
  id: 0, name: '', email: '', role: 'editor'
})

function handleSearch(val: string) {
  search.value = val
  resetPage()
}

async function handleSubmit() {
  const url = isEdit.value ? `/api/users/${form.id}` : '/api/users'
  const method = isEdit.value ? 'PUT' : 'POST'
  await fetch(url, { method, body: JSON.stringify(form) })
  close()
  refresh()
}
</script>
```

## 总结

Composition API 的价值不在于 "setup 比 Options 写法更酷"，而在于它迫使你把逻辑按**关注点**拆分。一个几百行的臃肿组件，拆成三五个独立的 Composable 后，每个都不超过 50 行，可单独测试、可跨组件复用——这才是它真正的力量。
