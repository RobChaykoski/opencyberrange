<template>
  <details class="expandable" :open="open">
    <summary class="expandable__summary">
      <span class="expandable__caret" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6" />
        </svg>
      </span>
      <span class="expandable__title">{{ title }}</span>
      <span v-if="meta" class="expandable__meta">{{ meta }}</span>
    </summary>
    <div class="expandable__body">
      <slot />
    </div>
  </details>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  meta: { type: String, default: '' },
  open: { type: Boolean, default: false },
})
</script>

<style scoped>
.expandable {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  overflow: hidden;
}

.expandable__summary {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.7rem 0.85rem;
  cursor: pointer;
  list-style: none;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.9rem;
}

.expandable__summary::-webkit-details-marker {
  display: none;
}

.expandable__summary:hover {
  background: var(--hover-bg);
}

.expandable__summary:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.expandable__caret {
  display: grid;
  place-items: center;
  width: 18px;
  height: 18px;
  color: var(--accent-text);
  transition: transform 150ms ease;
}

.expandable__caret svg {
  width: 16px;
  height: 16px;
}

.expandable[open] .expandable__caret {
  transform: rotate(90deg);
}

.expandable__title {
  min-width: 0;
  flex: 1 1 auto;
}

.expandable__meta {
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.expandable__body {
  padding: 0 0.85rem 0.85rem;
}

@media (prefers-reduced-motion: reduce) {
  .expandable__caret {
    transition: none;
  }
}
</style>
