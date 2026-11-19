<template>
  <section class="career-check">
    <div v-if="loading" class="career-check__state" role="status">
      Loading the career-direction questions...
    </div>

    <div v-else-if="error" class="career-check__state career-check__state--error" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--secondary btn--sm" @click="load">
        Try again
      </button>
    </div>

    <template v-else-if="!result">
      <p class="career-check__intro">
        Eight short questions about how you like to work. This is a reflection
        tool, not a personality test and not a hiring decision. Your answers are
        used for this response only and are not stored.
      </p>

      <ol class="career-check__questions">
        <li v-for="(question, index) in questions" :key="question.id" class="career-check__question">
          <fieldset>
            <legend>
              <span class="career-check__number">{{ index + 1 }}</span>
              {{ question.prompt }}
            </legend>
            <label
              v-for="option in question.options"
              :key="option.index"
              class="career-check__option"
              :class="{ 'career-check__option--selected': answers[question.id] === option.index }"
            >
              <input
                v-model.number="answers[question.id]"
                type="radio"
                :name="question.id"
                :value="option.index"
              />
              <span>{{ option.label }}</span>
            </label>
          </fieldset>
        </li>
      </ol>

      <div class="career-check__actions">
        <span class="career-check__progress">{{ answeredCount }} of {{ questions.length }} answered</span>
        <button
          type="button"
          class="btn btn--primary"
          :disabled="answeredCount !== questions.length || submitting"
          @click="submit"
        >
          {{ submitting ? 'Scoring...' : 'See my direction' }}
        </button>
      </div>
      <p v-if="submitError" class="career-check__error" role="alert">{{ submitError }}</p>
    </template>

    <template v-else>
      <div class="career-check__result-head">
        <div>
          <p class="career-check__eyebrow">Your current pattern</p>
          <h4>{{ strongestLabel }}</h4>
          <p class="career-check__note">{{ result.note }}</p>
        </div>
        <button type="button" class="btn btn--secondary btn--sm" @click="reset">
          Start over
        </button>
      </div>

      <div class="career-check__scores">
        <div v-for="row in result.scores" :key="row.id" class="career-check__score">
          <div class="career-check__score-head">
            <span>{{ row.label }}</span>
            <strong>{{ row.score }}%</strong>
          </div>
          <div
            class="career-check__bar"
            role="progressbar"
            :aria-valuenow="row.score"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`${row.label} match`"
          >
            <span :style="{ width: `${row.score}%` }"></span>
          </div>
          <p>{{ row.description }}</p>
        </div>
      </div>

      <div class="career-check__directions">
        <h5>Directions to explore</h5>
        <ul>
          <li v-for="direction in result.scores[0]?.directions || []" :key="direction">
            {{ direction }}
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const questions = ref([])
const answers = reactive({})
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const submitError = ref('')
const result = ref(null)

const answeredCount = computed(
  () => questions.value.filter((question) => answers[question.id] !== undefined).length,
)
const strongestLabel = computed(() => result.value?.scores?.[0]?.label || 'Your direction')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get('/profile/career-assessment')
    questions.value = data.questions || []
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the questions.'
  } finally {
    loading.value = false
  }
}

async function submit() {
  submitError.value = ''
  submitting.value = true
  try {
    const { data } = await axios.post('/profile/career-assessment', { answers: { ...answers } })
    result.value = data
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Could not score the answers.'
  } finally {
    submitting.value = false
  }
}

function reset() {
  result.value = null
  submitError.value = ''
  Object.keys(answers).forEach((key) => delete answers[key])
}

onMounted(load)
</script>

<style scoped>
.career-check {
  display: grid;
  gap: 1rem;
}

.career-check__state {
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  background: var(--bg-primary);
}

.career-check__state--error {
  border-color: var(--danger);
  color: var(--danger);
}

.career-check__intro,
.career-check__note {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.6;
}

.career-check__questions {
  display: grid;
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.career-check__question {
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.career-check__question fieldset {
  margin: 0;
  padding: 0;
  border: 0;
}

.career-check__question legend {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
  color: var(--text-primary);
  font-weight: 600;
  line-height: 1.45;
}

.career-check__number {
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  width: 1.35rem;
  height: 1.35rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent-text);
  font-size: 0.7rem;
}

.career-check__option {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  padding: 0.45rem 0.5rem;
  border-radius: 7px;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.45;
  cursor: pointer;
  transition: background-color 140ms ease, color 140ms ease;
}

.career-check__option:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.career-check__option--selected {
  background: var(--accent-bg);
  color: var(--text-primary);
}

.career-check__option input {
  margin-top: 0.15rem;
  accent-color: var(--accent);
}

.career-check__actions,
.career-check__result-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.career-check__progress {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.career-check__error {
  margin: 0;
  color: var(--danger);
  font-size: 0.78rem;
}

.career-check__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent-text);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.career-check__result-head h4 {
  margin: 0 0 0.35rem;
  color: var(--text-primary);
  font-size: 1.05rem;
}

.career-check__scores {
  display: grid;
  gap: 0.75rem;
}

.career-check__score {
  display: grid;
  gap: 0.35rem;
}

.career-check__score-head {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  color: var(--text-primary);
  font-size: 0.8rem;
}

.career-check__score p {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.5;
}

.career-check__bar {
  height: 6px;
  border-radius: 999px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.career-check__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent), var(--purple));
}

.career-check__directions {
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.career-check__directions h5 {
  margin: 0 0 0.4rem;
  color: var(--text-primary);
  font-size: 0.82rem;
}

.career-check__directions ul {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--text-secondary);
  font-size: 0.78rem;
  line-height: 1.6;
}

@media (prefers-reduced-motion: reduce) {
  .career-check__option {
    transition: none;
  }
}
</style>
