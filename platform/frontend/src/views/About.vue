<template>
  <div class="about-page">
    <div v-if="loading" class="about-state" role="status" aria-live="polite">Loading installation details...</div>
    <div v-else-if="error" class="about-state about-state--error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="load">Try again</button>
    </div>

    <template v-else-if="about">
      <header class="about-hero">
        <img src="/swocts-cyber-range-mark.png" alt="" class="about-hero__mark" />
        <div class="about-hero__copy">
          <p class="about-hero__kicker">About</p>
          <h1>SWOCTS Cyber Range</h1>
          <p class="about-hero__release">{{ about.release }}</p>
          <p class="about-hero__note">
            Powered by OpenCyberRange. Source-available under the PolyForm
            Noncommercial License 1.0.0.
          </p>
        </div>
      </header>

      <section class="about-grid" aria-label="Platform summary">
        <article class="about-card">
          <span class="about-card__label">Platform</span>
          <strong class="about-card__value">{{ about.platform.version }}</strong>
          <span class="about-card__detail">{{ about.platform.edition }}</span>
        </article>
        <article class="about-card">
          <span class="about-card__label">Runtime</span>
          <strong class="about-card__value">Python {{ about.platform.python }}</strong>
          <span class="about-card__detail">Node {{ about.platform.node }}</span>
        </article>
        <article class="about-card">
          <span class="about-card__label">Database</span>
          <strong class="about-card__value">PostgreSQL {{ about.platform.postgres }}</strong>
          <span class="about-card__detail">Redis {{ about.platform.redis }}</span>
        </article>
        <article class="about-card">
          <span class="about-card__label">Inventory</span>
          <strong class="about-card__value">{{ componentCount }} components</strong>
          <span class="about-card__detail">{{ about.sbom.length }} SBOM files</span>
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
            @click="viewLicence(doc)"
          >
            <span class="about-link__label">{{ doc.label }}</span>
            <span class="about-link__file">{{ doc.file }}</span>
          </button>
        </div>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Privacy controls</h2>
        <p class="about-text">
          {{ about.privacy.reveal }} {{ about.privacy.note }}
        </p>
        <div class="about-privacy-row">
          <span class="about-privacy-state" :class="{ 'about-privacy-state--on': privacyMode }">
            Privacy mode {{ privacyMode ? 'on' : 'off' }}
          </span>
          <button type="button" class="btn btn--secondary btn--sm" @click="togglePrivacy">
            {{ privacyMode ? 'Turn off' : 'Turn on' }}
          </button>
        </div>
        <p class="about-text">
          <strong>Masked fields:</strong> {{ about.privacy.masked_fields.join(', ') }}.
        </p>
        <p class="about-text"><strong>Applies to:</strong></p>
        <ul class="about-privacy-scope">
          <li v-for="item in about.privacy.scope" :key="item">{{ item }}</li>
        </ul>
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
          <div class="table-container">
            <table class="data-table data-table--compact">
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
        </details>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Software bill of materials</h2>
        <p class="about-text">
          CycloneDX SBOMs generated for this release. Each download includes a
          SHA-256 checksum so you can verify the file you received.
        </p>
        <ul class="about-sbom-list">
          <li v-for="file in about.sbom" :key="file.name" class="about-sbom">
            <div class="about-sbom__meta">
              <strong>{{ file.label }}</strong>
              <span class="cell-muted">{{ file.name }} · {{ formatBytes(file.bytes) }}</span>
              <code class="about-sbom__hash" :title="file.sha256">sha256:{{ file.sha256.slice(0, 16) }}…</code>
            </div>
            <button type="button" class="btn btn--secondary btn--sm" @click="downloadSbom(file)">
              Download
            </button>
          </li>
        </ul>
      </section>

      <div v-if="licenceModal.open" class="about-modal" role="dialog" aria-modal="true" :aria-label="licenceModal.title">
        <div class="about-modal__card">
          <div class="about-modal__header">
            <h2>{{ licenceModal.title }}</h2>
            <button type="button" class="btn btn--secondary btn--sm" @click="closeLicence">Close</button>
          </div>
          <pre class="about-modal__body">{{ licenceModal.text }}</pre>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api/axios'
import { usePrivacy } from '../composables/usePrivacy'

const about = ref(null)
const loading = ref(true)
const error = ref('')
const licenceModal = ref({ open: false, title: '', text: '' })
const { privacyMode, togglePrivacy } = usePrivacy()

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
  try {
    const text = await fetchBlob('licences', doc.file, 'text')
    licenceModal.value = { open: true, title: doc.label, text }
  } catch {
    error.value = 'Could not load that licence document.'
  }
}

const closeLicence = () => {
  licenceModal.value = { open: false, title: '', text: '' }
}

const downloadSbom = async (file) => {
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
  }
}

onMounted(load)
</script>

<style scoped>
.about-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 1.5rem;
}

.about-state {
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-muted, #64748b);
}

.about-state--error {
  color: var(--danger, #b91c1c);
}

.about-hero {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.75rem;
  margin-bottom: 1.25rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 1rem;
  background: var(--card-bg, #fff);
}

.about-hero__mark {
  width: 96px;
  height: 96px;
  object-fit: contain;
  flex: 0 0 auto;
}

.about-hero__kicker {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}

.about-hero h1 {
  margin: 0;
  font-size: 1.75rem;
  line-height: 1.2;
}

.about-hero__release {
  margin: 0.35rem 0 0;
  font-weight: 600;
}

.about-hero__note {
  margin: 0.5rem 0 0;
  color: var(--text-muted, #64748b);
  max-width: 60ch;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.85rem;
  margin-bottom: 1.25rem;
}

.about-card {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 1rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 0.85rem;
  background: var(--card-bg, #fff);
}

.about-card__label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted, #64748b);
}

.about-card__value {
  font-size: 1.15rem;
}

.about-card__detail {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
}

.about-panel {
  margin-bottom: 1.25rem;
}

.about-text {
  margin: 0.5rem 0 1rem;
  max-width: 80ch;
  line-height: 1.6;
}

.about-subtitle {
  margin: 1.25rem 0 0.65rem;
  font-size: 1rem;
}

.about-link-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.6rem;
}

.about-link {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 0.65rem;
  background: var(--surface-2, #f8fafc);
  text-align: left;
  cursor: pointer;
}

.about-link:hover {
  border-color: var(--primary, #8b5cf6);
}

.about-link__label {
  font-weight: 600;
}

.about-link__file {
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--text-muted, #64748b);
  overflow-wrap: anywhere;
}

.about-group {
  border-top: 1px solid var(--border, #e5e7eb);
  padding: 0.65rem 0;
}

.about-group summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  cursor: pointer;
  font-weight: 600;
  padding: 0.35rem 0;
}

.about-group__count {
  min-width: 2rem;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
  background: var(--surface-2, #f1f5f9);
  color: var(--text-muted, #64748b);
  font-size: 0.75rem;
  text-align: center;
}

.about-sbom-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.about-privacy-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin: 0.5rem 0 0.75rem;
}

.about-privacy-state {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: var(--surface-2, #f1f5f9);
  color: var(--text-muted, #64748b);
  font-size: 0.8rem;
  font-weight: 600;
}

.about-privacy-state--on {
  background: rgba(34, 197, 94, 0.14);
  color: var(--success, #15803d);
}

.about-privacy-scope {
  margin: 0.25rem 0 0.5rem;
  padding-left: 1.2rem;
  color: var(--text-muted, #64748b);
  line-height: 1.6;
}

.about-sbom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 0.65rem;
  background: var(--surface-2, #f8fafc);
}

.about-sbom__meta {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.about-sbom__hash {
  font-size: 0.72rem;
  color: var(--text-muted, #64748b);
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
  background: rgba(15, 23, 42, 0.55);
}

.about-modal__card {
  width: min(900px, 100%);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  border-radius: 0.85rem;
  background: var(--card-bg, #fff);
  overflow: hidden;
}

.about-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid var(--border, #e5e7eb);
}

.about-modal__header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.about-modal__body {
  margin: 0;
  padding: 1rem;
  overflow: auto;
  white-space: pre-wrap;
  font-size: 0.8rem;
  line-height: 1.5;
}

@media (max-width: 640px) {
  .about-page {
    padding: 1rem;
  }

  .about-hero {
    flex-direction: column;
    text-align: center;
  }

  .about-sbom {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
