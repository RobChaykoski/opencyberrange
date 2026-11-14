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
          <span class="about-summary__detail">Valkey {{ about.platform.valkey || about.platform.redis }}</span>
        </article>
        <article class="about-summary__item">
          <span class="about-summary__label">Inventory</span>
          <strong class="about-summary__value">{{ componentCount }} components</strong>
          <span class="about-summary__detail">{{ about.sbom.length }} SBOM files</span>
        </article>
      </section>

      <section class="panel about-panel">
        <div class="about-panel__header">
          <div>
            <h2 class="panel-title">Build and runtime</h2>
            <p class="about-text about-text--tight">
              Build facts come from the release; runtime values are read from
              this installation.
            </p>
          </div>
          <button type="button" class="btn btn--secondary btn--sm" @click="copyDiagnostics">
            {{ copyLabel }}
          </button>
        </div>

        <dl class="about-facts">
          <div class="about-fact">
            <dt>Release</dt>
            <dd>{{ about.platform.version }}</dd>
          </div>
          <div class="about-fact">
            <dt>Commit</dt>
            <dd class="cell-mono">{{ about.build?.git_sha || 'unknown' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Inventory built</dt>
            <dd>{{ formatTimestamp(about.build?.built_at) }}</dd>
          </div>
          <div class="about-fact">
            <dt>Schema revision</dt>
            <dd class="cell-mono">{{ about.runtime?.schema_revision || 'unknown' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Backend image</dt>
            <dd class="cell-mono" :title="about.build?.image_digests?.backend || 'unknown'">
              {{ shortDigest(about.build?.image_digests?.backend) }}
            </dd>
          </div>
          <div class="about-fact">
            <dt>Frontend image</dt>
            <dd class="cell-mono" :title="about.build?.image_digests?.frontend || 'unknown'">
              {{ shortDigest(about.build?.image_digests?.frontend) }}
            </dd>
          </div>
          <div class="about-fact">
            <dt>Python / Node</dt>
            <dd>{{ about.runtime?.python || '—' }} / {{ about.runtime?.node || '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>PostgreSQL / Valkey</dt>
            <dd>{{ about.runtime?.postgres || '-' }} / {{ about.runtime?.valkey || about.runtime?.redis || '-' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Edition</dt>
            <dd>{{ about.runtime?.edition || about.platform.edition }}</dd>
          </div>
          <div class="about-fact">
            <dt>Runtime checked</dt>
            <dd>{{ formatTimestamp(about.runtime?.checked_at) }}</dd>
          </div>
        </dl>
        <p class="about-copy-status" role="status" aria-live="polite">{{ copyStatus }}</p>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Platform maintenance</h2>
        <p class="about-copy">
          Versions of the host and runtime that operate the platform — not the tools
          inside lab containers. Status reflects the supported baseline and next
          upgrade target; follow the referenced document before changing a component.
        </p>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th scope="col">Component</th>
                <th scope="col">Running</th>
                <th scope="col">Supported / target</th>
                <th scope="col">Status</th>
                <th scope="col">Upgrade path</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in about.platform_health || []" :key="item.key">
                <td class="cell-primary">{{ item.name }}<div class="cell-muted">{{ item.note }}</div></td>
                <td class="cell-mono">{{ item.current }}</td>
                <td>{{ item.target }}</td>
                <td>
                  <span :class="['about-health', `about-health--${item.status}`]">
                    {{ statusLabel(item.status) }}
                  </span>
                </td>
                <td class="cell-mono">{{ item.path }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="about-maintenance">
          <h3>Upgrade and rollback</h3>
          <p>
            Take a verified backup first. Production upgrades are image rebuilds plus
            an Alembic upgrade; rollback restores the retained previous image tags and
            the pre-deploy database dump.
          </p>
          <pre class="about-command">{{ about.upgrade?.upgrade_command }}</pre>
          <p class="cell-muted">
            Rollback: {{ about.upgrade?.rollback }} See
            <code>{{ about.upgrade?.readiness }}</code>.
          </p>
          <p class="cell-muted">
            Operations: <code>{{ about.upgrade?.backup }}</code> ·
            <code>{{ about.upgrade?.check }}</code> ·
            <code>{{ about.upgrade?.runbook }}</code>
          </p>
        </div>
      </section>

      <section class="panel about-panel">
        <h2 class="panel-title">Content and integrity</h2>
        <dl class="about-facts about-facts--compact">
          <div class="about-fact">
            <dt>Labs</dt>
            <dd>{{ about.content?.labs ?? '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Tracks</dt>
            <dd>{{ about.content?.tracks ?? '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Levels</dt>
            <dd>{{ about.content?.levels ?? '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Change ledger</dt>
            <dd>
              <span class="about-integrity" :class="`about-integrity--${integrityStatus}`">
                {{ integrityLabel }}
              </span>
            </dd>
          </div>
          <div class="about-fact">
            <dt>Ledger entries</dt>
            <dd>{{ about.integrity?.entries ?? '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Unattributed, 7 days</dt>
            <dd>{{ about.integrity?.unattributed_7d ?? '—' }}</dd>
          </div>
          <div class="about-fact">
            <dt>Unreviewed, 7 days</dt>
            <dd>{{ about.integrity?.unreviewed_7d ?? '—' }}</dd>
          </div>
        </dl>
        <p class="about-text about-text--tight">
          Operators review unattributed writes in
          <strong>Admin → System → Integrity</strong>; each review records the
          reviewer, decision, and note in the audit log and ledger. Full chain,
          checksum, and data-quality checks run from the host schedule.
        </p>
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

        <h3 class="about-subtitle">Project documents</h3>
        <div class="about-link-grid">
          <button
            v-for="doc in projectLicences"
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

        <details class="about-group about-licence-group">
          <summary>
            <span>Third-party licence texts</span>
            <span class="about-group__count">{{ thirdPartyLicences.length }}</span>
          </summary>
          <div class="about-link-grid about-link-grid--nested">
            <button
              v-for="doc in thirdPartyLicences"
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
        </details>
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

const copyState = ref('')
const copyStatus = ref('')

const copyLabel = computed(() =>
  copyState.value === 'copied' ? 'Copied' : 'Copy diagnostics'
)

const integrityStatus = computed(() => about.value?.integrity?.status || 'unknown')

const integrityLabel = computed(() => {
  const labels = {
    ok: 'Active, no unattributed writes',
    warning: 'Active, review unattributed writes',
    error: 'Not installed',
    unavailable: 'Not available',
    unknown: 'Unknown',
  }
  return labels[integrityStatus.value] || 'Unknown'
})

const diagnostics = computed(() => ({
  release: about.value?.version,
  platform: about.value?.platform,
  build: about.value?.build,
  runtime: about.value?.runtime,
  content: about.value?.content,
  integrity: about.value?.integrity,
  client: { user_agent: navigator.userAgent },
}))

const copyDiagnostics = async () => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(diagnostics.value, null, 2))
    copyState.value = 'copied'
    copyStatus.value = 'Diagnostics copied to the clipboard.'
  } catch {
    copyState.value = 'error'
    copyStatus.value = 'Could not copy diagnostics. Copy the build facts manually.'
  }
  window.setTimeout(() => {
    copyState.value = ''
    copyStatus.value = ''
  }, 3000)
}

const shortDigest = (value) => {
  if (!value) return 'unknown'
  const text = String(value)
  return text.length > 19 ? `${text.slice(0, 19)}…` : text
}

const formatTimestamp = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

const statusLabel = (status) =>
  ({
    current: 'Current',
    supported: 'Supported',
    'upgrade-planned': 'Upgrade planned',
    'upgrade-candidate': 'Upgrade candidate',
  })[status] || status

const PROJECT_LICENCE_FILES = new Set([
  'LICENSE',
  'NOTICE',
  'LICENSING.md',
  'BRANDING.md',
  'BUILD_NOTICE.md',
  'THIRD_PARTY_NOTICES.md',
])

const projectLicences = computed(() =>
  (about.value?.licences || []).filter((doc) => PROJECT_LICENCE_FILES.has(doc.file))
)

const thirdPartyLicences = computed(() =>
  (about.value?.licences || []).filter((doc) => !PROJECT_LICENCE_FILES.has(doc.file))
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
  color: var(--text-secondary);
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

.about-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.about-text--tight {
  margin: 0.25rem 0 1rem;
}

.about-facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.25rem 1.25rem;
  margin: 0.5rem 0 0;
}

.about-fact {
  min-width: 0;
  padding: 0.55rem 0;
  border-top: 1px solid var(--border-color);
}

.about-fact dt {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.about-fact dd {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  overflow-wrap: anywhere;
}

.about-facts--compact {
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
}

.about-integrity {
  font-weight: 600;
}

.about-integrity--ok { color: var(--success); }
.about-integrity--warning { color: var(--warning); }
.about-integrity--error { color: var(--danger); }
.about-integrity--unavailable,
.about-integrity--unknown { color: var(--text-muted); }

.about-copy-status {
  min-height: 1.2rem;
  margin: 0.75rem 0 0;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.about-health {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  font-size: 0.72rem;
  white-space: nowrap;
}
.about-health--current { color: var(--success); border-color: var(--success); }
.about-health--supported { color: var(--accent-text); border-color: var(--accent); }
.about-health--upgrade-planned,
.about-health--upgrade-candidate { color: var(--warning, #d97706); border-color: var(--warning, #d97706); }
.about-maintenance {
  margin-top: 1rem;
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
}
.about-maintenance h3 { margin: 0 0 0.4rem; font-size: 0.95rem; }
.about-command {
  margin: 0.6rem 0;
  padding: 0.6rem;
  background: var(--bg-primary);
  border-radius: 6px;
  font-size: 0.75rem;
  overflow-x: auto;
  white-space: pre-wrap;
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

.about-link-grid--nested {
  margin-top: 0.75rem;
}

.about-licence-group {
  margin-top: 1rem;
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
  color: var(--text-secondary);
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
  color: var(--text-secondary);
  font-weight: 600;
}

.about-table :deep(td) {
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}

.about-empty {
  margin: 0.5rem 0;
  color: var(--text-secondary);
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
  color: var(--text-secondary);
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
