<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts } = useToast()
</script>

<template>
  <div class="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="[
          'pointer-events-auto px-4 py-2.5 rounded-lg text-sm shadow-lg max-w-xs animate-slide-in',
          t.type === 'success' ? 'bg-emerald-600 text-white' :
          t.type === 'error' ? 'bg-red-600 text-white' :
          'bg-gray-800 text-white dark:bg-gray-200 dark:text-gray-900',
        ]"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.toast-enter-active { animation: slideIn 0.3s ease-out; }
.toast-leave-active { animation: slideIn 0.2s ease-in reverse; }
</style>
