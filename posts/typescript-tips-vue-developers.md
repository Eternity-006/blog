---
title: "Vue 3 开发中不可不知的 TypeScript 高级模式"
date: "2026-04-20"
category: "前端"
tags: ["typescript", "vue", "tips"]
excerpt: "从泛型组件、可辨识联合类型到类型安全的 Provide/Inject 和 Emits 声明，全面提升 Vue 项目的类型覆盖率和代码健壮性。"
---

## 泛型组件——编写真正可复用的 UI

假设你要写一个 Select 下拉组件，选项可以是任意类型——字符串、对象、数字……泛型组件让你一次性解决：

```vue
<!-- GenericSelect.vue -->
<script setup lang="ts" generic="T">
import { computed } from 'vue'

const props = defineProps<{
  options: T[]
  modelValue: T
  labelKey?: keyof T       // 对象类型时，取哪个字段当显示文本
  valueKey?: keyof T       // 对象类型时，取哪个字段当值
}>()

const emit = defineEmits<{
  'update:modelValue': [value: T]
}>()

function getLabel(option: T): string {
  if (typeof option === 'object' && option !== null && props.labelKey) {
    return String(option[props.labelKey])
  }
  return String(option)
}

function getValue(option: T): string {
  if (typeof option === 'object' && option !== null && props.valueKey) {
    return String(option[props.valueKey])
  }
  return String(option)
}

function select(option: T) {
  emit('update:modelValue', option)
}
</script>

<template>
  <div class="relative">
    <button class="w-full border rounded px-3 py-2 text-left">
      {{ getLabel(modelValue) }}
    </button>
    <ul class="absolute top-full mt-1 w-full border rounded bg-white shadow-lg z-10">
      <li
        v-for="(option, index) in options"
        :key="getValue(option) || index"
        @click="select(option)"
        class="px-3 py-2 hover:bg-gray-100 cursor-pointer"
        :class="{ 'bg-blue-50': getValue(option) === getValue(modelValue) }"
      >
        {{ getLabel(option) }}
      </li>
    </ul>
  </div>
</template>
```

使用时类型自动推断：

```vue
<script setup lang="ts">
import { ref } from 'vue'

interface User {
  id: number
  name: string
  email: string
}

// TS 自动推断 T = User
const selected = ref<User>({ id: 0, name: '', email: '' })

const users: User[] = [
  { id: 1, name: '张三', email: 'zhang@example.com' },
  { id: 2, name: '李四', email: 'li@example.com' },
]
</script>

<template>
  <GenericSelect
    v-model="selected"
    :options="users"
    label-key="name"
    value-key="id"
  />
</template>
```

## 可辨识联合类型处理 API 状态

用联合类型建模 API 请求的三种状态，消除 `null` 检查地狱：

```typescript
// types/api.ts
type ApiState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: T }

// composables/useApi.ts
import { ref, type Ref } from 'vue'

export function useApi<T>() {
  const state = ref<ApiState<T>>({ status: 'idle' }) as Ref<ApiState<T>>

  async function execute(promise: Promise<T>) {
    state.value = { status: 'loading' }
    try {
      const data = await promise
      state.value = { status: 'success', data }
    } catch (e) {
      const error = e instanceof Error ? e : new Error(String(e))
      state.value = { status: 'error', error }
    }
  }

  function reset() {
    state.value = { status: 'idle' }
  }

  return { state, execute, reset }
}
```

在模板中，TypeScript 会精确收窄类型：

```vue
<template>
  <div>
    <!-- loading -->
    <Spinner v-if="state.status === 'loading'" />

    <!-- error — 此处 state.error 自动可用 -->
    <div v-else-if="state.status === 'error'" class="text-red-500">
      错误：{{ state.error.message }}
      <button @click="retry">重试</button>
    </div>

    <!-- success — 此处 state.data 自动可用 -->
    <div v-else-if="state.status === 'success'">
      {{ state.data }}
    </div>

    <!-- idle -->
    <p v-else>暂无数据</p>
  </div>
</template>
```

这就是**可辨识联合（Discriminated Union）**的价值——`status` 作为判别字段，TS 根据它自动推断每个分支中能访问哪些属性。

## 类型安全的 Provide / Inject

Vue 3 的 provide/inject 默认丢失类型。用 `InjectionKey` 修复：

```typescript
// providers/userProvider.ts
import { provide, inject, ref, readonly, type InjectionKey, type Ref } from 'vue'

interface UserContext {
  user: Ref<{ id: number; name: string } | null>
  login: (name: string) => void
  logout: () => void
}

// 类型安全的注入密钥
export const USER_KEY: InjectionKey<UserContext> = Symbol('user')

export function provideUser() {
  const user = ref<{ id: number; name: string } | null>(null)

  function login(name: string) {
    user.value = { id: Date.now(), name }
  }

  function logout() {
    user.value = null
  }

  provide(USER_KEY, { user: readonly(user), login, logout })
}

export function useUser(): UserContext {
  const ctx = inject(USER_KEY)
  if (!ctx) {
    throw new Error('useUser() 必须在 provideUser() 的子组件中调用')
  }
  return ctx
}
```

调用方获得完整类型提示和编译时检查：

```typescript
const { user, login, logout } = useUser()
// user: Ref<{ id: number; name: string } | null>
// login: (name: string) => void
// 全部自动推导，零手写类型
```

## 强类型的 Emits 声明

不要用数组字符串声明 emits，用泛型定义参数类型：

```vue
<script setup lang="ts">
// ❌ 弱类型，payload 是 any
// const emit = defineEmits(['update', 'delete'])

// ✅ 强类型，参数类型明确约束
const emit = defineEmits<{
  update: [id: number, payload: { name: string; email: string }]
  delete: [id: number]
  'page-change': [page: number]
}>()

// 调用时 TS 自动校验参数类型和数量
emit('update', 1, { name: '张三', email: 'zhang@example.com' }) // ✅ 正确
// emit('update', '1', { name: 123 })                            // ❌ 类型错误
// emit('page-change')                                           // ❌ 缺少参数
</script>
```

## 模板 Ref 的类型标注

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import GenericSelect from './GenericSelect.vue'

// DOM 元素 ref —— 标注具体元素类型
const inputRef = ref<HTMLInputElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

// 组件实例 ref —— 用 InstanceType
const selectRef = ref<InstanceType<typeof GenericSelect> | null>(null)

onMounted(() => {
  inputRef.value?.focus()           // TS 知道这是 HTMLInputElement
  canvasRef.value?.getContext('2d') // TS 知道这是 HTMLCanvasElement
})
</script>

<template>
  <input ref="inputRef" />
  <canvas ref="canvasRef" />
  <GenericSelect ref="selectRef" />
</template>
```

## 小结

TypeScript 在 Vue 3 中的价值取决于你用多深。引入泛型组件消除 `any`、用可辨识联合消除 `null` 检查、用 `InjectionKey` 保证依赖注入的类型安全——这些模式一旦内化，类型系统就不是负担，而是你写代码时最可靠的助手。
