<template>
  <teleport to="body">
    <transition name="confirm-fade">
      <div v-if="open" class="confirm" @click.self="cancel">
        <div
          class="confirm__card"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="messageId"
        >
          <h2 :id="titleId" class="confirm__title">{{ title }}</h2>
          <p :id="messageId" class="confirm__message">{{ message }}</p>
          <div class="confirm__actions">
            <button ref="cancelButton" type="button" class="btn btn--secondary" @click="cancel">
              {{ cancelLabel }}
            </button>
            <button
              type="button"
              class="btn"
              :class="danger ? 'btn--danger' : 'btn--primary'"
              :disabled="busy"
              @click="$emit('confirm')"
            >
              {{ busy ? busyLabel : confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: '' },
  confirmLabel: { type: String, default: 'Confirm' },
  cancelLabel: { type: String, default: 'Cancel' },
  busyLabel: { type: String, default: 'Working...' },
  busy: { type: Boolean, default: false },
  danger: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])

const cancelButton = ref(null)
const titleId = `confirm-title-${Math.random().toString(36).slice(2, 9)}`
const messageId = `confirm-message-${Math.random().toString(36).slice(2, 9)}`

function onKeydown(event) {
  if (event.key === 'Escape' && props.open && !props.busy) {
    event.preventDefault()
    cancel()
  }
}

function cancel() {
  if (props.busy) return
  emit('cancel')
}

watch(
  () => props.open,
  async (value) => {
    if (value) {
      document.addEventListener('keydown', onKeydown)
      await nextTick()
      cancelButton.value?.focus()
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
)

onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.confirm {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  background: rgba(2, 6, 23, 0.62);
}
.confirm__card {
  width: min(440px, 100%);
  padding: 1.1rem 1.2rem;
  border-radius: 0.7rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-primary);
  box-shadow: 0 24px 60px rgba(2, 6, 23, 0.45);
}
.confirm__title {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
}
.confirm__message {
  margin: 0 0 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}
.confirm__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 120ms ease;
}
.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}
</style>
