<template>
  <div class="rangebox-home">
    <div class="rangebox-home__container">
      <header class="rangebox-home__hero">
        <div class="rangebox-home__mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
        </div>
        <div>
          <p class="rangebox-home__eyebrow">Browser workspace</p>
          <h1 class="rangebox-home__title">RangeBox</h1>
          <p class="rangebox-home__subtitle">
            A Kali, Ubuntu, or REMnux desktop in your browser. No VPN, installs, or local tools required.
          </p>
        </div>
      </header>

      <section class="rangebox-card" aria-labelledby="rangebox-card-title">
        <div class="rangebox-card__head">
          <div>
            <h2 id="rangebox-card-title" class="rangebox-card__title">Standalone desktop</h2>
            <p class="rangebox-card__description">
              Launch a desktop for practice, tool access, or checking connectivity.
            </p>
          </div>
          <span class="rangebox-badge" :class="statusBadgeClass">{{ statusLabel }}</span>
        </div>

        <div class="rangebox-status">
          <div class="rangebox-status__item">
            <span class="rangebox-status__label">Deployed</span>
            <span class="rangebox-status__value" :class="capacityClass">
              {{ capacity.running }} / {{ capacity.max }}
            </span>
          </div>
          <div v-if="status !== 'running'" class="rangebox-status__item rangebox-status__item--image">
            <span class="rangebox-status__label">Image</span>
            <div class="rangebox-image-toggle" role="group" aria-label="RangeBox image">
              <button
                v-for="option in imageOptions"
                :key="option.value"
                type="button"
                class="rangebox-image-toggle__btn"
                :class="{ 'rangebox-image-toggle__btn--active': image === option.value }"
                :aria-pressed="image === option.value"
                @click="image = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>

        <div class="rangebox-card__actions">
          <button
            type="button"
            class="btn btn--lg"
            :class="primaryButtonClass"
            :disabled="primaryDisabled"
            @click="onPrimaryAction"
          >
            <svg v-if="loading" class="btn-icon rangebox-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
            </svg>
            <svg v-else-if="status === 'running'" class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="6" y="6" width="12" height="12" rx="1" />
            </svg>
            <svg v-else class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
              <line x1="8" y1="21" x2="16" y2="21" />
              <line x1="12" y1="17" x2="12" y2="21" />
            </svg>
            {{ primaryButtonLabel }}
          </button>
          <p v-if="errorMessage" class="rangebox-error" role="alert">{{ errorMessage }}</p>
        </div>

        <p class="rangebox-card__note">
          This desktop is for standalone practice. To work on an exercise with its lab network
          and flag dock, open the exercise and choose RangeBox when it starts.
          <router-link to="/exercises">Browse exercises</router-link>
        </p>
      </section>

      <section v-if="showViewer && status === 'running'" class="rangebox-viewer" aria-label="RangeBox desktop">
        <RangeBox
          :standalone="true"
          :image-name="image"
          :status-data="statusData"
        />
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'
import RangeBox from '../components/RangeBox.vue'
import { usePoll } from '../composables/usePoll'

const imageOptions = [
  { value: 'kali', label: 'Kali' },
  { value: 'ubuntu', label: 'Ubuntu' },
  { value: 'remnux', label: 'REMnux' },
]

const status = ref('not_found')
const statusData = ref(null)
const loading = ref(false)
const showViewer = ref(false)
const boxReady = ref(false)
const image = ref('kali')
const capacity = ref({ running: 0, max: 0, available: true })
const errorMessage = ref('')

const fetchCapacity = async () => {
  try {
    const { data } = await axios.get('/rangebox/capacity')
    capacity.value = data
  } catch {
    // Capacity is informational; keep the last known values.
  }
}

const fetchStatus = async () => {
  try {
    const { data } = await axios.get('/rangebox/standalone/status')
    statusData.value = data || null
    const containerRunning = data?.status === 'running'
    boxReady.value = containerRunning && data?.ready !== false
    if (containerRunning && !boxReady.value) {
      // Docker reports "running" before Xvfb, x11vnc, and websockify are up.
      status.value = 'starting'
      showViewer.value = false
      return
    }
    status.value = data?.status || 'not_found'
    if (status.value === 'running') {
      showViewer.value = true
    }
  } catch {
    status.value = 'not_found'
    boxReady.value = false
  }
}

const launch = async () => {
  loading.value = true
  errorMessage.value = ''
  status.value = 'starting'
  try {
    await axios.post(`/rangebox/standalone/launch?image=${image.value}`)
    let attempts = 0
    const poll = setInterval(async () => {
      attempts += 1
      await fetchStatus()
      if (status.value === 'running' || attempts > 30) {
        clearInterval(poll)
        loading.value = false
        showViewer.value = status.value === 'running'
        if (status.value === 'running') {
          fetchCapacity()
        } else {
          errorMessage.value = 'RangeBox did not start in time. Try again or contact an administrator.'
        }
      }
    }, 2000)
  } catch (error) {
    console.error('Failed to launch RangeBox:', error)
    status.value = 'not_found'
    loading.value = false
    errorMessage.value = 'Could not launch RangeBox. The pool may be full; try again shortly.'
  }
}

const stop = async () => {
  loading.value = true
  errorMessage.value = ''
  status.value = 'stopping'
  showViewer.value = false
  try {
    await axios.delete('/rangebox/standalone/destroy')
    status.value = 'not_found'
    await fetchCapacity()
  } catch (error) {
    console.error('Failed to stop RangeBox:', error)
    errorMessage.value = 'Could not stop RangeBox. Refresh the status and try again.'
    await fetchStatus()
  } finally {
    loading.value = false
  }
}

const onPrimaryAction = () => {
  if (status.value === 'running') {
    stop()
  } else {
    launch()
  }
}

const statusLabel = computed(() => {
  switch (status.value) {
    case 'running': return 'Running'
    case 'starting': return 'Starting'
    case 'stopping': return 'Stopping'
    default:
      return capacity.value.available ? 'Not running' : 'Unavailable'
  }
})

const statusBadgeClass = computed(() => {
  switch (status.value) {
    case 'running': return 'rangebox-badge--ready'
    case 'starting':
    case 'stopping': return 'rangebox-badge--pending'
    default:
      return capacity.value.available ? '' : 'rangebox-badge--danger'
  }
})

const capacityClass = computed(() => {
  const { running, max } = capacity.value
  if (running >= max) return 'rangebox-status__value--danger'
  if (running >= max * 0.8) return 'rangebox-status__value--pending'
  return 'rangebox-status__value--ready'
})

const primaryDisabled = computed(() =>
  loading.value
  || status.value === 'starting'
  || (!capacity.value.available && status.value !== 'running')
)

const primaryButtonClass = computed(() => {
  if (status.value === 'running') return 'btn--stop'
  return capacity.value.available ? 'btn--rangebox' : 'btn--disabled'
})

const primaryButtonLabel = computed(() => {
  if (loading.value) return status.value === 'running' ? 'Stopping...' : 'Starting...'
  if (status.value === 'starting') return 'Starting...'
  if (status.value === 'running') return 'Stop RangeBox'
  if (!capacity.value.available) return 'Unavailable'
  return 'Launch RangeBox'
})

usePoll(fetchCapacity, 15000)
usePoll(() => {
  if (status.value === 'starting') fetchStatus()
}, 3000)

onMounted(() => {
  fetchCapacity()
  fetchStatus()
})
</script>

<style scoped>
.rangebox-home {
  min-height: 100vh;
  background: var(--bg-primary);
  padding: 2rem;
}

.rangebox-home__container {
  max-width: 1000px;
  margin: 0 auto;
}

.rangebox-home__hero {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.rangebox-home__mark {
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.rangebox-home__mark svg {
  width: 34px;
  height: 34px;
}

.rangebox-home__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.rangebox-home__title {
  margin: 0 0 0.4rem;
  font-size: 2rem;
  line-height: 1.15;
  color: var(--text-primary);
}

.rangebox-home__subtitle {
  margin: 0;
  max-width: 62ch;
  color: var(--text-muted);
}

.rangebox-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.rangebox-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.rangebox-card__title {
  margin: 0 0 0.25rem;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.rangebox-card__description {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.rangebox-badge {
  flex-shrink: 0;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
}

.rangebox-badge--ready {
  color: var(--success);
  border-color: color-mix(in srgb, var(--success) 45%, transparent);
  background: color-mix(in srgb, var(--success) 12%, transparent);
}

.rangebox-badge--pending {
  color: var(--warning);
  border-color: color-mix(in srgb, var(--warning) 45%, transparent);
  background: color-mix(in srgb, var(--warning) 12%, transparent);
}

.rangebox-badge--danger {
  color: var(--danger);
  border-color: color-mix(in srgb, var(--danger) 45%, transparent);
  background: color-mix(in srgb, var(--danger) 12%, transparent);
}

.rangebox-status {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
}

.rangebox-status__item {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.rangebox-status__label {
  font-size: 0.72rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.rangebox-status__value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.rangebox-status__value--ready {
  color: var(--success);
}

.rangebox-status__value--pending {
  color: var(--warning);
}

.rangebox-status__value--danger {
  color: var(--danger);
}

.rangebox-image-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.rangebox-image-toggle__btn {
  padding: 0.3rem 0.75rem;
  border: none;
  background: var(--bg-primary);
  color: var(--text-muted);
  font: inherit;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.rangebox-image-toggle__btn:not(:last-child) {
  border-right: 1px solid var(--border-color);
}

.rangebox-image-toggle__btn:hover:not(.rangebox-image-toggle__btn--active) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.rangebox-image-toggle__btn--active {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.rangebox-card__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.btn--lg {
  padding: 0.9rem 1.6rem;
  font-size: 0.95rem;
}

.btn--rangebox {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: #fff;
}

.btn--rangebox:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-1px);
}

.btn--stop {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: #fff;
}

.btn--stop:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-1px);
}

.btn--disabled {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  cursor: not-allowed;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.rangebox-spinner {
  animation: rangebox-spin 1s linear infinite;
}

@keyframes rangebox-spin {
  to { transform: rotate(360deg); }
}

.rangebox-error {
  margin: 0;
  color: var(--danger);
  font-size: 0.875rem;
}

.rangebox-card__note {
  margin: 0;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.55;
}

.rangebox-card__note a {
  color: var(--accent);
}

.rangebox-viewer {
  margin-top: 1.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
}

@media (max-width: 720px) {
  .rangebox-home {
    padding: 1rem;
  }

  .rangebox-home__hero {
    align-items: flex-start;
  }

  .rangebox-home__mark {
    width: 52px;
    height: 52px;
  }

  .rangebox-home__mark svg {
    width: 26px;
    height: 26px;
  }

  .rangebox-home__title {
    font-size: 1.6rem;
  }

  .rangebox-card__head {
    flex-direction: column;
  }

  .rangebox-status {
    gap: 1.25rem;
  }
}
</style>
