<template>
  <teleport to="body">
    <transition name="tool-panel">
      <section
        v-if="isOpen && activeTool"
        class="tool-panel"
        :class="{ 'tool-panel--expanded': expanded }"
        role="region"
        :aria-label="`${activeTool.title} panel`"
      >
        <header class="tool-panel__head">
          <div class="tool-panel__identity">
            <p class="tool-panel__eyebrow">Tools</p>
            <h2 class="tool-panel__title">{{ activeTool.title }}</h2>
            <span class="tool-panel__badge">Sandboxed external tool</span>
            <p class="tool-panel__description">{{ activeTool.description }}</p>
          </div>
          <div class="tool-panel__actions">
            <button
              type="button"
              class="btn btn--secondary btn--sm"
              :aria-pressed="expanded"
              @click="expanded = !expanded"
            >
              {{ expanded ? 'Restore' : 'Expand' }}
            </button>
            <a
              :href="toolUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn--secondary btn--sm"
            >
              Open in new tab
            </a>
            <button
              ref="closeButton"
              type="button"
              class="tool-panel__close"
              :aria-label="`Close ${activeTool.title} panel`"
              @click="closeTool"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M18 6 6 18" />
                <path d="m6 6 12 12" />
              </svg>
            </button>
          </div>
        </header>

        <div class="tool-panel__body">
          <iframe
            v-show="!timedOut"
            ref="frame"
            :src="toolUrl"
            :title="activeTool.title"
            class="tool-panel__frame"
            :sandbox="toolSandbox"
            referrerpolicy="no-referrer"
            allow="clipboard-write"
            @load="onLoad"
          ></iframe>

          <div v-if="loading && !timedOut" class="tool-panel__state" aria-live="polite">
            <span class="tool-panel__spinner" aria-hidden="true"></span>
            <strong>Loading {{ activeTool.title }}…</strong>
            <p>The tool runs outside the platform. It cannot read your session.</p>
          </div>

          <div v-if="timedOut" class="tool-panel__state tool-panel__state--error" role="alert">
            <strong>{{ activeTool.title }} did not load in the panel.</strong>
            <p>
              The network or the tool's frame policy may have blocked it. Open it in a new
              tab instead; the exercise stays open here.
            </p>
            <a
              :href="toolUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn--primary btn--sm"
            >
              Open in new tab
            </a>
          </div>
        </div>

        <footer class="tool-panel__foot">
          <span>{{ activeTool.attribution }}</span>
          <span>Downloads and clipboard use the external tool, not the platform.</span>
        </footer>
      </section>
    </transition>
  </teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useToolPanel } from '../composables/useToolPanel'
import { safeHttpUrl } from '../utils/url'

const { activeTool, isOpen, closeTool } = useToolPanel()

const toolUrl = computed(() => safeHttpUrl(activeTool.value?.url))

// A same-origin tool is a reviewed, pinned build (CyberChef). A future
// cross-origin tool must not get allow-same-origin, which would cancel the
// sandbox for the app origin.
const toolSandbox = computed(() => {
  const url = toolUrl.value
  if (!url) return 'allow-scripts allow-forms'
  try {
    const sameOrigin = new URL(url, window.location.origin).origin === window.location.origin
    return sameOrigin
      ? 'allow-scripts allow-same-origin allow-forms allow-downloads allow-modals'
      : 'allow-scripts allow-forms allow-downloads allow-modals'
  } catch {
    return 'allow-scripts allow-forms'
  }
})

const frame = ref(null)
const closeButton = ref(null)
const loading = ref(true)
const timedOut = ref(false)
const expanded = ref(false)
let loadTimer = null
let returnFocus = null

function clearLoadTimer() {
  if (loadTimer) {
    window.clearTimeout(loadTimer)
    loadTimer = null
  }
}

function startLoadTimer() {
  clearLoadTimer()
  loadTimer = window.setTimeout(() => {
    if (loading.value) {
      timedOut.value = true
      loading.value = false
    }
  }, 12000)
}

function onLoad() {
  loading.value = false
  timedOut.value = false
  clearLoadTimer()
}

function onKeydown(event) {
  if (event.key === 'Escape' && isOpen.value) {
    closeTool()
  }
}

watch(isOpen, async (open) => {
  if (open) {
    returnFocus = document.activeElement
    loading.value = true
    timedOut.value = false
    expanded.value = false
    startLoadTimer()
    await nextTick()
    closeButton.value?.focus()
  } else {
    clearLoadTimer()
    loading.value = true
    timedOut.value = false
    if (returnFocus && typeof returnFocus.focus === 'function') {
      returnFocus.focus()
    }
    returnFocus = null
  }
})

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  clearLoadTimer()
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.tool-panel {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 280;
  display: flex;
  flex-direction: column;
  height: min(55vh, 620px);
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  box-shadow: 0 -18px 45px rgba(2, 6, 23, 0.35);
  transition: height 180ms ease;
}

.tool-panel--expanded {
  height: min(85vh, 980px);
}

.tool-panel__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.tool-panel__identity {
  min-width: 0;
}

.tool-panel__eyebrow {
  margin: 0 0 0.15rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.tool-panel__title {
  display: inline;
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 700;
}

.tool-panel__badge {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.1rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  font-size: 0.6rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  vertical-align: middle;
}

.tool-panel__description {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.tool-panel__actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex: 0 0 auto;
}

.tool-panel__close {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  cursor: pointer;
}

.tool-panel__close:hover {
  border-color: var(--accent);
  color: var(--accent-text);
}

.tool-panel__close:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.tool-panel__close svg {
  width: 16px;
  height: 16px;
}

.tool-panel__body {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  background: var(--bg-primary);
}

.tool-panel__frame {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}

.tool-panel__state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 1.5rem;
  background: var(--bg-primary);
  color: var(--text-secondary);
  text-align: center;
}

.tool-panel__state strong {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.tool-panel__state p {
  max-width: 42rem;
  margin: 0;
  font-size: 0.8rem;
}

.tool-panel__state--error {
  border-top: 1px solid var(--border-color);
}

.tool-panel__spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--bg-tertiary);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: tool-panel-spin 0.8s linear infinite;
}

@keyframes tool-panel-spin {
  to { transform: rotate(360deg); }
}

.tool-panel__foot {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.25rem 1rem;
  padding: 0.45rem 1rem calc(0.45rem + env(safe-area-inset-bottom));
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.65rem;
}

.tool-panel-enter-active,
.tool-panel-leave-active {
  transition: transform 180ms ease, opacity 180ms ease;
}

.tool-panel-enter-from,
.tool-panel-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (max-width: 768px) {
  .tool-panel {
    height: 85vh;
  }

  .tool-panel__head {
    flex-direction: column;
    gap: 0.5rem;
  }

  .tool-panel__actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .tool-panel__actions .btn {
    flex: 1 1 auto;
  }

  .tool-panel__foot {
    font-size: 0.6rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tool-panel,
  .tool-panel-enter-active,
  .tool-panel-leave-active {
    transition: none;
  }

  .tool-panel__spinner {
    animation: none;
  }
}
</style>
