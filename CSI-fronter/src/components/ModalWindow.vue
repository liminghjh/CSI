<template>
  <transition name="modal">
    <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
      <section class="modal-shell" :class="sizeClass">
        <header class="modal-header">
          <div>
            <p v-if="eyebrow" class="modal-eyebrow">{{ eyebrow }}</p>
            <h3>{{ title }}</h3>
          </div>
          <button class="modal-close" type="button" data-tooltip="关闭" @click="$emit('close')">&times;</button>
        </header>
        <div class="modal-body">
          <slot />
        </div>
      </section>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    eyebrow?: string
    size?: 'medium' | 'large'
  }>(),
  { eyebrow: '', size: 'medium' },
)

defineEmits<{ close: [] }>()

const sizeClass = computed(() => `modal-shell--${props.size}`)
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(6px);
}

.modal-shell {
  width: min(100%, 600px);
  max-height: min(85vh, 800px);
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
}

.modal-shell--large {
  width: min(100%, 860px);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f3f4f6;
  flex-shrink: 0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
  color: #111827;
}

.modal-eyebrow {
  margin: 0 0 4px;
  color: #7c3aed;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #9ca3af;
  font-size: 1.25rem;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-close::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 10px;
  border-radius: 4px;
  background: #1f2937;
  color: #fff;
  font-size: 0.7rem;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s;
}

.modal-close:hover::after {
  opacity: 1;
}

.modal-body {
  padding: 20px 24px 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .modal-shell,
.modal-leave-to .modal-shell {
  transform: scale(0.96);
}
</style>
