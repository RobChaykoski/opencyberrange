<template>
  <Teleport to="body">
    <Transition name="pa-fade">
      <div
        v-if="show"
        class="pa-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pa-title"
        aria-describedby="pa-intro"
      >
        <div class="pa-card">
          <p class="pa-eyebrow">Before you begin</p>
          <h2 id="pa-title">Your privacy choices</h2>
          <p id="pa-intro" class="pa-intro">
            The Cyber Range only needs the information that runs your account and
            learning record. Everything else is your choice.
          </p>

          <ul class="pa-list">
            <li>
              <strong>Optional learning profiles are off.</strong> Cyber DNA, Cyber
              GPS, the professional portfolio, AI coaching, and research stay off
              until you enable them.
            </li>
            <li>
              <strong>Public visibility is off.</strong> Scoreboards and public
              certificate verification are private unless you choose to appear.
            </li>
            <li>
              <strong>You are in control.</strong> You can change or withdraw each
              choice, download your data, or delete your account from
              Profile → Security &amp; privacy.
            </li>
            <li>
              <strong>No advertising.</strong> We do not sell your information or
              use third-party behavioural advertising.
            </li>
          </ul>

          <p class="pa-links">
            <router-link to="/privacy/youth" target="_blank" rel="noopener noreferrer">
              Youth privacy summary
            </router-link>
            <span aria-hidden="true"> · </span>
            <router-link to="/privacy" target="_blank" rel="noopener noreferrer">
              Full Privacy notice
            </router-link>
          </p>

          <div class="pa-actions">
            <button type="button" class="btn btn--secondary" :disabled="saving" @click="$emit('decline')">
              Sign out
            </button>
            <button
              ref="ackButton"
              type="button"
              class="btn btn--primary"
              :disabled="saving"
              @click="$emit('acknowledge')"
            >
              {{ saving ? 'Saving...' : 'I understand' }}
            </button>
          </div>
          <p v-if="error" class="pa-error" role="alert">{{ error }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

defineEmits(['acknowledge', 'decline'])

const ackButton = ref(null)

const onKeydown = (event) => {
  if (event.key === 'Escape') {
    // Acknowledgement is required; Escape must not dismiss the dialog.
    event.preventDefault()
  }
}

watch(
  () => props.show,
  async (visible) => {
    if (typeof document !== 'undefined') {
      document.body.style.overflow = visible ? 'hidden' : ''
    }
    if (visible) {
      await nextTick()
      ackButton.value?.focus()
    }
  }
)

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', onKeydown)
}

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', onKeydown)
  }
  if (typeof document !== 'undefined') document.body.style.overflow = ''
})
</script>

<style scoped>
.pa-overlay {
  position: fixed;
  inset: 0;
  z-index: 3100;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  background: rgba(2, 6, 23, 0.78);
  -webkit-backdrop-filter: blur(6px);
  backdrop-filter: blur(6px);
}

.pa-card {
  width: min(580px, 100%);
  max-height: calc(100vh - 2.5rem);
  overflow-y: auto;
  padding: 1.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
}

.pa-eyebrow {
  margin: 0 0 0.25rem;
  color: var(--accent);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.pa-card h2 {
  margin: 0;
  color: var(--text-primary);
}

.pa-intro {
  margin: 0.6rem 0 1rem;
  color: var(--text-secondary);
  line-height: 1.55;
}

.pa-list {
  margin: 0;
  padding-left: 1.15rem;
  display: grid;
  gap: 0.65rem;
  color: var(--text-secondary);
  line-height: 1.5;
  font-size: 0.9rem;
}

.pa-list strong {
  color: var(--text-primary);
}

.pa-links {
  margin: 1rem 0 0;
  font-size: 0.85rem;
}

.pa-links a {
  color: var(--accent);
}

.pa-actions {
  margin-top: 1.1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.6rem;
}

.pa-error {
  margin: 0.75rem 0 0;
  color: var(--danger);
  font-size: 0.85rem;
}

.pa-fade-enter-active,
.pa-fade-leave-active {
  transition: opacity 0.18s ease;
}

.pa-fade-enter-from,
.pa-fade-leave-to {
  opacity: 0;
}
</style>
