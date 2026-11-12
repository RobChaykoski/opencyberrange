<template>
  <aside
    v-if="isMobile && !dismissed"
    class="mobile-notice"
    role="note"
    aria-label="Mobile screen notice"
  >
    <svg class="mobile-notice__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <rect x="7" y="2" width="10" height="20" rx="2" />
      <line x1="11" y1="18" x2="13" y2="18" />
    </svg>
    <div class="mobile-notice__copy">
      <strong>{{ title }}</strong>
      <p>{{ message }}</p>
    </div>
    <button
      type="button"
      class="mobile-notice__close"
      :aria-label="`Dismiss notice: ${title}`"
      @click="dismiss"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M18 6 6 18M6 6l12 12" />
      </svg>
    </button>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useMobileView } from '../composables/useMobileView'

const props = defineProps({
  title: { type: String, default: 'Best on a larger screen' },
  message: {
    type: String,
    default: 'This workspace has controls and tables that are easier to use on a desktop. You can keep going here, but a laptop or desktop will be faster.',
  },
  storageKey: { type: String, default: 'ocr.mobile-notice' },
})

const { isMobile } = useMobileView()
const dismissed = ref(sessionStorage.getItem(props.storageKey) === '1')

function dismiss() {
  dismissed.value = true
  try {
    sessionStorage.setItem(props.storageKey, '1')
  } catch {
    // Private mode: the notice reappears next visit, which is acceptable.
  }
}
</script>

<style scoped>
.mobile-notice {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  margin: 0.75rem 0;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.mobile-notice__icon {
  flex: 0 0 auto;
  width: 22px;
  height: 22px;
  margin-top: 0.1rem;
  color: var(--accent-text);
}

.mobile-notice__copy {
  min-width: 0;
  flex: 1 1 auto;
}

.mobile-notice__copy strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.mobile-notice__copy p {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  line-height: 1.45;
}

.mobile-notice__close {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
}

.mobile-notice__close:hover {
  border-color: var(--accent);
  color: var(--accent-text);
}

.mobile-notice__close:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.mobile-notice__close svg {
  width: 14px;
  height: 14px;
}
</style>
