<template>
  <div class="quiz-page">
    <div class="quiz-shell">
      <button type="button" class="back-link" @click="goBack">
        &larr; Back to the track
      </button>

      <div v-if="loading" class="quiz-state">Loading knowledge check...</div>
      <div v-else-if="error" class="quiz-state quiz-state--error" role="alert">
        {{ error }}
      </div>

      <template v-else-if="summary">
        <header class="quiz-head">
          <div>
            <p class="quiz-eyebrow">Optional knowledge check</p>
            <h1>{{ summary.lab.name }}</h1>
            <div class="quiz-chips">
              <span class="quiz-chip">Benchmark, not an exam item</span>
              <span v-if="summary.certification" class="quiz-chip quiz-chip--cert">
                {{ summary.certification.name }}
                <template v-if="summary.certification.code"> · {{ summary.certification.code }}</template>
              </span>
              <span v-if="summary.source === 'track'" class="quiz-chip quiz-chip--muted">General track benchmark</span>
              <span class="quiz-chip quiz-chip--muted">{{ summary.question_count }} question bank</span>
            </div>
          </div>
          <a
            v-if="safeHttpUrl(summary.certification?.url)"
            :href="safeHttpUrl(summary.certification.url)"
            target="_blank"
            rel="noopener noreferrer"
            class="cert-link"
          >
            Certification reference
          </a>
        </header>

        <section v-if="!summary.available" class="quiz-empty">
          <h2>No knowledge check yet</h2>
          <p>This exercise does not have a question bank yet. Use the workbook and lab hints for now.</p>
        </section>

        <template v-else>
          <section class="quiz-intro">
            <div>
              <h2>How to use this benchmark</h2>
              <p>{{ summary.benchmark_notice }}</p>
              <p v-if="summary.source === 'track'" class="quiz-muted">
                This is a general track benchmark, not a certification-specific bank. Use the
                workbook and the certification references for deeper study.
              </p>
              <p class="quiz-muted">
                Your score is not a grade and does not affect lab access, course completion, or
                certificates. It adds evidence to your Cyber DNA and helps the course team see
                whether the exercise is clear and useful.
              </p>
            </div>
            <div class="quiz-stats">
              <div>
                <strong>{{ summary.best_score === null ? '—' : `${summary.best_score}%` }}</strong>
                <span>best score</span>
              </div>
              <div>
                <strong>{{ summary.attempts }}</strong>
                <span>attempts</span>
              </div>
              <div>
                <strong>{{ summary.attempt_question_count }}</strong>
                <span>per attempt</span>
              </div>
            </div>
          </section>

          <section v-if="!attempt && !results" class="quiz-start">
            <h2>Ready when you are</h2>
            <p>
              Each attempt shows {{ summary.attempt_question_count }} questions drawn from the
              {{ summary.question_count }}-question bank. You can re-attempt as often as you like;
              the explanations and references appear after you submit.
            </p>
            <button class="btn btn--primary" :disabled="starting" @click="startAttempt">
              {{ starting ? 'Preparing...' : (summary.attempts ? 'Start another attempt' : 'Start knowledge check') }}
            </button>
            <p v-if="summary.completed" class="quiz-muted">
              You have completed the exercise. This check is optional; use it to confirm what you
              remember.
            </p>
            <p v-else class="quiz-muted">
              You can take this before or after the exercise. The benchmark is most useful after
              you have worked through the lab.
            </p>
          </section>

          <section v-if="attempt" class="quiz-attempt">
            <div class="quiz-attempt__head">
              <div>
                <p class="quiz-eyebrow">Attempt {{ summary.attempts + 1 }}</p>
                <h2>{{ attempt.question_count }} questions</h2>
              </div>
              <span class="quiz-progress">{{ answeredCount }} / {{ attempt.question_count }} answered</span>
            </div>

            <form @submit.prevent="submitAttempt">
              <fieldset
                v-for="(question, index) in attempt.questions"
                :key="question.id"
                class="quiz-question"
              >
                <legend>
                  <span class="quiz-question__number">Question {{ index + 1 }}</span>
                  {{ question.prompt }}
                </legend>
                <label
                  v-for="(option, optionIndex) in question.options"
                  :key="optionIndex"
                  class="quiz-option"
                  :class="{ 'quiz-option--selected': answers[question.id] === optionIndex }"
                >
                  <input
                    v-model.number="answers[question.id]"
                    type="radio"
                    :name="question.id"
                    :value="optionIndex"
                  />
                  <span>{{ option }}</span>
                </label>
              </fieldset>

              <div class="quiz-attempt__actions">
                <button class="btn btn--primary" type="submit" :disabled="submitting || !allAnswered">
                  {{ submitting ? 'Checking...' : 'Submit answers' }}
                </button>
                <button class="btn btn--ghost" type="button" :disabled="submitting" @click="cancelAttempt">
                  Cancel
                </button>
                <span v-if="submitError" class="quiz-error" role="alert">{{ submitError }}</span>
              </div>
            </form>
          </section>

          <section v-if="results" class="quiz-results">
            <div class="quiz-score" :class="results.passed ? 'quiz-score--pass' : 'quiz-score--practice'">
              <strong>{{ results.score }}%</strong>
              <div>
                <h2>{{ results.passed ? 'Benchmark met' : 'Good practice run' }}</h2>
                <p>
                  {{ results.correct }} of {{ results.total }} correct.
                  {{ results.passed ? 'You are above the 70% benchmark.' : 'Review the explanations and try another set.' }}
                </p>
              </div>
            </div>

            <article
              v-for="(result, index) in results.results"
              :key="result.id"
              class="quiz-result"
              :class="result.correct ? 'quiz-result--correct' : 'quiz-result--wrong'"
            >
              <header>
                <span class="quiz-result__badge">{{ result.correct ? 'Correct' : 'Review' }}</span>
                <h3>{{ index + 1 }}. {{ result.prompt }}</h3>
              </header>
              <p class="quiz-result__answer">
                <strong>Correct answer:</strong> {{ result.correct_option }}
              </p>
              <p v-if="!result.correct && result.selected !== null" class="quiz-result__selected">
                <strong>Your answer:</strong> {{ result.options[result.selected] }}
              </p>
              <p class="quiz-result__explanation">{{ result.explanation }}</p>
              <a
                v-if="safeHttpUrl(result.reference?.url)"
                :href="safeHttpUrl(result.reference.url)"
                target="_blank"
                rel="noopener noreferrer"
                class="quiz-result__reference"
              >
                {{ result.reference.label || 'Reference' }} ↗
              </a>
            </article>

            <div class="quiz-results__actions">
              <button class="btn btn--primary" :disabled="starting" @click="startAttempt">
                {{ starting ? 'Preparing...' : 'Try another set' }}
              </button>
              <button class="btn btn--ghost" type="button" @click="goBack">Back to the track</button>
            </div>

            <section class="quiz-feedback">
              <div>
                <h2>Was this check useful?</h2>
                <p class="quiz-muted">
                  Optional. These ratings feed the course experience report; they are not part of
                  your score.
                </p>
              </div>
              <form class="quiz-feedback__form" @submit.prevent="sendFeedback">
                <label v-for="field in feedbackFields" :key="field.key">
                  <span>{{ field.label }}</span>
                  <select v-model.number="feedback[field.key]">
                    <option :value="null">Not rated</option>
                    <option v-for="value in 5" :key="value" :value="value">{{ value }}</option>
                  </select>
                </label>
                <label class="quiz-feedback__comment">
                  <span>Anything else? (optional)</span>
                  <textarea v-model="feedback.comment" rows="2" maxlength="2000"></textarea>
                </label>
                <div class="quiz-feedback__actions">
                  <button class="btn btn--secondary btn--sm" type="submit" :disabled="feedbackSending">
                    {{ feedbackSending ? 'Sending...' : 'Send feedback' }}
                  </button>
                  <span v-if="feedbackSent" class="quiz-success" role="status">Thank you.</span>
                </div>
              </form>
            </section>
          </section>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { safeHttpUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()
const labSlug = computed(() => route.params.labSlug)
const trackSlug = computed(() => route.params.trackSlug)

const summary = ref(null)
const attempt = ref(null)
const results = ref(null)
const loading = ref(true)
const starting = ref(false)
const submitting = ref(false)
const error = ref('')
const submitError = ref('')
const answers = reactive({})
const feedbackSending = ref(false)
const feedbackSent = ref(false)
const feedback = reactive({
  satisfaction: null,
  relevance: null,
  usefulness: null,
  ease_of_use: null,
  comment: '',
})

const feedbackFields = [
  { key: 'satisfaction', label: 'Satisfaction' },
  { key: 'relevance', label: 'Relevance to the exercise' },
  { key: 'usefulness', label: 'Usefulness for your learning' },
  { key: 'ease_of_use', label: 'Ease of use' },
]

const answeredCount = computed(
  () => Object.values(answers).filter((value) => value !== null && value !== undefined).length
)
const allAnswered = computed(
  () => attempt.value && answeredCount.value === attempt.value.question_count
)

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get(`/exercises/labs/${labSlug.value}/quiz`)
    summary.value = data
    if (data.feedback) {
      for (const field of feedbackFields) {
        feedback[field.key] = data.feedback[field.key] ?? null
      }
      feedback.comment = data.feedback.comment || ''
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load this knowledge check.'
  } finally {
    loading.value = false
  }
}

const clearAnswers = () => {
  for (const key of Object.keys(answers)) delete answers[key]
}

const startAttempt = async () => {
  starting.value = true
  submitError.value = ''
  results.value = null
  feedbackSent.value = false
  try {
    const { data } = await axios.post(`/exercises/labs/${labSlug.value}/quiz/attempts`)
    clearAnswers()
    attempt.value = data
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Could not start an attempt.'
  } finally {
    starting.value = false
  }
}

const cancelAttempt = () => {
  attempt.value = null
  clearAnswers()
}

const submitAttempt = async () => {
  if (!attempt.value || !allAnswered.value) return
  submitting.value = true
  submitError.value = ''
  try {
    const { data } = await axios.post(
      `/exercises/labs/${labSlug.value}/quiz/attempts/${attempt.value.attempt_id}/submit`,
      { answers: { ...answers } }
    )
    results.value = data
    attempt.value = null
    await load()
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Could not submit this attempt.'
  } finally {
    submitting.value = false
  }
}

const sendFeedback = async () => {
  feedbackSending.value = true
  try {
    await axios.post(`/exercises/labs/${labSlug.value}/quiz/feedback`, { ...feedback })
    feedbackSent.value = true
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Could not send feedback.'
  } finally {
    feedbackSending.value = false
  }
}

const goBack = () => {
  router.push(`/exercises/${trackSlug.value}`)
}

onMounted(load)
</script>

<style scoped>
.quiz-page {
  min-height: calc(100vh - 64px);
  padding: 1.5rem 1rem 3rem;
  background: var(--bg-primary);
}

.quiz-shell {
  max-width: 880px;
  margin: 0 auto;
  display: grid;
  gap: 1rem;
}

.back-link {
  justify-self: start;
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.82rem;
  cursor: pointer;
  padding: 0;
}

.back-link:hover { color: var(--accent); }

.quiz-state {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

.quiz-state--error { color: var(--danger); }

.quiz-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.quiz-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.quiz-head h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.4rem, 3.5vw, 2rem);
}

.quiz-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }

.quiz-chip {
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 600;
}

.quiz-chip--cert { background: var(--accent-bg); color: var(--accent); }
.quiz-chip--muted { color: var(--text-muted); }

.cert-link {
  color: var(--accent);
  font-size: 0.75rem;
  white-space: nowrap;
}

.quiz-intro,
.quiz-start,
.quiz-attempt,
.quiz-results,
.quiz-empty {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.quiz-intro {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: start;
}

.quiz-intro h2,
.quiz-start h2,
.quiz-attempt h2,
.quiz-feedback h2 {
  margin: 0 0 0.35rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.quiz-intro p,
.quiz-start p,
.quiz-empty p,
.quiz-feedback p {
  margin: 0 0 0.5rem;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.quiz-muted { color: var(--text-muted) !important; font-size: 0.78rem !important; }

.quiz-stats { display: flex; gap: 0.9rem; }
.quiz-stats div { display: grid; gap: 0.05rem; min-width: 72px; }
.quiz-stats strong { color: var(--text-primary); font-size: 1.25rem; }
.quiz-stats span { color: var(--text-muted); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; }

.quiz-start { display: grid; gap: 0.5rem; justify-items: start; }

.quiz-attempt__head,
.quiz-results__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.quiz-progress { color: var(--text-muted); font-size: 0.75rem; }

.quiz-question {
  margin: 1rem 0 0;
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.quiz-question legend {
  padding: 0 0.25rem;
  color: var(--text-primary);
  font-size: 0.88rem;
  font-weight: 600;
  line-height: 1.45;
}

.quiz-question__number {
  display: block;
  margin-bottom: 0.15rem;
  color: var(--accent);
  font-size: 0.64rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.quiz-option {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
  margin-top: 0.4rem;
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.82rem;
  cursor: pointer;
}

.quiz-option input { margin-top: 0.15rem; accent-color: var(--accent); }
.quiz-option--selected { border-color: var(--accent); background: var(--accent-bg); color: var(--text-primary); }

.quiz-attempt__actions { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; margin-top: 1rem; }
.quiz-error { color: var(--danger); font-size: 0.78rem; }

.quiz-score {
  display: flex;
  gap: 0.9rem;
  align-items: center;
  padding: 0.9rem;
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.quiz-score--pass { border-color: var(--success); background: var(--success-bg); }
.quiz-score--practice { border-color: var(--warning); background: var(--warning-bg); }
.quiz-score > strong { font-size: 2rem; color: var(--text-primary); }
.quiz-score h2 { margin: 0; }
.quiz-score p { margin: 0; }

.quiz-result {
  margin-top: 0.65rem;
  padding: 0.8rem;
  border-left: 3px solid var(--border-color);
  border-radius: 0 8px 8px 0;
  background: var(--bg-primary);
}

.quiz-result--correct { border-left-color: var(--success); }
.quiz-result--wrong { border-left-color: var(--warning); }
.quiz-result header { display: flex; gap: 0.5rem; align-items: baseline; }
.quiz-result h3 { margin: 0; font-size: 0.85rem; color: var(--text-primary); }
.quiz-result__badge { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); }
.quiz-result--correct .quiz-result__badge { color: var(--success); }
.quiz-result--wrong .quiz-result__badge { color: var(--warning); }
.quiz-result__answer, .quiz-result__selected, .quiz-result__explanation {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.79rem;
  line-height: 1.5;
}
.quiz-result__explanation { color: var(--text-primary); }
.quiz-result__reference { display: inline-block; margin-top: 0.35rem; color: var(--accent); font-size: 0.75rem; }

.quiz-results__actions { margin-top: 0.9rem; }

.quiz-feedback {
  margin-top: 1rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border-color);
}

.quiz-feedback__form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.6rem;
  margin-top: 0.6rem;
}

.quiz-feedback__form label { display: grid; gap: 0.2rem; color: var(--text-secondary); font-size: 0.75rem; }
.quiz-feedback__form select,
.quiz-feedback__form textarea {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.8rem;
}
.quiz-feedback__comment { grid-column: 1 / -1; }
.quiz-feedback__actions { grid-column: 1 / -1; display: flex; gap: 0.6rem; align-items: center; }
.quiz-success { color: var(--success); font-size: 0.75rem; }

@media (max-width: 640px) {
  .quiz-head { flex-direction: column; }
  .quiz-intro { grid-template-columns: 1fr; }
  .quiz-stats { width: 100%; justify-content: space-between; }
}
</style>
