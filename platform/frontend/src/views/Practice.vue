<template>
  <div class="practice">
    <header class="practice__head">
      <p class="practice__eyebrow">Certification practice</p>
      <h1>Practice, not a certificate</h1>
      <p>
        Timed mock exams and domain drills over the reviewed bank. A pass here is
        a study signal, not a certification.
      </p>
    </header>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="message" class="practice__message" role="status">{{ message }}</p>
    <p v-if="loading" class="practice__muted">Loading practice...</p>

    <template v-else-if="session && session.session.status === 'active'">
      <section class="practice__run">
        <div class="practice__run-head">
          <div>
            <p class="practice__eyebrow">{{ session.session.mode === 'domain' ? 'Domain drill' : 'Mock exam' }}</p>
            <h2>{{ session.session.pathway_name }}</h2>
            <p class="practice__muted">
              {{ session.session.question_count }} questions · pass {{ session.session.pass_mark }}%
            </p>
          </div>
          <div class="practice__timer" :class="{ 'practice__timer--low': remaining <= 60 }">
            <span>Time left</span>
            <strong>{{ formattedTime }}</strong>
          </div>
        </div>

        <div class="practice__dots" role="group" aria-label="Jump to a question">
          <button
            v-for="question in session.questions"
            :key="question.position"
            type="button"
            class="practice__dot"
            :class="{
              'practice__dot--current': question.position === position,
              'practice__dot--answered': answers[question.position] !== undefined,
            }"
            :aria-label="`Question ${question.position}${answers[question.position] !== undefined ? ', answered' : ', not answered'}`"
            :aria-current="question.position === position ? 'true' : undefined"
            @click="goTo(question.position)"
          >
            {{ question.position }}
          </button>
        </div>

        <article v-if="current" class="practice__question">
          <div class="practice__question-head">
            <p class="practice__muted">
              Question {{ current.position }} of {{ session.questions.length }}
              <template v-if="current.domain_name"> · {{ current.domain_name }}</template>
            </p>
            <p class="practice__muted practice__answered-count">
              {{ answeredCount }} of {{ session.questions.length }} answered
            </p>
          </div>
          <h3>{{ current.prompt }}</h3>
          <ul class="practice__options">
            <li v-for="(option, index) in current.options" :key="index">
              <button
                type="button"
                class="practice__option"
                :class="{ 'practice__option--selected': answers[current.position] === index }"
                :aria-pressed="answers[current.position] === index"
                @click="answers[current.position] = index"
              >
                <span class="practice__label">{{ current.labels[index] }}</span>
                {{ option }}
              </button>
            </li>
          </ul>
        </article>

        <nav class="practice__nav" aria-label="Question navigation">
          <button
            type="button"
            class="btn btn--outline practice__nav-btn"
            :disabled="position <= 1"
            @click="goTo(position - 1)"
          >
            <span aria-hidden="true">←</span> Previous question
          </button>
          <p class="practice__nav-status" aria-live="polite">
            Question {{ position }} of {{ session.questions.length }}
          </p>
          <button
            type="button"
            class="btn btn--secondary practice__nav-btn practice__nav-btn--next"
            :disabled="position >= session.questions.length"
            @click="goTo(position + 1)"
          >
            Next question <span aria-hidden="true">→</span>
          </button>
        </nav>

        <p v-if="position >= session.questions.length" class="practice__last-hint">
          You are on the last question. Review your answers, then submit for final mark below.
        </p>

        <section class="practice__submit" aria-labelledby="practice-submit-title">
          <div class="practice__submit-copy">
            <h3 id="practice-submit-title">Finished answering?</h3>
            <p class="practice__muted">
              Submitting marks this attempt and shows your score and explanations. You cannot
              change your answers after it is submitted.
            </p>
            <p v-if="unansweredCount" class="practice__submit-warning">
              {{ unansweredCount }} question{{ unansweredCount === 1 ? '' : 's' }} still
              unanswered. Unanswered questions are marked incorrect.
            </p>
          </div>
          <div class="practice__submit-actions">
            <template v-if="!confirmingSubmit">
              <button
                type="button"
                class="btn btn--primary practice__submit-btn"
                :disabled="submitting"
                @click="confirmingSubmit = true"
              >
                Submit for final mark
              </button>
            </template>
            <template v-else>
              <p class="practice__submit-confirm" role="alert">
                Submit now and end this attempt?
              </p>
              <button
                type="button"
                class="btn btn--primary practice__submit-btn"
                :disabled="submitting"
                @click="submitSession"
              >
                {{ submitting ? 'Submitting...' : 'Yes, submit for final mark' }}
              </button>
              <button
                type="button"
                class="btn btn--outline practice__submit-btn"
                :disabled="submitting"
                @click="confirmingSubmit = false"
              >
                Keep working
              </button>
            </template>
          </div>
        </section>
      </section>
    </template>

    <template v-else-if="session">
      <section class="practice__result">
        <p class="practice__eyebrow">Attempt complete</p>
        <h2>{{ session.session.pathway_name }}</h2>
        <p class="practice__score" :class="{ 'practice__score--pass': session.session.passed }">
          {{ session.session.percentage }}%
        </p>
        <p>
          {{ session.session.score }} of {{ session.session.total }} correct ·
          {{ session.session.passed ? 'at or above the practice pass mark' : 'below the practice pass mark' }}
        </p>
        <p v-if="session.session.timed_out" class="practice__muted">
          The timer expired before submission; answered questions were still scored.
        </p>
        <button type="button" class="btn btn--primary btn--sm" @click="resetSession">
          Start another attempt
        </button>
      </section>

      <section class="practice__section">
        <h2>Review</h2>
        <ul class="practice__review">
          <li v-for="question in session.questions" :key="question.position" class="practice__review-card">
            <p class="practice__muted">
              Question {{ question.position }}
              <template v-if="question.domain_name"> · {{ question.domain_name }}</template>
            </p>
            <h3>{{ question.prompt }}</h3>
            <ul class="practice__review-options">
              <li
                v-for="(option, index) in question.options"
                :key="index"
                :class="{
                  'practice__correct': index === question.correct_index,
                  'practice__wrong':
                    index === question.selected_index && index !== question.correct_index,
                }"
              >
                <span class="practice__label">{{ question.labels[index] }}</span>
                {{ option }}
                <span v-if="index === question.correct_index" class="practice__tag">correct</span>
                <span v-else-if="index === question.selected_index" class="practice__tag">your answer</span>
              </li>
            </ul>
            <p v-if="question.explanation" class="practice__explanation">
              {{ question.explanation }}
            </p>
            <p v-if="question.reference" class="practice__muted">
              Reference:
              <a :href="question.reference.url" target="_blank" rel="noopener noreferrer">
                {{ question.reference.label || question.reference.url }}
              </a>
            </p>
          </li>
        </ul>
      </section>
    </template>

    <template v-else>
      <section v-if="progress && progress.pathways.length" class="practice__section">
        <h2>Your progress</h2>
        <ul class="practice__progress">
          <li v-for="row in progress.pathways" :key="row.pathway_id">
            <div>
              <strong>{{ row.pathway_name }}</strong>
              <p class="practice__muted">{{ row.attempts }} attempt{{ row.attempts === 1 ? '' : 's' }}</p>
            </div>
            <div class="practice__progress-score">
              <span>Best</span>
              <strong>{{ row.best_percentage }}%</strong>
            </div>
          </li>
        </ul>
        <div v-if="progress.domains.length">
          <h3>Domain accuracy</h3>
          <ul class="practice__domains">
            <li v-for="row in progress.domains" :key="`${row.pathway_id}-${row.domain_id}`">
              <span>{{ row.domain_name }}</span>
              <strong>{{ row.correct }}/{{ row.answered }} · {{ row.accuracy }}%</strong>
            </li>
          </ul>
        </div>
      </section>

      <section class="practice__section">
        <h2>Choose a pathway</h2>
        <ul class="practice__pathways">
          <li v-for="pathway in pathways" :key="pathway.id" class="practice__pathway">
            <div>
              <span class="practice__tag">{{ pathway.code }}</span>
              <h3>{{ pathway.name }}</h3>
              <p class="practice__muted">
                {{ pathway.question_count }} reviewed questions ·
                {{ pathway.exam.question_count }} in a mock ·
                {{ pathway.exam.duration_minutes }} minutes
              </p>
            </div>
            <div class="practice__pathway-actions">
              <button
                type="button"
                class="btn btn--primary btn--sm"
                :disabled="starting"
                @click="start(pathway, 'mock')"
              >
                Start mock
              </button>
              <label class="practice__domain-pick">
                <span class="practice__muted">Domain drill</span>
                <select v-model="domainChoice[pathway.id]" class="form-input">
                  <option value="">Choose a domain</option>
                  <option
                    v-for="domain in pathway.domain_list"
                    :key="domain.id"
                    :value="domain.id"
                    :disabled="!domain.question_count"
                  >
                    {{ domain.name }} ({{ domain.question_count }})
                  </option>
                </select>
              </label>
              <button
                type="button"
                class="btn btn--outline btn--sm"
                :disabled="starting || !domainChoice[pathway.id]"
                @click="start(pathway, 'domain')"
              >
                Drill domain
              </button>
            </div>
          </li>
        </ul>
      </section>

      <section v-if="history.length" class="practice__section">
        <h2>Recent attempts</h2>
        <ul class="practice__history">
          <li v-for="row in history" :key="row.id">
            <div>
              <strong>{{ row.pathway_name }}</strong>
              <p class="practice__muted">
                {{ row.mode }} · {{ formatDate(row.started_at) }}
              </p>
            </div>
            <div class="practice__progress-score">
              <strong v-if="row.status === 'submitted'">{{ row.percentage }}%</strong>
              <button
                v-else
                type="button"
                class="btn btn--outline btn--sm"
                @click="resume(row.id)"
              >
                Resume
              </button>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const pathways = ref([])
const progress = ref(null)
const history = ref([])
const session = ref(null)
const loading = ref(false)
const starting = ref(false)
const submitting = ref(false)
const confirmingSubmit = ref(false)
const error = ref('')
const message = ref('')
const position = ref(1)
const answers = reactive({})
const domainChoice = reactive({})
const remaining = ref(0)
let timer = null

const current = computed(() =>
  session.value?.questions.find((row) => row.position === position.value) || null
)

const answeredCount = computed(() => Object.keys(answers).length)
const unansweredCount = computed(() =>
  session.value ? Math.max(session.value.questions.length - answeredCount.value, 0) : 0
)

function goTo(nextPosition) {
  const total = session.value?.questions.length || 0
  if (nextPosition < 1 || nextPosition > total) return
  position.value = nextPosition
  confirmingSubmit.value = false
}

const formattedTime = computed(() => {
  const total = Math.max(remaining.value, 0)
  const minutes = Math.floor(total / 60)
  const seconds = total % 60
  return `${minutes}:${String(seconds).padStart(2, '0')}`
})

function formatDate(value) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const [pathwayResponse, progressResponse, historyResponse] = await Promise.all([
      axios.get('/practice/pathways'),
      axios.get('/practice/progress'),
      axios.get('/practice/sessions', { params: { limit: 10 } }),
    ])
    pathways.value = pathwayResponse.data.pathways || []
    progress.value = progressResponse.data
    history.value = historyResponse.data.sessions || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load practice.'
  } finally {
    loading.value = false
  }
}

function startTimer() {
  stopTimer()
  timer = setInterval(() => {
    if (!session.value) return
    const expires = new Date(session.value.session.expires_at).getTime()
    remaining.value = Math.max(Math.floor((expires - Date.now()) / 1000), 0)
    if (remaining.value === 0 && session.value.session.status === 'active') {
      stopTimer()
      submitSession()
    }
  }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function setSession(payload) {
  session.value = payload
  position.value = 1
  confirmingSubmit.value = false
  for (const key of Object.keys(answers)) delete answers[key]
  const expires = payload.session.expires_at
    ? new Date(payload.session.expires_at).getTime()
    : 0
  remaining.value = expires ? Math.max(Math.floor((expires - Date.now()) / 1000), 0) : 0
  if (payload.session.status === 'active') startTimer()
  else stopTimer()
}

async function start(pathway, mode) {
  starting.value = true
  error.value = ''
  message.value = ''
  try {
    const response = await axios.post('/practice/sessions', {
      pathway_id: pathway.id,
      mode,
      domain_id: mode === 'domain' ? domainChoice[pathway.id] : null,
      question_count: pathway.exam.question_count,
    })
    setSession(response.data)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not start practice.'
  } finally {
    starting.value = false
  }
}

async function resume(sessionId) {
  error.value = ''
  try {
    const response = await axios.get(`/practice/sessions/${sessionId}`)
    setSession(response.data)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not resume practice.'
  }
}

async function submitSession() {
  if (!session.value || submitting.value) return
  submitting.value = true
  confirmingSubmit.value = false
  error.value = ''
  try {
    const payload = session.value.questions
      .filter((row) => answers[row.position] !== undefined)
      .map((row) => ({
        position: row.position,
        selected_index: answers[row.position],
      }))
    const response = await axios.post(
      `/practice/sessions/${session.value.session.id}/submit`,
      { answers: payload }
    )
    setSession(response.data)
    message.value = 'Attempt scored. Review the explanations below.'
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not submit the attempt.'
  } finally {
    submitting.value = false
  }
}

function resetSession() {
  session.value = null
  message.value = ''
  loadDashboard()
}

onMounted(loadDashboard)
onBeforeUnmount(stopTimer)
</script>

<style scoped>
.practice {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1.25rem;
}

.practice__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.practice__head h1 {
  margin: 0 0 0.5rem;
}

.practice__head p {
  margin: 0;
  color: var(--text-muted);
}

.practice__muted {
  color: var(--text-muted);
  font-size: 0.88rem;
}

.practice__message {
  color: var(--success);
  background: var(--success-bg);
  border: 1px solid var(--success);
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.practice__run,
.practice__result,
.practice__section {
  border: 1px solid var(--border-color);
  border-radius: 0.9rem;
  background: var(--bg-secondary);
  padding: 1rem;
}

.practice__run-head,
.practice__progress li,
.practice__history li,
.practice__domains li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.practice__timer {
  text-align: right;
}

.practice__timer span {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.practice__timer strong {
  font-size: 1.5rem;
}

.practice__timer--low strong {
  color: var(--danger);
}

.practice__dots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0.8rem 0;
}

.practice__dot {
  min-width: 2.25rem;
  height: 2.25rem;
  padding: 0 0.35rem;
  border-radius: 0.4rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}

.practice__dot:hover {
  border-color: var(--accent);
}

.practice__dot:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.practice__dot--answered {
  background: var(--accent-bg);
  color: var(--text-primary);
}

.practice__dot--current {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
  color: var(--text-primary);
  font-weight: 700;
}

.practice__options,
.practice__review,
.practice__review-options,
.practice__pathways,
.practice__progress,
.practice__domains,
.practice__history {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.6rem;
}

.practice__option {
  width: 100%;
  text-align: left;
  border: 1px solid var(--border-color);
  border-radius: 0.6rem;
  background: var(--bg-secondary);
  padding: 0.7rem;
  cursor: pointer;
}

.practice__option--selected {
  border-color: var(--accent, #2563eb);
  background: var(--accent-bg);
}

.practice__label {
  display: inline-block;
  min-width: 1.4rem;
  font-weight: 700;
  color: var(--accent);
}

.practice__question-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.practice__answered-count {
  margin: 0;
  white-space: nowrap;
}

.practice__nav {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.practice__nav-btn {
  justify-self: start;
  min-height: 44px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.practice__nav-btn:focus-visible,
.practice__submit-btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.practice__nav-btn--next {
  justify-self: end;
  color: var(--text-primary);
}

.practice__nav-status {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

.practice__last-hint {
  margin: 0.65rem 0 0;
  padding: 0.55rem 0.75rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--accent-bg);
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.practice__submit {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--accent);
  border-radius: 0.75rem;
  background: var(--bg-primary);
}

.practice__submit h3 {
  margin: 0 0 0.2rem;
  font-size: 0.95rem;
}

.practice__submit-copy p {
  margin: 0;
}

.practice__submit-warning {
  margin-top: 0.35rem !important;
  color: var(--warning);
  font-size: 0.84rem;
}

.practice__submit-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.practice__submit-confirm {
  flex-basis: 100%;
  margin: 0 0 0.15rem;
  color: var(--text-primary);
  font-size: 0.84rem;
  font-weight: 600;
  text-align: right;
}

.practice__submit-btn {
  min-height: 44px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.practice__score {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0.2rem 0;
}

.practice__score--pass {
  color: var(--success);
}

.practice__review-card {
  border: 1px solid var(--border-color);
  border-radius: 0.8rem;
  padding: 0.9rem;
}

.practice__review-options li {
  border-radius: 0.4rem;
  padding: 0.35rem 0.5rem;
  border: 1px solid transparent;
}

.practice__correct {
  background: var(--success-bg);
  border-color: var(--success) !important;
}

.practice__wrong {
  background: var(--danger-bg);
  border-color: var(--danger) !important;
}

.practice__tag {
  display: inline-block;
  margin-left: 0.35rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.practice__explanation {
  margin: 0.5rem 0 0.2rem;
  line-height: 1.5;
}

.practice__pathway {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 0.8rem;
  padding: 0.9rem;
}

.practice__pathway h3 {
  margin: 0.25rem 0;
}

.practice__pathway-actions {
  display: grid;
  gap: 0.4rem;
  min-width: 220px;
}

.practice__domain-pick {
  display: grid;
  gap: 0.2rem;
}

.practice__progress li,
.practice__history li,
.practice__domains li {
  border-bottom: 1px solid var(--border-color);
  padding: 0.45rem 0;
}

.practice__progress-score {
  text-align: right;
}

@media (max-width: 720px) {
  .practice__pathway,
  .practice__run-head,
  .practice__submit {
    flex-direction: column;
    align-items: stretch;
  }

  .practice__submit-actions {
    justify-content: stretch;
  }

  .practice__submit-confirm {
    text-align: left;
  }
}

@media (max-width: 640px) {
  .practice__nav {
    grid-template-columns: 1fr 1fr;
  }

  .practice__nav-status {
    grid-column: 1 / -1;
    grid-row: 1;
  }

  .practice__nav-btn {
    width: 100%;
  }

  .practice__nav-btn--next {
    justify-self: stretch;
  }

  .practice__submit-btn {
    width: 100%;
  }
}
</style>
