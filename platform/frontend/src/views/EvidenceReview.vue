<template>
  <div class="evidence-review">
    <header class="evidence-review__head">
      <div>
        <p class="evidence-review__eyebrow">Release 6 evidence</p>
        <h1>Evidence review</h1>
        <p class="evidence-review__intro">
          Review evidence against the rubric version it was collected with. A
          decision is appended; the evidence record itself is never edited.
        </p>
      </div>
      <button
        type="button"
        class="btn btn--secondary btn--sm"
        :disabled="loadingQueue"
        @click="refreshQueue"
      >
        {{ loadingQueue ? 'Loading...' : 'Refresh queue' }}
      </button>
    </header>

    <p v-if="queueError" class="form-error" role="alert">{{ queueError }}</p>
    <p v-if="message" class="evidence-review__message" role="status">{{ message }}</p>

    <div class="evidence-review__layout">
      <aside class="evidence-review__queue" aria-label="Evidence review queue">
        <div class="evidence-review__queue-head">
          <h2>Awaiting review</h2>
          <span class="evidence-review__count">{{ queue.length }}</span>
        </div>

        <p v-if="loadingQueue && !queue.length" class="evidence-review__empty">
          Loading the queue...
        </p>
        <p v-else-if="!queue.length" class="evidence-review__empty">
          No evidence is waiting for review.
        </p>
        <ul v-else class="evidence-review__list">
          <li v-for="item in queue" :key="item.id">
            <button
              type="button"
              class="evidence-review__queue-item"
              :class="{ 'evidence-review__queue-item--active': item.id === selectedId }"
              @click="selectRecord(item.id)"
            >
              <span class="evidence-review__queue-top">
                <strong>{{ item.learner?.username || `Learner ${item.learner_id}` }}</strong>
                <span class="evidence-review__status" :class="`evidence-review__status--${item.status}`">
                  {{ statusLabel(item.status) }}
                </span>
              </span>
              <span class="evidence-review__queue-source">{{ item.source_type }} · {{ item.source_id }}</span>
              <span class="evidence-review__queue-meta">
                {{ item.rubric.id }} v{{ item.rubric.version }}
                <template v-if="item.collected_at"> · {{ formatDate(item.collected_at) }}</template>
              </span>
            </button>
          </li>
        </ul>
      </aside>

      <section class="evidence-review__detail" aria-labelledby="evidence-detail-title">
        <p v-if="detailError" class="form-error" role="alert">{{ detailError }}</p>
        <p v-if="loadingDetail" class="evidence-review__empty">Loading evidence...</p>
        <p v-else-if="!record" class="evidence-review__empty">
          Select an item from the queue to review it.
        </p>

        <template v-else>
          <div class="evidence-review__detail-head">
            <div>
              <p class="evidence-review__eyebrow">Evidence #{{ record.id }}</p>
              <h2 id="evidence-detail-title">
                {{ record.learner?.display_name || record.learner?.username || `Learner ${record.learner_id}` }}
              </h2>
              <p class="evidence-review__detail-sub">
                {{ record.source_type }} · {{ record.source_id }}
              </p>
            </div>
            <span class="evidence-review__status" :class="`evidence-review__status--${record.status}`">
              {{ statusLabel(record.status) }}
            </span>
          </div>

          <dl class="evidence-review__meta">
            <div><dt>Rubric</dt><dd>{{ record.rubric.id }} v{{ record.rubric.version }}</dd></div>
            <div><dt>Confidence</dt><dd>{{ record.confidence }}</dd></div>
            <div><dt>Provenance</dt><dd>{{ record.provenance }}{{ record.provenance_version ? ` ${record.provenance_version}` : '' }}</dd></div>
            <div><dt>Collected</dt><dd>{{ formatDate(record.collected_at) }}</dd></div>
            <div><dt>Visibility</dt><dd>{{ record.visibility }}</dd></div>
            <div><dt>Formula</dt><dd>{{ record.formula_version }}</dd></div>
          </dl>

          <section v-if="record.artifact" class="evidence-review__block" aria-labelledby="evidence-artifact-title">
            <h3 id="evidence-artifact-title">Artifact</h3>
            <p class="evidence-review__mono">{{ record.artifact.sha256 }}</p>
            <p class="evidence-review__note">
              {{ record.artifact.mime || 'Unknown type' }}
              <template v-if="record.artifact.size !== null && record.artifact.size !== undefined">
                · {{ record.artifact.size }} bytes
              </template>
            </p>
          </section>

          <section class="evidence-review__block" aria-labelledby="evidence-competencies-title">
            <h3 id="evidence-competencies-title">Competencies and criteria</h3>
            <ul class="evidence-review__competencies">
              <li v-for="link in record.competencies" :key="link.competency_id">
                <strong>{{ link.competency_id }}</strong>
                <span class="evidence-review__criteria">{{ link.criteria.join(', ') }}</span>
                <span class="evidence-review__weight">weight {{ link.weight }}</span>
              </li>
            </ul>
          </section>

          <section class="evidence-review__block" aria-labelledby="evidence-rubric-title">
            <div class="evidence-review__block-head">
              <h3 id="evidence-rubric-title">Rubric</h3>
              <span v-if="selectedRubric" class="evidence-review__note">{{ selectedRubric.title }}</span>
            </div>
            <p v-if="!selectedRubric" class="form-error">
              The recorded rubric version is not available. Review is blocked.
            </p>
            <table v-else class="evidence-review__rubric">
              <thead>
                <tr><th scope="col">Criterion</th><th scope="col">Weight</th><th scope="col">Score</th></tr>
              </thead>
              <tbody>
                <tr v-for="criterion in selectedRubric.criteria" :key="criterion.id">
                  <th scope="row">
                    {{ criterion.label }}
                    <span class="evidence-review__note">{{ criterion.id }}</span>
                  </th>
                  <td>{{ criterion.weight }}</td>
                  <td>
                    <select
                      v-model.number="scores[criterion.id]"
                      class="form-input form-input--sm"
                      :aria-label="`${criterion.label} score`"
                    >
                      <option :value="null">Select</option>
                      <option v-for="level in 4" :key="level" :value="level - 1">
                        {{ level - 1 }} — {{ criterion.levels[level - 1] }}
                      </option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="selectedRubric" class="evidence-review__note">
              A score of 3 is the strongest observable descriptor. Accepted decisions
              require every criterion to be scored.
            </p>
          </section>

          <section v-if="canReview" class="evidence-review__block" aria-labelledby="evidence-decision-title">
            <h3 id="evidence-decision-title">Decision</h3>
            <div class="evidence-review__form-grid">
              <label class="evidence-review__field">
                <span>Decision</span>
                <select v-model="decision" class="form-input">
                  <option value="accepted">Accept</option>
                  <option value="more_evidence">Request more evidence</option>
                  <option value="rejected">Reject</option>
                </select>
              </label>
              <label class="evidence-review__field evidence-review__field--wide">
                <span>Notes</span>
                <textarea
                  v-model="notes"
                  class="form-input"
                  rows="3"
                  maxlength="1000"
                  placeholder="What is strong, what is missing, and why?"
                />
              </label>
              <label v-if="decision !== 'accepted'" class="evidence-review__field evidence-review__field--wide">
                <span>Next step for the learner</span>
                <input v-model="nextStep" class="form-input" maxlength="500" />
              </label>
            </div>
            <p v-if="reviewError" class="form-error" role="alert">{{ reviewError }}</p>
            <button
              type="button"
              class="btn btn--primary btn--sm"
              :disabled="submitting"
              @click="submitReview"
            >
              {{ submitting ? 'Saving...' : 'Record decision' }}
            </button>
          </section>

          <section v-if="record.reviews.length" class="evidence-review__block" aria-labelledby="evidence-history-title">
            <h3 id="evidence-history-title">Review history</h3>
            <article v-for="review in record.reviews" :key="review.id" class="evidence-review__history">
              <div class="evidence-review__history-head">
                <strong>{{ statusLabel(review.decision) }}</strong>
                <span>{{ formatDate(review.reviewed_at) }}</span>
              </div>
              <p v-if="review.weighted_score !== null && review.weighted_score !== undefined">
                Weighted score: {{ Math.round(review.weighted_score * 100) }}%
              </p>
              <p v-if="review.notes">{{ review.notes }}</p>
              <p v-if="review.next_step" class="evidence-review__note">Next step: {{ review.next_step }}</p>
            </article>
          </section>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const queue = ref([])
const rubrics = ref([])
const record = ref(null)
const selectedId = ref(null)
const loadingQueue = ref(false)
const loadingDetail = ref(false)
const queueError = ref('')
const detailError = ref('')
const reviewError = ref('')
const message = ref('')
const submitting = ref(false)
const decision = ref('accepted')
const notes = ref('')
const nextStep = ref('')
const scores = reactive({})

const selectedRubric = computed(() => {
  if (!record.value) return null
  return (
    rubrics.value.find(
      (item) =>
        item.rubric === record.value.rubric.id &&
        String(item.version) === String(record.value.rubric.version)
    ) || null
  )
})

const canReview = computed(
  () => record.value && ['collected', 'in_review'].includes(record.value.status)
)

function statusLabel(status) {
  return String(status || '').replace('_', ' ')
}

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function resetForm() {
  decision.value = 'accepted'
  notes.value = ''
  nextStep.value = ''
  reviewError.value = ''
  Object.keys(scores).forEach((key) => delete scores[key])
  if (selectedRubric.value) {
    selectedRubric.value.criteria.forEach((criterion) => {
      scores[criterion.id] = null
    })
  }
}

async function fetchRubrics() {
  const response = await axios.get('/evidence/rubrics')
  rubrics.value = response.data.rubrics || []
}

async function refreshQueue() {
  loadingQueue.value = true
  queueError.value = ''
  try {
    const response = await axios.get('/evidence/queue', { params: { limit: 100 } })
    queue.value = response.data.evidence || []
    if (!queue.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = null
      record.value = null
    }
  } catch (error) {
    queueError.value = error.response?.data?.detail || 'Could not load the evidence queue.'
  } finally {
    loadingQueue.value = false
  }
}

async function selectRecord(id) {
  selectedId.value = id
  loadingDetail.value = true
  detailError.value = ''
  message.value = ''
  try {
    const response = await axios.get(`/evidence/${id}`)
    record.value = response.data.evidence
    resetForm()
  } catch (error) {
    record.value = null
    detailError.value = error.response?.data?.detail || 'Could not load this evidence record.'
  } finally {
    loadingDetail.value = false
  }
}

function payloadScores() {
  return Object.fromEntries(
    Object.entries(scores).filter(
      ([, value]) => value !== null && value !== undefined && value !== ''
    )
  )
}

async function submitReview() {
  if (!record.value) return
  reviewError.value = ''
  submitting.value = true
  try {
    await axios.post(`/evidence/${record.value.id}/review`, {
      decision: decision.value,
      criterion_scores: payloadScores(),
      notes: notes.value || null,
      next_step: nextStep.value || null,
    })
    message.value = 'Decision recorded.'
    await refreshQueue()
    await selectRecord(record.value.id)
  } catch (error) {
    reviewError.value =
      error.response?.data?.detail || 'Could not record the decision. Check the scores and notes.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    await fetchRubrics()
  } catch (error) {
    detailError.value = error.response?.data?.detail || 'Could not load the rubric registry.'
  }
  await refreshQueue()
})
</script>

<style scoped>
.evidence-review {
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.evidence-review__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.evidence-review__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.evidence-review__head h1,
.evidence-review__detail h2 {
  margin: 0;
}

.evidence-review__intro,
.evidence-review__detail-sub,
.evidence-review__note {
  color: var(--text-muted, #64748b);
}

.evidence-review__layout {
  display: grid;
  grid-template-columns: minmax(280px, 360px) 1fr;
  gap: 1rem;
  align-items: start;
}

.evidence-review__queue,
.evidence-review__detail {
  background: var(--surface, #fff);
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.8rem;
  padding: 1rem;
}

.evidence-review__queue-head,
.evidence-review__detail-head,
.evidence-review__block-head,
.evidence-review__history-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.evidence-review__queue-head h2,
.evidence-review__block h3 {
  margin: 0 0 0.5rem;
}

.evidence-review__count {
  display: inline-grid;
  place-items: center;
  min-width: 1.8rem;
  height: 1.8rem;
  border-radius: 999px;
  background: var(--accent-soft, #e0ecff);
  color: var(--accent, #2563eb);
  font-weight: 700;
}

.evidence-review__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.evidence-review__queue-item {
  width: 100%;
  display: grid;
  gap: 0.25rem;
  text-align: left;
  padding: 0.75rem;
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.6rem;
  background: transparent;
  cursor: pointer;
}

.evidence-review__queue-item--active {
  border-color: var(--accent, #2563eb);
  background: var(--accent-soft, #eff6ff);
}

.evidence-review__queue-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  align-items: center;
}

.evidence-review__queue-source,
.evidence-review__queue-meta {
  color: var(--text-muted, #64748b);
  font-size: 0.82rem;
}

.evidence-review__status {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: capitalize;
  background: #e2e8f0;
  color: #334155;
}

.evidence-review__status--accepted {
  background: #dcfce7;
  color: #166534;
}

.evidence-review__status--rejected {
  background: #fee2e2;
  color: #991b1b;
}

.evidence-review__status--in_review {
  background: #fef3c7;
  color: #92400e;
}

.evidence-review__meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}

.evidence-review__meta dt {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted, #64748b);
}

.evidence-review__meta dd {
  margin: 0.15rem 0 0;
  word-break: break-word;
}

.evidence-review__block {
  border-top: 1px solid var(--border, #dbe3ee);
  padding-top: 1rem;
  margin-top: 1rem;
}

.evidence-review__competencies {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.evidence-review__competencies li {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: baseline;
}

.evidence-review__criteria,
.evidence-review__weight {
  color: var(--text-muted, #64748b);
  font-size: 0.85rem;
}

.evidence-review__rubric {
  width: 100%;
  border-collapse: collapse;
}

.evidence-review__rubric th,
.evidence-review__rubric td {
  text-align: left;
  padding: 0.55rem 0.4rem;
  border-bottom: 1px solid var(--border, #dbe3ee);
  vertical-align: top;
}

.evidence-review__rubric select {
  min-width: 11rem;
}

.evidence-review__form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.evidence-review__field {
  display: grid;
  gap: 0.3rem;
}

.evidence-review__field--wide {
  grid-column: 1 / -1;
}

.evidence-review__history {
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.6rem;
  padding: 0.75rem;
  margin-top: 0.6rem;
}

.evidence-review__mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.evidence-review__message {
  color: #166534;
  background: #dcfce7;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.evidence-review__empty {
  color: var(--text-muted, #64748b);
  padding: 1rem 0;
}

@media (max-width: 900px) {
  .evidence-review__layout {
    grid-template-columns: 1fr;
  }

  .evidence-review__form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
