<template>
  <section class="qbank" aria-labelledby="qbank-title">
    <header class="qbank__head">
      <div>
        <p class="qbank__eyebrow">Question banks</p>
        <h2 id="qbank-title">Certification-aligned practice</h2>
        <p class="qbank__intro">
          These are original exam-style items written to public certification
          objectives. The full bank, answers, explanations, and references are
          visible only to administrators. Learners receive a three-question sample
          and see the answer key after they submit.
        </p>
      </div>
      <div class="qbank__actions">
        <button type="button" class="btn btn--secondary btn--sm" :disabled="validating" @click="runValidation">
          {{ validating ? 'Checking…' : 'Run validation' }}
        </button>
      </div>
    </header>

    <p v-if="loading" class="qbank-state">Loading question banks…</p>
    <p v-else-if="error" class="qbank-state qbank-state--error" role="alert">{{ error }}</p>

    <template v-else>
      <div v-if="validation" class="qbank-validation" :class="validation.ok ? 'qbank-validation--ok' : 'qbank-validation--bad'">
        <strong>
          {{ validation.ok ? 'References and structure pass' : `${validation.errors} error(s) need review` }}
        </strong>
        <span>
          {{ validation.pathways }} pathways · {{ validation.questions }} questions ·
          reviewed {{ validation.reviewed_at || 'not recorded' }}
        </span>
        <span v-if="validation.warnings">{{ validation.warnings }} warning(s)</span>
      </div>

      <div class="qbank-layout">
        <nav class="qbank-list" aria-label="Certification pathways">
          <button
            v-for="pathway in pathways"
            :key="pathway.id"
            type="button"
            class="qbank-list__item"
            :class="{ 'qbank-list__item--active': selectedId === pathway.id }"
            :aria-current="selectedId === pathway.id ? 'true' : undefined"
            @click="selectPathway(pathway.id)"
          >
            <span class="qbank-list__name">{{ pathway.name }}</span>
            <span class="qbank-list__meta">{{ pathway.code }} · {{ pathway.question_count }} questions</span>
            <span class="qbank-list__tracks">{{ pathway.tracks.join(' · ') }}</span>
          </button>
        </nav>

        <div class="qbank-detail">
          <p v-if="detailLoading" class="qbank-state">Loading the bank…</p>
          <p v-else-if="detailError" class="qbank-state qbank-state--error" role="alert">{{ detailError }}</p>

          <template v-else-if="detail">
            <header class="qbank-detail__head">
              <div>
                <p class="qbank__eyebrow">{{ detail.code }}</p>
                <h3>{{ detail.name }}</h3>
                <p>
                  {{ detail.domains.length }} domains · {{ detail.questions.length }} questions.
                  Sample size per attempt: 3.
                </p>
              </div>
              <a :href="safeHttpUrl(detail.objectives_url)" target="_blank" rel="noopener noreferrer" class="btn btn--outline btn--xs">
                Public objectives
              </a>
            </header>

            <div class="qbank-domains">
              <span v-for="domain in detail.domains" :key="domain.id" class="qbank-domain">
                <b>{{ domain.id }}</b> {{ domain.name }}
                <template v-if="domain.weight"> · {{ domain.weight }}%</template>
              </span>
            </div>

            <div class="qbank-questions">
              <article v-for="question in detail.questions" :key="question.id" class="qbank-question">
                <div class="qbank-question__head">
                  <span class="qbank-question__id">{{ question.id }}</span>
                  <span class="qbank-question__domain">Domain {{ question.domain }}</span>
                  <span class="qbank-question__difficulty">{{ question.difficulty }}</span>
                </div>
                <h4>{{ question.prompt }}</h4>
                <ol class="qbank-options">
                  <li
                    v-for="(option, index) in question.options"
                    :key="option"
                    :class="{ 'qbank-option--correct': index === question.correct }"
                  >
                    <span class="qbank-option__marker">{{ index === question.correct ? 'Correct' : '—' }}</span>
                    {{ option }}
                  </li>
                </ol>
                <p class="qbank-question__explanation">{{ question.explanation }}</p>
                <p class="qbank-question__objective">
                  <span>Objective</span>{{ question.objective }}
                </p>
                <p class="qbank-question__reference">
                  <span>Reference</span>
                  <a :href="safeHttpUrl(question.reference.url)" target="_blank" rel="noopener noreferrer">
                    {{ question.reference.label || question.reference.url }}
                  </a>
                </p>
              </article>
            </div>
          </template>
        </div>
      </div>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'
import { safeHttpUrl } from '../utils/url'

const loading = ref(true)
const error = ref('')
const pathways = ref([])
const validation = ref(null)
const selectedId = ref('')
const detail = ref(null)
const detailLoading = ref(false)
const detailError = ref('')
const validating = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/admin/question-banks')
    pathways.value = response.data.pathways || []
    validation.value = response.data.validation || null
    if (pathways.value.length) {
      await selectPathway(pathways.value[0].id)
    }
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      'Could not load question banks. Administrator access is required.'
  } finally {
    loading.value = false
  }
}

async function selectPathway(pathwayId) {
  selectedId.value = pathwayId
  detailLoading.value = true
  detailError.value = ''
  detail.value = null
  try {
    const response = await axios.get(`/admin/question-banks/${pathwayId}`)
    detail.value = response.data
  } catch (e) {
    detailError.value = e.response?.data?.detail || 'Could not load this question bank.'
  } finally {
    detailLoading.value = false
  }
}

async function runValidation() {
  validating.value = true
  try {
    const response = await axios.post('/admin/question-banks/validate')
    validation.value = response.data
    if (detail.value) {
      detail.value.validation = response.data
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Validation failed.'
  } finally {
    validating.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.qbank {
  display: grid;
  gap: 0.8rem;
}

.qbank__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    radial-gradient(circle at 100% 0%, var(--accent-bg), transparent 55%),
    var(--bg-secondary);
}

.qbank__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--text-muted);
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.qbank__head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 750;
}

.qbank__intro {
  max-width: 60rem;
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.76rem;
  line-height: 1.5;
}

.qbank__actions {
  flex: 0 0 auto;
}

.qbank-state {
  margin: 0;
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.qbank-state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.qbank-validation {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.8rem;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  font-size: 0.68rem;
}

.qbank-validation--ok {
  border: 1px solid var(--success);
  background: var(--success-bg);
  color: var(--text-primary);
}

.qbank-validation--bad {
  border: 1px solid var(--danger);
  background: var(--danger-bg);
  color: var(--text-primary);
}

.qbank-validation span {
  color: var(--text-secondary);
}

.qbank-layout {
  display: grid;
  grid-template-columns: minmax(220px, 0.32fr) minmax(0, 1fr);
  gap: 0.7rem;
  align-items: start;
}

.qbank-list {
  display: grid;
  gap: 0.35rem;
}

.qbank-list__item {
  display: grid;
  gap: 0.1rem;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.qbank-list__item:hover {
  border-color: var(--accent);
}

.qbank-list__item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.qbank-list__item--active {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.qbank-list__name {
  color: var(--text-primary);
  font-size: 0.74rem;
  font-weight: 650;
}

.qbank-list__meta {
  color: var(--text-muted);
  font-size: 0.6rem;
}

.qbank-list__tracks {
  color: var(--text-muted);
  font-size: 0.56rem;
  line-height: 1.35;
}

.qbank-detail {
  min-width: 0;
}

.qbank-detail__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.7rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.qbank-detail__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 700;
}

.qbank-detail__head p {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.qbank-domains {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin: 0.55rem 0;
}

.qbank-domain {
  padding: 0.16rem 0.4rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.58rem;
}

.qbank-domain b {
  color: var(--accent-text);
}

.qbank-questions {
  display: grid;
  gap: 0.55rem;
}

.qbank-question {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.qbank-question__head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.6rem;
  color: var(--text-muted);
  font-size: 0.58rem;
}

.qbank-question__id {
  color: var(--accent-text);
  font-family: "JetBrains Mono", ui-monospace, monospace;
}

.qbank-question__difficulty {
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.qbank-question h4 {
  margin: 0.3rem 0 0.45rem;
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 650;
  line-height: 1.45;
}

.qbank-options {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.2rem;
}

.qbank-options li {
  display: flex;
  gap: 0.4rem;
  padding: 0.25rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.68rem;
  line-height: 1.4;
}

.qbank-option--correct {
  border-color: var(--success) !important;
  background: var(--success-bg);
  color: var(--text-primary) !important;
}

.qbank-option__marker {
  flex: 0 0 44px;
  color: var(--text-muted);
  font-size: 0.54rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.qbank-option--correct .qbank-option__marker {
  color: var(--success);
}

.qbank-question__explanation {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.68rem;
  line-height: 1.45;
}

.qbank-question__objective,
.qbank-question__reference {
  margin: 0.3rem 0 0;
  color: var(--text-muted);
  font-size: 0.6rem;
  line-height: 1.4;
}

.qbank-question__objective span,
.qbank-question__reference span {
  display: block;
  color: var(--text-muted);
  font-size: 0.54rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.qbank-question__reference a {
  color: var(--accent-text);
  overflow-wrap: anywhere;
}

@media (max-width: 900px) {
  .qbank-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .qbank-list {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
}

@media (max-width: 640px) {
  .qbank__head,
  .qbank-detail__head {
    flex-direction: column;
  }
}
</style>
