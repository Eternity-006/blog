import { ref } from 'vue'

export interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

const toasts = ref<ToastItem[]>([])
let nextId = 0

export function useToast() {
  function add(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const id = nextId++
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  function success(msg: string) { add(msg, 'success') }
  function error(msg: string) { add(msg, 'error') }
  function info(msg: string) { add(msg, 'info') }

  return { toasts, success, error, info }
}
