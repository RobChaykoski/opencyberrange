<template>
  <div class="governance-page">
    <header class="governance-page__head">
      <div>
        <p class="governance-page__eyebrow">Institution governance</p>
        <h1>Privacy and audit evidence</h1>
        <p>
          Aggregate evidence for the privacy office and auditors. This page does
          not expose learner-level records.
        </p>
      </div>
      <div class="governance-page__tabs" role="tablist" aria-label="Governance views">
        <button
          v-for="tab in availableTabs"
          :key="tab.id"
          type="button"
          role="tab"
          :aria-selected="activeTab === tab.id"
          :class="{ 'is-active': activeTab === tab.id }"
          @click="selectTab(tab.id)"
        >
          {{ tab.label }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="governance-page__empty" role="status">
      Loading governance evidence…
    </div>
    <div v-else-if="error" class="governance-page__empty governance-page__empty--error" role="alert">
      {{ error }}
    </div>
    <template v-else-if="data">
      <p class="governance-page__meta">
        Generated {{ formatDate(data.generated_at) }} · small-cell threshold
        {{ data.suppression_threshold }} · {{ data.scope }}
      </p>

      <section v-if="activeTab === 'privacy'" class="governance-grid">
        <article class="governance-card">
          <h2>Learners and safeguards</h2>
          <p><span>Learners</span><strong>{{ data.learners }}</strong></p>
          <p><span>Minors</span><strong>{{ data.minors }}</strong></p>
          <p><span>Courses</span><strong>{{ data.courses }}</strong></p>
          <p><span>Enrollments</span><strong>{{ data.enrollments }}</strong></p>
        </article>
        <article class="governance-card">
          <h2>Consent</h2>
          <p v-for="(counts, key) in data.consent" :key="key">
            <span>{{ key }}</span>
            <strong>{{ counts.granted }} granted / {{ counts.declined }} declined</strong>
          </p>
          <p v-if="!Object.keys(data.consent).length" class="muted">No consent records.</p>
        </article>
        <article class="governance-card">
          <h2>Retention and erasure</h2>
          <p><span>Erasure suppressions</span><strong>{{ data.erasure_suppressions }}</strong></p>
          <p><span>Retention runs</span><strong>{{ data.retention_runs }}</strong></p>
          <p v-if="data.latest_retention_run">
            <span>Last retention action</span>
            <strong>{{ data.latest_retention_run.action }}</strong>
          </p>
        </article>
        <article class="governance-card">
          <h2>Report access</h2>
          <p><span>Viewed</span><strong>{{ data.report_access.viewed }}</strong></p>
          <p><span>Exported</span><strong>{{ data.report_access.exported }}</strong></p>
          <p><span>Denied</span><strong>{{ data.report_access.denied }}</strong></p>
          <p><span>Library views</span><strong>{{ data.report_access.library_views }}</strong></p>
        </article>
        <article class="governance-card">
          <h2>Data inventory</h2>
          <p v-for="(count, key) in data.data_inventory" :key="key">
            <span>{{ key.replaceAll('_', ' ') }}</span><strong>{{ count }}</strong>
          </p>
        </article>
        <article class="governance-card">
          <h2>Classification</h2>
          <p><span>Current label</span><strong>{{ data.data_labels.classification || 'Not set' }}</strong></p>
          <p v-if="data.data_labels.organisation">
            <span>Organisation</span><strong>{{ data.data_labels.organisation }}</strong>
          </p>
          <p v-if="data.data_labels.framework_refs?.length" class="governance-card__refs">
            {{ data.data_labels.framework_refs.join(' · ') }}
          </p>
        </article>
      </section>

      <section v-else class="governance-grid">
        <article class="governance-card">
          <h2>Report evidence</h2>
          <p><span>Report manifests</span><strong>{{ data.report_exports }}</strong></p>
          <p><span>Expired manifests</span><strong>{{ data.expired_reports }}</strong></p>
          <p><span>Viewed</span><strong>{{ data.report_access.viewed }}</strong></p>
          <p><span>Exported</span><strong>{{ data.report_access.exported }}</strong></p>
          <p><span>Denied</span><strong>{{ data.report_access.denied }}</strong></p>
        </article>
        <article class="governance-card">
          <h2>Access changes</h2>
          <p><span>Course staff events</span><strong>{{ data.course_staff_events }}</strong></p>
          <p><span>Governance views</span><strong>{{ data.governance_views }}</strong></p>
          <p><span>Security events</span><strong>{{ data.security_events }}</strong></p>
        </article>
        <article class="governance-card">
          <h2>Integrity evidence</h2>
          <p><span>Ledger entries</span><strong>{{ data.integrity_entries }}</strong></p>
          <p><span>Unattributed writes</span><strong>{{ data.integrity_unattributed }}</strong></p>
          <p><span>Reviewed windows</span><strong>{{ data.integrity_reviews }}</strong></p>
        </article>
        <article class="governance-card">
          <h2>Decisions and records</h2>
          <p><span>Certificates</span><strong>{{ data.certificates }}</strong></p>
          <p><span>Review requests</span><strong>{{ data.review_requests }}</strong></p>
          <p><span>Retention runs</span><strong>{{ data.retention_runs }}</strong></p>
          <p><span>Erasure suppressions</span><strong>{{ data.erasure_suppressions }}</strong></p>
        </article>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const data = ref(null)
const loading = ref(true)
const error = ref('')
const activeTab = ref('privacy')

const role = (() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}').role || ''
  } catch {
    return ''
  }
})()

const availableTabs = computed(() => {
  const tabs = []
  if (['privacy_officer', 'institution_admin', 'admin'].includes(role)) {
    tabs.push({ id: 'privacy', label: 'Privacy office' })
  }
  if (['auditor', 'institution_admin', 'admin'].includes(role)) {
    tabs.push({ id: 'audit', label: 'Audit evidence' })
  }
  return tabs
})

const formatDate = (value) => {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

const load = async (tab) => {
  loading.value = true
  error.value = ''
  data.value = null
  try {
    const path = tab === 'privacy' ? '/governance/privacy/dashboard' : '/governance/audit/dashboard'
    const { data: payload } = await axios.get(path)
    data.value = payload
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load governance evidence.'
  } finally {
    loading.value = false
  }
}

const selectTab = (tab) => {
  activeTab.value = tab
  load(tab)
}

onMounted(() => {
  if (availableTabs.value.length) {
    activeTab.value = availableTabs.value[0].id
    load(activeTab.value)
  } else {
    loading.value = false
    error.value = 'Your role does not have access to a governance dashboard.'
  }
})
</script>

<style scoped>
.governance-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2rem;
}

.governance-page__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.governance-page__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.governance-page h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.4rem;
}

.governance-page__head p {
  max-width: 46rem;
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.55;
}

.governance-page__tabs {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.governance-page__tabs button {
  padding: 0.4rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.governance-page__tabs button.is-active {
  border-color: var(--accent);
  color: var(--accent-text);
  background: var(--accent-bg);
}

.governance-page__meta {
  margin: 0 0 0.9rem;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.governance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: 0.75rem;
}

.governance-card {
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.governance-card h2 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 0.86rem;
}

.governance-card p {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  margin: 0.25rem 0;
  color: var(--text-secondary);
  font-size: 0.74rem;
}

.governance-card p strong {
  color: var(--text-primary);
  text-align: right;
}

.governance-card p.muted,
.governance-card__refs {
  color: var(--text-muted);
  font-size: 0.7rem;
  line-height: 1.45;
  display: block;
}

.governance-page__empty {
  padding: 1.2rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.governance-page__empty--error {
  border-color: var(--danger);
  color: var(--danger);
}

@media (max-width: 640px) {
  .governance-page {
    padding: 1rem;
  }
}
</style>
