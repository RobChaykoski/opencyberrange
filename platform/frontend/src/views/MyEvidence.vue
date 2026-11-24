<template>
  <div class="my-evidence">
    <header class="my-evidence__head">
      <p class="my-evidence__eyebrow">Learning evidence</p>
      <h1>My evidence</h1>
      <p>
        Every reviewed or automatically verified practice record appears here.
        A rejected record can be appealed for a second review.
      </p>
    </header>

    <p v-if="message" class="my-evidence__message" role="status">{{ message }}</p>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="my-evidence__empty">Loading your evidence...</p>
    <p v-else-if="!records.length" class="my-evidence__empty">
      No evidence yet. Complete an exercise, pass a knowledge check, or save a
      workbook answer.
    </p>

    <ul v-else class="my-evidence__list">
      <li v-for="item in records" :key="item.id" class="my-evidence__card">
        <div class="my-evidence__card-head">
          <div>
            <span class="my-evidence__source">{{ item.source_type }} · {{ item.source_id }}</span>
            <h2>{{ item.rubric.id }} v{{ item.rubric.version }}</h2>
          </div>
          <span class="my-evidence__status" :class="`my-evidence__status--${item.status}`">
            {{ statusLabel(item.status) }}
          </span>
        </div>

        <p class="my-evidence__meta">
          Collected {{ formatDate(item.collected_at) }}
          <template v-if="item.confidence"> · confidence {{ item.confidence }}</template>
        </p>

        <p
          v-if="item.contract_status?.provisional"
          class="my-evidence__contract"
          :class="`my-evidence__contract--${item.contract_status.status === 'pending' ? 'info' : 'warning'}`"
        >
          {{ contractNote(item.contract_status) }}
        </p>

        <p v-if="item.content_text" class="my-evidence__answer">{{ item.content_text }}</p>

        <div v-if="item.competencies.length" class="my-evidence__competencies">
          <span v-for="link in item.competencies" :key="link.competency_id">
            {{ link.competency_id }}
          </span>
        </div>

        <div v-if="item.latest_review" class="my-evidence__review">
          <strong>{{ statusLabel(item.latest_review.decision) }}</strong>
          <span v-if="item.latest_review.weighted_score !== null && item.latest_review.weighted_score !== undefined">
            · {{ Math.round(item.latest_review.weighted_score * 100) }}%
          </span>
          <p v-if="item.latest_review.notes">{{ item.latest_review.notes }}</p>
          <p v-if="item.latest_review.next_step" class="my-evidence__note">
            Next step: {{ item.latest_review.next_step }}
          </p>
        </div>

        <div v-if="item.appeals.length" class="my-evidence__appeals">
          <p class="my-evidence__note">Appeals</p>
          <p v-for="appeal in item.appeals" :key="appeal.id">
            <strong>{{ statusLabel(appeal.status) }}</strong> · {{ formatDate(appeal.created_at) }}
            <span v-if="appeal.decision_notes"> — {{ appeal.decision_notes }}</span>
          </p>
        </div>

        <div v-if="canAppeal(item)" class="my-evidence__appeal-form">
          <label>
            <span>Why should this be reviewed again?</span>
            <textarea
              v-model="appealReasons[item.id]"
              class="form-input"
              rows="3"
              maxlength="2000"
              placeholder="Point to the evidence the reviewer may have missed."
            />
          </label>
          <button
            type="button"
            class="btn btn--secondary btn--sm"
            :disabled="appealingId === item.id || (appealReasons[item.id] || '').trim().length < 10"
            @click="appeal(item)"
          >
            {{ appealingId === item.id ? 'Submitting...' : 'Request second review' }}
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const records = ref([])
const loading = ref(false)
const error = ref('')
const message = ref('')
const appealingId = ref(null)
const appealReasons = reactive({})

function statusLabel(status) {
  return String(status || '').replace('_', ' ')
}

function contractNote(status) {
  const value = status?.status
  if (value === 'pending') {
    return 'The competency mapping for this exercise is pending review; the skills credited are provisional.'
  }
  if (value === 'changes_requested') {
    return 'The competency mapping is under revision; the skills credited may change.'
  }
  if (value === 'overdue') {
    return 'The competency mapping is overdue for review; the skills credited may be out of date.'
  }
  if (value === 'stale') {
    return 'The exercise changed after its competency review; the skills credited may be out of date.'
  }
  return ''
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function canAppeal(item) {
  return (
    item.status === 'rejected' &&
    !(item.appeals || []).some((appeal) => appeal.status === 'pending')
  )
}

async function loadEvidence() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/evidence', { params: { limit: 100 } })
    records.value = response.data.evidence || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load your evidence.'
  } finally {
    loading.value = false
  }
}

async function appeal(item) {
  appealingId.value = item.id
  message.value = ''
  error.value = ''
  try {
    await axios.post(`/evidence/${item.id}/appeal`, {
      reason: appealReasons[item.id],
    })
    message.value = 'Second review requested.'
    appealReasons[item.id] = ''
    await loadEvidence()
  } catch (err) {
    error.value =
      err.response?.data?.detail || 'Could not request a second review.'
  } finally {
    appealingId.value = null
  }
}

onMounted(loadEvidence)
</script>

<style scoped>
.my-evidence {
  max-width: 980px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
}

.my-evidence__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.my-evidence__head h1 {
  margin: 0 0 0.5rem;
}

.my-evidence__head p {
  margin: 0;
  color: var(--text-muted);
}

.my-evidence__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.75rem;
}

.my-evidence__card {
  border: 1px solid var(--border-color);
  border-radius: 0.8rem;
  background: var(--bg-secondary);
  padding: 1rem;
  display: grid;
  gap: 0.6rem;
}

.my-evidence__card-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: start;
}

.my-evidence__card-head h2 {
  margin: 0.2rem 0 0;
  font-size: 1rem;
}

.my-evidence__source,
.my-evidence__meta,
.my-evidence__note {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.my-evidence__contract {
  margin: 0;
  padding: 0.5rem 0.7rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 0.35rem 0.35rem 0;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.my-evidence__contract--warning {
  border-left-color: var(--warning);
  background: color-mix(in srgb, var(--warning) 8%, var(--bg-secondary));
}

.my-evidence__status {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: capitalize;
  background: #e2e8f0;
  color: #334155;
}

.my-evidence__status--accepted {
  background: #dcfce7;
  color: #166534;
}

.my-evidence__status--rejected {
  background: #fee2e2;
  color: #991b1b;
}

.my-evidence__status--in_review {
  background: #fef3c7;
  color: #92400e;
}

.my-evidence__answer {
  white-space: pre-wrap;
  line-height: 1.5;
  background: var(--bg-tertiary);
  border-radius: 0.5rem;
  padding: 0.7rem;
  margin: 0;
}

.my-evidence__competencies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.my-evidence__competencies span {
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent, #2563eb);
  font-size: 0.75rem;
  font-weight: 600;
}

.my-evidence__review,
.my-evidence__appeals {
  border-top: 1px solid var(--border-color);
  padding-top: 0.5rem;
}

.my-evidence__review p,
.my-evidence__appeals p {
  margin: 0.25rem 0 0;
}

.my-evidence__appeal-form {
  display: grid;
  gap: 0.5rem;
  border-top: 1px solid var(--border-color);
  padding-top: 0.6rem;
}

.my-evidence__appeal-form label {
  display: grid;
  gap: 0.25rem;
}

.my-evidence__message {
  color: #166534;
  background: #dcfce7;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.my-evidence__empty {
  color: var(--text-muted);
  padding: 1rem 0;
}
</style>
