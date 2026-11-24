<template>
  <div class="contract-review">
    <header class="contract-review__head">
      <div>
        <p class="contract-review__eyebrow">Release 6 quality</p>
        <h1>Contract review</h1>
        <p class="contract-review__intro">
          Review the competency contract against the exercise, workbook, and
          evidence. Sign-off records the review cycle; it does not edit the
          generated contract or publish anything.
        </p>
      </div>
      <button type="button" class="btn btn--secondary btn--sm" :disabled="loadingQueue" @click="refreshQueue">
        {{ loadingQueue ? 'Loading...' : 'Refresh queue' }}
      </button>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="contract-review__message" role="status">{{ message }}</p>

    <section class="contract-review__summary" aria-label="Review cycle summary">
      <article v-for="(count, status) in counts" :key="status">
        <span>{{ statusLabel(status) }}</span>
        <strong>{{ count }}</strong>
      </article>
    </section>

    <div class="contract-review__layout">
      <aside class="contract-review__queue" aria-label="Contract review queue">
        <div class="contract-review__queue-head">
          <h2>Contracts</h2>
          <span class="contract-review__count">{{ filteredQueue.length }}</span>
        </div>
        <div class="contract-review__filters">
          <input v-model="search" type="search" class="form-input" placeholder="Filter by lab or track" />
          <select v-model="statusFilter" class="form-input">
            <option value="">All statuses</option>
            <option v-for="status in statusOptions" :key="status" :value="status">{{ statusLabel(status) }}</option>
          </select>
        </div>
        <p v-if="loadingQueue && !queue.length" class="contract-review__empty">Loading contracts...</p>
        <p v-else-if="!filteredQueue.length" class="contract-review__empty">No contracts match the filter.</p>
        <ul v-else class="contract-review__list">
          <li v-for="row in filteredQueue" :key="row.lab_slug">
            <button
              type="button"
              class="contract-review__item"
              :class="{ 'contract-review__item--active': row.lab_slug === selectedSlug }"
              :aria-current="row.lab_slug === selectedSlug ? 'true' : undefined"
              @click="selectContract(row.lab_slug)"
            >
              <span class="contract-review__item-top">
                <strong>{{ row.lab_slug }}</strong>
                <span class="contract-review__status" :class="`contract-review__status--${row.status}`">
                  {{ statusLabel(row.status) }}
                </span>
              </span>
              <span class="contract-review__item-meta">
                {{ row.track || 'Unknown track' }}
                <template v-if="row.next_review_at"> · next {{ formatDate(row.next_review_at) }}</template>
                <template v-if="row.reviewer_name"> · {{ row.reviewer_name }}</template>
              </span>
            </button>
          </li>
        </ul>
      </aside>

      <section class="contract-review__detail" aria-labelledby="contract-detail-title">
        <p v-if="loadingDetail" class="contract-review__empty">Loading contract...</p>
        <p v-else-if="!detail" class="contract-review__empty">
          Select a contract to review. A competency with no review is pending, not approved.
        </p>
        <template v-else>
          <div class="contract-review__detail-head">
            <div>
              <p class="contract-review__eyebrow">{{ detail.contract.track || 'Contract' }}</p>
              <h2 id="contract-detail-title">{{ detail.lab_slug }}</h2>
              <p class="contract-review__item-meta">
                {{ detail.contract.difficulty || 'unknown' }} ·
                {{ detail.contract.expected_duration_minutes || '—' }} minutes ·
                current {{ detail.status }}
              </p>
            </div>
            <span class="contract-review__status" :class="`contract-review__status--${detail.status}`">
              {{ statusLabel(detail.status) }}
            </span>
          </div>

          <section v-if="detail.latest" class="contract-review__block">
            <h3>Last signed review</h3>
            <p>
              {{ detail.latest.reviewer_name || 'Unknown reviewer' }} ·
              {{ detail.latest.decision }} ·
              {{ formatDate(detail.latest.signed_at) }}
            </p>
            <p v-if="detail.latest.next_review_at" class="contract-review__muted">
              Next review {{ formatDate(detail.latest.next_review_at) }} ·
              cycle {{ detail.latest.review_cycle_months }} months
            </p>
            <p v-if="detail.latest.deviation" class="contract-review__muted">
              Changes: {{ deviationText(detail.latest.deviation) }}
            </p>
          </section>

          <section class="contract-review__block">
            <h3>Competencies</h3>
            <div v-for="(row, index) in form.competencies" :key="index" class="contract-review__row">
              <select v-model="row.id" class="form-input">
                <option v-for="competency in catalogue.competencies" :key="competency.id" :value="competency.id">
                  {{ competency.id }} — {{ competency.name }}
                </option>
              </select>
              <input v-model.number="row.weight" type="number" min="0" max="1" step="0.05" class="form-input contract-review__weight" />
              <button type="button" class="btn btn--outline btn--sm" @click="form.competencies.splice(index, 1)">Remove</button>
            </div>
            <p class="contract-review__muted">Competency weight total: {{ competencyTotal.toFixed(2) }}</p>
            <button type="button" class="btn btn--outline btn--sm" @click="addCompetency">Add competency</button>
          </section>

          <section class="contract-review__block">
            <h3>Evidence</h3>
            <div v-for="(row, index) in form.evidence" :key="index" class="contract-review__row">
              <select v-model="row.type" class="form-input">
                <option v-for="type in catalogue.evidence_types" :key="type" :value="type">{{ type }}</option>
              </select>
              <input v-model.number="row.weight" type="number" min="0" max="1" step="0.05" class="form-input contract-review__weight" />
              <input v-model="row.source" class="form-input" placeholder="source" />
              <input v-model="row.validation" class="form-input" placeholder="validation" />
              <button type="button" class="btn btn--outline btn--sm" @click="form.evidence.splice(index, 1)">Remove</button>
            </div>
            <p class="contract-review__muted">Evidence weight total: {{ evidenceTotal.toFixed(2) }}</p>
            <button type="button" class="btn btn--outline btn--sm" @click="addEvidence">Add evidence</button>
          </section>

          <section class="contract-review__block">
            <h3>Reliability and criteria</h3>
            <div class="contract-review__grid">
              <label><span>Level</span><select v-model="form.reliability.level" class="form-input"><option value="low">low</option><option value="medium">medium</option><option value="high">high</option></select></label>
              <label><span>Score</span><input v-model.number="form.reliability.score" type="number" min="0" max="1" step="0.05" class="form-input" /></label>
              <label><span>Evidence completeness</span><select v-model="form.reliability.evidence_completeness" class="form-input"><option value="low">low</option><option value="medium">medium</option><option value="high">high</option></select></label>
              <label><span>Determinism</span><input v-model="form.reliability.determinism" class="form-input" /></label>
              <label><span>Independent validation</span><input v-model="form.reliability.independent_validation" class="form-input" /></label>
            </div>
            <label class="contract-review__field">
              <span>Reliability rationale</span>
              <textarea v-model="form.reliability.rationale" class="form-input" rows="3" />
            </label>
            <label class="contract-review__field">
              <span>Assessment criteria, one per line</span>
              <textarea v-model="criteriaText" class="form-input" rows="3" />
            </label>
          </section>

          <section class="contract-review__block">
            <h3>Sign-off</h3>
            <label class="contract-review__field">
              <span>Review rationale</span>
              <textarea v-model="form.rationale" class="form-input" rows="3" placeholder="What did you inspect, and why is this contract right?" />
            </label>
            <div class="contract-review__grid">
              <label><span>Decision</span><select v-model="form.decision" class="form-input"><option value="">Choose a decision</option><option value="approved">Approve</option><option value="changes_requested">Request changes</option></select></label>
              <label><span>Cycle</span><select v-model.number="form.cycle_months" class="form-input"><option v-for="months in catalogue.cycle_months" :key="months" :value="months">{{ months }} months</option></select></label>
            </div>
            <label class="contract-review__check">
              <input v-model="form.attestation" type="checkbox" />
              <span>I inspected the exercise, workbook, and evidence, and I sign this review.</span>
            </label>
            <p class="contract-review__muted">
              Competency weights {{ competencyTotal.toFixed(2) }} · evidence {{ evidenceTotal.toFixed(2) }} ·
              rationale {{ form.rationale.trim().length }}/20 characters.
            </p>
            <div class="contract-review__actions">
              <button type="button" class="btn btn--outline btn--sm" :disabled="savingDraft" @click="saveDraft">
                {{ savingDraft ? 'Saving...' : 'Save draft' }}
              </button>
              <button type="button" class="btn btn--primary btn--sm" :disabled="!canSign || signing" @click="signReview">
                {{ signing ? 'Signing...' : 'Sign review' }}
              </button>
            </div>
            <p v-if="!canSign" class="contract-review__muted">
              A signature needs a decision, the attestation, a 20-character rationale, and weights that total 1.00.
            </p>
          </section>

          <section v-if="detail.history.length" class="contract-review__block">
            <h3>History</h3>
            <article v-for="row in detail.history" :key="row.id" class="contract-review__history">
              <p>
                <strong>{{ row.decision || row.status }}</strong> ·
                {{ row.reviewer_name || 'Unknown' }} ·
                {{ formatDate(row.signed_at || row.created_at) }}
              </p>
              <p class="contract-review__muted">{{ row.rationale }}</p>
            </article>
          </section>
        </template>
      </section>
    </div>

    <section v-if="isAdmin" class="contract-review__block">
      <h3>Approved reviews waiting for export</h3>
      <p v-if="!exportReady.length" class="contract-review__muted">No approved review is waiting for export.</p>
      <ul v-else class="contract-review__list">
        <li v-for="row in exportReady" :key="row.id" class="contract-review__export-row">
          <span>{{ row.lab_slug }} · {{ row.reviewer_name }} · {{ formatDate(row.signed_at) }}</span>
          <button type="button" class="btn btn--outline btn--sm" @click="markExported(row.id)">Mark exported</button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const queue = ref([])
const counts = ref({})
const catalogue = ref({ domains: [], competencies: [], evidence_types: [], cycle_months: [6, 12, 24] })
const detail = ref(null)
const exportReady = ref([])
const selectedSlug = ref('')
const search = ref('')
const statusFilter = ref('')
const loadingQueue = ref(false)
const loadingDetail = ref(false)
const savingDraft = ref(false)
const signing = ref(false)
const error = ref('')
const message = ref('')
const criteriaText = ref('')

const form = reactive({
  competencies: [],
  evidence: [],
  reliability: {},
  rationale: '',
  decision: '',
  cycle_months: 12,
  attestation: false,
})

const statusOptions = [
  'pending', 'draft', 'changes_requested', 'current', 'due_soon', 'overdue', 'stale',
]

const userRole = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}').role || ''
  } catch {
    return ''
  }
})
const isAdmin = computed(() => ['admin', 'institution_admin'].includes(userRole.value))

const filteredQueue = computed(() => {
  const term = search.value.trim().toLowerCase()
  return queue.value.filter((row) => {
    if (statusFilter.value && row.status !== statusFilter.value) return false
    if (!term) return true
    return `${row.lab_slug} ${row.track || ''}`.toLowerCase().includes(term)
  })
})

const competencyTotal = computed(() =>
  (form.competencies || []).reduce((total, row) => total + (Number(row.weight) || 0), 0)
)
const evidenceTotal = computed(() =>
  (form.evidence || []).reduce((total, row) => total + (Number(row.weight) || 0), 0)
)

const canSign = computed(() =>
  Boolean(
    form.decision &&
    form.attestation &&
    form.rationale.trim().length >= 20 &&
    Math.abs(competencyTotal.value - 1) < 0.001 &&
    Math.abs(evidenceTotal.value - 1) < 0.001
  )
)

function statusLabel(value) {
  return String(value || '').replaceAll('_', ' ')
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function deviationText(deviation) {
  const parts = []
  if (deviation.competencies_added?.length) parts.push(`added ${deviation.competencies_added.join(', ')}`)
  if (deviation.competencies_removed?.length) parts.push(`removed ${deviation.competencies_removed.join(', ')}`)
  if (deviation.weights_changed?.length) parts.push(`weights ${deviation.weights_changed.join(', ')}`)
  return parts.length ? parts.join('; ') : 'none'
}

function addCompetency() {
  form.competencies.push({ id: catalogue.value.competencies[0]?.id || '', weight: 0.1 })
}

function addEvidence() {
  form.evidence.push({ type: catalogue.value.evidence_types[0] || 'artifact', weight: 0.1, source: '', validation: '' })
}

function populate(detailPayload) {
  detail.value = detailPayload
  const source =
    detailPayload.draft?.contract_snapshot ||
    detailPayload.latest?.contract_snapshot ||
    detailPayload.contract
  form.competencies = (source.competency_ids || []).map((row) => ({
    id: String(row.id),
    weight: Number(row.weight) || 0,
  }))
  form.evidence = (source.evidence || []).map((row) => ({
    type: row.type,
    weight: Number(row.weight) || 0,
    source: row.source || '',
    validation: row.validation || '',
  }))
  form.reliability = { ...(source.assessment_reliability || {}) }
  form.rationale = detailPayload.draft?.rationale || detailPayload.latest?.rationale || ''
  form.decision = ''
  form.cycle_months = detailPayload.latest?.review_cycle_months || 12
  form.attestation = false
  criteriaText.value = (source.assessment_criteria || []).join('\n')
}

async function refreshQueue() {
  loadingQueue.value = true
  error.value = ''
  try {
    const response = await axios.get('/competency-reviews/queue')
    queue.value = response.data.contracts || []
    counts.value = response.data.counts || {}
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load the contract queue.'
  } finally {
    loadingQueue.value = false
  }
}

async function selectContract(slug) {
  selectedSlug.value = slug
  loadingDetail.value = true
  error.value = ''
  message.value = ''
  try {
    const response = await axios.get(`/competency-reviews/${slug}`)
    populate(response.data)
  } catch (err) {
    detail.value = null
    error.value = err.response?.data?.detail || 'Could not load the contract.'
  } finally {
    loadingDetail.value = false
  }
}

function payload() {
  return {
    competency_ids: form.competencies.map((row) => ({ id: row.id, weight: Number(row.weight) })),
    evidence: form.evidence.map((row) => ({
      type: row.type,
      weight: Number(row.weight),
      source: row.source || null,
      validation: row.validation || null,
    })),
    assessment_reliability: form.reliability,
    assessment_criteria: criteriaText.value.split('\n').map((line) => line.trim()).filter(Boolean),
    review_cycle_months: form.cycle_months,
    rationale: form.rationale,
    decision: form.decision || null,
    attestation: form.attestation,
  }
}

async function saveDraft() {
  if (!selectedSlug.value) return
  savingDraft.value = true
  error.value = ''
  message.value = ''
  try {
    await axios.post(`/competency-reviews/${selectedSlug.value}/draft`, payload())
    message.value = 'Draft saved.'
    await refreshQueue()
    await selectContract(selectedSlug.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not save the draft.'
  } finally {
    savingDraft.value = false
  }
}

async function signReview() {
  if (!selectedSlug.value || !canSign.value) return
  signing.value = true
  error.value = ''
  message.value = ''
  try {
    await axios.post(`/competency-reviews/${selectedSlug.value}/sign`, payload())
    message.value = 'Review signed.'
    await refreshQueue()
    await selectContract(selectedSlug.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not sign the review.'
  } finally {
    signing.value = false
  }
}

async function loadExportReady() {
  if (!isAdmin.value) return
  try {
    const response = await axios.get('/competency-reviews/export-ready')
    exportReady.value = response.data.reviews || []
  } catch {
    exportReady.value = []
  }
}

async function markExported(id) {
  try {
    await axios.post(`/competency-reviews/${id}/exported`)
    message.value = 'Marked exported.'
    await loadExportReady()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not mark the review exported.'
  }
}

onMounted(async () => {
  try {
    const response = await axios.get('/competency-reviews/catalogue')
    catalogue.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load the competency catalogue.'
  }
  await refreshQueue()
  await loadExportReady()
})
</script>

<style scoped>
.contract-review {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
}

.contract-review__head,
.contract-review__detail-head,
.contract-review__queue-head,
.contract-review__export-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.contract-review__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.contract-review__head h1,
.contract-review__detail-head h2 {
  margin: 0 0 0.4rem;
}

.contract-review__intro,
.contract-review__muted,
.contract-review__item-meta {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.contract-review__summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.6rem;
}

.contract-review__summary article,
.contract-review__queue,
.contract-review__detail,
.contract-review__block {
  border: 1px solid var(--border-color);
  border-radius: 0.8rem;
  background: var(--bg-secondary);
  padding: 0.9rem;
}

.contract-review__summary article {
  display: grid;
  gap: 0.2rem;
}

.contract-review__summary span {
  color: var(--text-muted);
  font-size: 0.75rem;
  text-transform: capitalize;
}

.contract-review__summary strong {
  font-size: 1.35rem;
}

.contract-review__layout {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
  align-items: start;
}

.contract-review__filters {
  display: grid;
  gap: 0.4rem;
  margin-bottom: 0.6rem;
}

.contract-review__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.45rem;
}

.contract-review__item {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border-color);
  border-radius: 0.6rem;
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 0.6rem;
  cursor: pointer;
  display: grid;
  gap: 0.25rem;
}

.contract-review__item--active {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
}

.contract-review__item-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}

.contract-review__status {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: capitalize;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.contract-review__status--current { background: var(--success-bg); color: var(--success); }
.contract-review__status--overdue,
.contract-review__status--stale { background: var(--danger-bg); color: var(--danger); }
.contract-review__status--due_soon,
.contract-review__status--changes_requested { background: var(--warning-bg); color: var(--warning); }
.contract-review__status--draft { background: var(--accent-bg); color: var(--accent-text); }

.contract-review__detail {
  display: grid;
  gap: 0.8rem;
}

.contract-review__block {
  display: grid;
  gap: 0.55rem;
}

.contract-review__block h3 {
  margin: 0;
  font-size: 0.95rem;
}

.contract-review__row {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) 90px 90px minmax(120px, 1fr) minmax(120px, 1fr) auto;
  gap: 0.4rem;
  align-items: center;
}

.contract-review__weight {
  max-width: 90px;
}

.contract-review__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.6rem;
}

.contract-review__grid label,
.contract-review__field,
.contract-review__check {
  display: grid;
  gap: 0.25rem;
}

.contract-review__field,
.contract-review__check {
  grid-column: 1 / -1;
}

.contract-review__check {
  grid-template-columns: auto 1fr;
  align-items: start;
}

.contract-review__actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.contract-review__history {
  border-top: 1px solid var(--border-color);
  padding-top: 0.4rem;
}

.contract-review__message {
  color: var(--success);
  background: var(--success-bg);
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.contract-review__empty {
  color: var(--text-muted);
  padding: 0.8rem 0;
}

@media (max-width: 980px) {
  .contract-review__layout {
    grid-template-columns: 1fr;
  }

  .contract-review__row {
    grid-template-columns: 1fr;
  }
}
</style>
