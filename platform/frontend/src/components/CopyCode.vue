<template>
  <button
    type="button"
    class="copy-code"
    :title="copied ? 'Copied' : `Copy ${label}`"
    :aria-label="copied ? `${label} copied` : `Copy ${label}`"
    @click="copy"
  >
    <code class="copy-code__value">{{ value }}</code>
    <svg class="copy-code__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
         stroke-width="2" aria-hidden="true">
      <rect x="9" y="9" width="11" height="11" rx="2" />
      <path d="M5 15V5a2 2 0 0 1 2-2h8" />
    </svg>
    <span class="copy-code__status" aria-live="polite">{{ copied ? 'Copied' : '' }}</span>
  </button>
</template>

<script setup>
import { onBeforeUnmount, ref } from 'vue'

const props = defineProps({
  value: { type: String, required: true },
  label: { type: String, default: 'value' },
})

const copied = ref(false)
let timer = null

const fallbackCopy = (text) => {
  const area = document.createElement('textarea')
  area.value = text
  area.setAttribute('readonly', '')
  area.style.position = 'fixed'
  area.style.opacity = '0'
  document.body.appendChild(area)
  area.select()
  document.execCommand('copy')
  area.remove()
}

const copy = async () => {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(props.value)
    } else {
      fallbackCopy(props.value)
    }
    copied.value = true
    clearTimeout(timer)
    timer = setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    copied.value = false
  }
}

onBeforeUnmount(() => clearTimeout(timer))
</script>

<style scoped>
.copy-code {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.125rem 0.375rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.copy-code:hover {
  border-color: var(--accent);
}

.copy-code:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.copy-code__value {
  font-family: var(--font-mono, ui-monospace, SFMono-Regular, Menlo, monospace);
  font-size: 0.8125rem;
}

.copy-code__icon {
  width: 14px;
  height: 14px;
  color: var(--text-muted);
}

.copy-code__status {
  font-size: 0.75rem;
  color: var(--success);
  min-width: 3.25rem;
  text-align: left;
}
</style>
