<template>
  <div class="about-page">
    <div v-if="loading" class="about-state" role="status" aria-live="polite">
      Loading installation details...
    </div>
    <div v-else-if="error" class="about-state about-state--error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="load">Try again</button>
    </div>

    <template v-else-if="about">
      <header class="about-hero">
        <img src="/swocts-cyber-range-mark.png" alt="" class="about-hero__mark" />
        <div class="about-hero__copy">
          <p class="about-hero__eyebrow">About this installation</p>
          <h1>{{ about.platform.name }}</h1>
          <p class="about-hero__release">{{ about.release }}</p>
          <p class="about-hero__note">
            Powered by OpenCyberRange. Source-available under the PolyForm
            Noncommercial License 1.0.0.
          </p>
        </div>
      </header>

      <section class="about-summary" aria-label="Platform summary">
        <article class="about-summary__item">
          <span class="about-summary__label">Platform</span>
          <strong class="about-summary__value">{{ about.platform.version }}</strong>
          <span class="about-summary__detail">{{ about.platform.edition }}</span>
        </article>
        <article class="about-summary__item">
          <span class="about-summary__label">Runtime</span>
          <strong class="about-summary__value">Python {{ about.platform.python }}</strong>
          <span class="about-summary__detail">Node {{ about.platform.node }}</span>
        </article>
        <article class="about-summary__item">
          <span class="about-summary__label">Data</span>
          <strong class="about-summary__value">PostgreSQL {{ about.platform.postgres }}</strong>
          <span class="about-summary__detail">Redis {{ about.platform.redis }}</span>
        </article>
        <article class="about-summary__item">
          <span class="about-summary__label">Inventory</span>
          <strong class="about-summary__value">{{ componentCount }} components</strong>
          <span class="about-summary__detail">{{ about.sbom.length }} SBOM files</span>
        </article>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Branding and licence</h2>
        <p class="about-text">
          The <strong>SWOCTS</strong> name and logo are owned by SWOCTS. The logo
          was created and designed by <strong>Avery Chaykoski</strong>. They are
          brand assets, not software, and are not licensed under the PolyForm
          software licence.
        </p>
        <p class="about-text">
          The platform and original content are licensed under the
          <strong>PolyForm Noncommercial License 1.0.0</strong>. Third-party
          software and data keep their own licences; the upstream
          <strong>OpenCyberRange</strong> attribution and notices remain in force.
        </p>

        <h3 class="about-subtitle">Licence documents</h3>
        <div class="about-link-grid">
          <button
            v-for="doc in about.licences"
            :key="doc.file"
            type="button"
            class="about-link"
            aria-haspopup="dialog"
            :disabled="licenceLoading === doc.file"
            @click="viewLicence(doc)"
          >
            <span class="about-link__label">
              {{ licenceLoading === doc.file ? 'Loading…' : doc.label }}
            </span>
            <span class="about-link__file">{{ doc.file }}</span>
          </button>
        </div>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Components</h2>
        <p class="about-text">
          Direct runtime components, container images, and lab toolchains. The
          full transitive inventory is in the CycloneDX SBOM downloads below.
        </p>

        <details v-for="group in groups" :key="group.key" class="about-group">
          <summary>
            <span>{{ group.label }}</span>
            <span class="about-group__count">{{ group.items.length }}</span>
          </summary>
          <div v-if="group.items.length" class="table-container about-table">
            <table class="data-table data-table--compact">
              <caption class="sr-only">{{ group.label }} components</caption>
              <thead>
                <tr>
                  <th scope="col">Component</th>
                  <th scope="col">Version</th>
                  <th scope="col">Licence</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in group.items" :key="`${group.key}-${item.name}`">
                  <td>{{ item.name }}</td>
                  <td class="cell-mono">{{ item.version || '—' }}</td>
                  <td>{{ item.licence }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="about-empty">No components recorded in this group.</p>
        </details>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Software bill of materials</h2>
        <p class="about-text">
          CycloneDX SBOMs generated for this release. Each download includes a
          SHA-256 checksum so you can verify the file you received.
        </p>
        <ul v-if="about.sbom.length" class="about-sbom-list">
          <li v-for="file in about.sbom" :key="file.name" class="about-sbom">
            <div class="about-sbom__meta">
              <strong>{{ file.label }}</strong>
              <span class="cell-muted">{{ file.name }} · {{ formatBytes(file.bytes) }}</span>
              <code class="about-sbom__hash" :title="file.sha256">
                sha256:{{ file.sha256.slice(0, 16) }}…
              </code>
            </div>
            <button
              type="button"
              class="btn btn--secondary btn--sm"
              :disabled="sbomLoading === file.name"
              :aria-label="`Download ${file.label}`"
              @click="downloadSbom(file)"
            >
              {{ sbomLoading === file.name ? 'Downloading…' : 'Download' }}
            </button>
          </li>
        </ul>
        <p v-else class="about-empty">No SBOM files are available for this build.</p>
      </section>

      <div
        v-if="licenceModal.open"
        class="about-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="about-modal-title"
        @click.self="closeLicence"
        @keydown.esc="closeLicence"
        @keydown="trapFocus"
      >
        <div ref="modalCard" class="about-modal__card">
          <div class="about-modal__header">
            <h2 id="about-modal-title">{{ licenceModal.title }}</h2>
            <button
              ref="closeButton"
              type="button"
              class="btn btn--secondary btn--sm"
              @click="closeLicence"
            >
              Close
            </button>
          </div>
          <pre ref="modalBody" class="about-modal__body" tabindex="0">{{ licenceModal.text }}</pre>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import api from '../api/axios'

const about = ref(null)
const loading = ref(true)
const error = ref('')
const licenceModal = ref({ open: false, title: '', text: '' })
const licenceLoading = ref('')
const sbomLoading = ref('')
const licenceTrigger = ref(null)
const modalCard = ref(null)
const closeButton = ref(null)
const modalBody = ref(null)

const groups = computed(() => {
  const components = about.value?.components || {}
  return [
    { key: 'backend', label: 'Backend runtime', items: components.backend || [] },
    { key: 'frontend', label: 'Frontend runtime', items: components.frontend || [] },
    { key: 'images', label: 'Container images', items: components.images || [] },
    { key: 'lab', label: 'Lab toolchains', items: components.lab_toolchains || [] },
  ]
})

const componentCount = computed(() =>
  groups.value.reduce((total, group) => total + group.items.length, 0)
)

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/about')
    about.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the About inventory.'
  } finally {
    loading.value = false
  }
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const fetchBlob = async (kind, name, type) => {
  const response = await api.get(`/about/${kind}/${encodeURIComponent(name)}`, { responseType: type })
  return response.data
}

const viewLicence = async (doc) => {
  licenceTrigger.value = document.activeElement
  licenceLoading.value = doc.file
  try {
    const text = await fetchBlob('licences', doc.file, 'text')
    licenceModal.value = { open: true, title: doc.label, text }
    await nextTick()
    closeButton.value?.focus()
  } catch {
    error.value = 'Could not load that licence document.'
  } finally {
    licenceLoading.value = ''
  }
}

const closeLicence = () => {
  licenceModal.value = { open: false, title: '', text: '' }
  nextTick(() => licenceTrigger.value?.focus())
}

const trapFocus = (event) => {
  if (event.key !== 'Tab') return
  const focusable = [closeButton.value, modalBody.value].filter(Boolean)
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

const downloadSbom = async (file) => {
  sbomLoading.value = file.name
  try {
    const blob = await fetchBlob('sbom', file.name, 'blob')
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = file.name
    anchor.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = 'Could not download that SBOM.'
  } finally {
    sbomLoading.value = ''
  }
}

onMounted(load)
</script>

<style scoped>
.about-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 1rem;
}

.about-state {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.about-state--error {
  color: var(--danger);
}

.about-hero {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.about-hero__mark {
  width: 64px;
  height: 64px;
  object-fit: contain;
  flex: 0 0 auto;
}

.about-hero__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.about-hero h1 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.2;
  color: var(--text-primary);
}

.about-hero__release {
  margin: 0.35rem 0 0;
  font-weight: 600;
  color: var(--text-secondary);
}

.about-hero__note {
  margin: 0.5rem 0 0;
  max-width: 68ch;
  color: var(--text-secondary);
}

.about-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.about-summary__item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
  min-width: 0;
}

.about-summary__label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.about-summary__value {
  font-size: 1.05rem;
  color: var(--text-primary);
}

.about-summary__detail {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.about-panel {
  margin-bottom: 1rem;
  padding: 1.25rem 1.5rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.about-panel .panel-title {
  margin: 0 0 0.75rem;
  font-size: 1.15rem;
  line-height: 1.3;
  color: var(--text-primary);
}

.about-text {
  margin: 0.5rem 0 1rem;
  max-width: 80ch;
  line-height: 1.6;
  color: var(--text-secondary);
}

.about-text strong {
  color: var(--text-primary);
  font-weight: 600;
}

.about-subtitle {
  margin: 1.25rem 0 0.65rem;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.about-link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.65rem;
}

.about-link {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  text-align: left;
  cursor: pointer;
  transition: border-color 150ms ease, background 150ms ease;
}

.about-link:hover:not(:disabled) {
  border-color: var(--accent);
  background: var(--bg-secondary);
}

.about-link:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.about-link:disabled {
  cursor: progress;
  opacity: 0.75;
}

.about-link__label {
  font-weight: 600;
}

.about-link__file {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.72rem;
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.about-group {
  border-top: 1px solid var(--border-color);
  padding: 0.6rem 0;
}

.about-group summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.35rem 0;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-primary);
}

.about-group summary:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.about-group__count {
  min-width: 2rem;
  padding: 0.1rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.72rem;
  text-align: center;
}

.about-table {
  margin-top: 0.5rem;
  overflow-x: auto;
}

.about-table :deep(th) {
  color: var(--text-muted);
  font-weight: 600;
}

.about-table :deep(td) {
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}

.about-empty {
  margin: 0.5rem 0;
  color: var(--text-muted);
}

.about-sbom-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.about-sbom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.about-sbom__meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.about-sbom__hash {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.72rem;
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.about-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(2, 6, 23, 0.6);
}

.about-modal__card {
  width: min(900px, 100%);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--panel-bg);
  overflow: hidden;
}

.about-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.about-modal__header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.about-modal__body {
  margin: 0;
  padding: 1rem;
  overflow: auto;
  white-space: pre-wrap;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.55;
}

.about-modal__body:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 900px) {
  .about-page {
    max-width: 100%;
  }
}

@media (max-width: 640px) {
  .about-page {
    padding: 1rem;
  }

  .about-panel {
    padding: 1rem;
  }

  .about-hero {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }

  .about-summary {
    grid-template-columns: 1fr;
  }

  .about-sbom {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
