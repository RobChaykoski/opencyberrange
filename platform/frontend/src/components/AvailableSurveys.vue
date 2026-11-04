<template>
  <section v-if="visible" class="available-surveys" aria-labelledby="available-surveys-title">
    <div class="available-surveys__head">
      <div>
        <h2 id="available-surveys-title">Course surveys</h2>
        <p v-if="optInRequired">
          Survey participation is off. Turn it on under
          <router-link to="/profile">Privacy and data</router-link> to take course surveys.
        </p>
        <p v-else>Short surveys from your instructors. Responses are used for course improvement.</p>
      </div>
      <span class="available-surveys__count">{{ surveys.length }}</span>
    </div>

    <p v-if="message" class="available-surveys__message" role="status">{{ message }}</p>
    <p v-if="error" class="available-surveys__error" role="alert">{{ error }}</p>

    <div v-if="surveys.length" class="available-survey-list">
      <article v-for="survey in surveys" :key="survey.id" class="available-survey">
        <header class="available-survey__head">
          <div>
            <h3>{{ survey.title }}</h3>
            <p v-if="survey.description">{{ survey.description }}</p>
            <span class="available-survey__course">{{ survey.course?.code }} · {{ survey.questions.length }} questions</span>
          </div>
          <button
            type="button"
            class="btn btn--outline btn--xs"
            @click="toggleSurvey(survey)"
          >
            {{ openId === survey.id ? 'Close' : 'Take survey' }}
          </button>
        </header>

        <form v-if="openId === survey.id" class="available-survey__form" @submit.prevent="submit(survey)">
          <div v-for="(question, index) in survey.questions" :key="index" class="available-question">
            <p class="available-question__prompt">{{ index + 1 }}. {{ question.prompt }}</p>
            <div v-if="question.type === 'scale'" class="available-scale">
              <button
                v-for="value in [1, 2, 3, 4, 5]"
                :key="value"
                type="button"
                class="available-scale__option"
                :class="{ 'available-scale__option--active': answers[survey.id]?.[index] === value }"
                @click="setAnswer(survey.id, index, value)"
              >
                {{ value }}
              </button>
              <span class="available-scale__hint">1 = low · 5 = high</span>
            </div>
            <select
              v-else-if="question.type === 'choice'"
              v-model="answers[survey.id][index]"
              class="available-input"
            >
              <option disabled value="">Choose an option</option>
              <option v-for="option in question.options" :key="option" :value="option">{{ option }}</option>
            </select>
            <textarea
              v-else
              v-model="answers[survey.id][index]"
              rows="3"
              maxlength="2000"
              class="available-input"
              placeholder="Your response"
            />
          </div>
          <div class="available-survey__actions">
            <button type="submit" class="btn btn--primary btn--sm" :disabled="savingId === survey.id">
              {{ savingId === survey.id ? 'Submitting...' : 'Submit survey' }}
            </button>
          </div>
        </form>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const surveys = ref([])
const optInRequired = ref(false)
const openId = ref(null)
const answers = reactive({})
const savingId = ref(null)
const message = ref('')
const error = ref('')

const visible = ref(false)

const load = async () => {
  try {
    const { data } = await axios.get('/analytics/surveys/available')
    optInRequired.value = data.reason === 'opt_in_required'
    surveys.value = data.surveys || []
    visible.value = optInRequired.value || surveys.value.length > 0
  } catch {
    visible.value = false
  }
}

const toggleSurvey = (survey) => {
  if (openId.value === survey.id) {
    openId.value = null
    return
  }
  openId.value = survey.id
  if (!answers[survey.id]) {
    answers[survey.id] = Object.fromEntries(
      survey.questions.map((_, index) => [index, ''])
    )
  }
}

const setAnswer = (surveyId, index, value) => {
  if (!answers[surveyId]) answers[surveyId] = {}
  answers[surveyId][index] = value
}

const submit = async (survey) => {
  savingId.value = survey.id
  error.value = ''
  message.value = ''
  const payload = {}
  for (const [index, value] of Object.entries(answers[survey.id] || {})) {
    if (value === '' || value === null || value === undefined) {
      error.value = 'Answer every question before submitting.'
      savingId.value = null
      return
    }
    payload[index] = value
  }
  try {
    await axios.post(`/analytics/surveys/${survey.id}/responses`, { answers: payload })
    surveys.value = surveys.value.filter((item) => item.id !== survey.id)
    openId.value = null
    message.value = 'Survey submitted. Thank you.'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not submit the survey.'
  } finally {
    savingId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.available-surveys {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.available-surveys__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.6rem;
}

.available-surveys h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
}

.available-surveys__head p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.available-surveys__count {
  display: grid;
  place-items: center;
  min-width: 28px;
  height: 28px;
  border-radius: 9px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.72rem;
  font-weight: 800;
}

.available-surveys__message {
  margin: 0 0 0.5rem;
  color: var(--success);
  font-size: 0.7rem;
}

.available-surveys__error {
  margin: 0 0 0.5rem;
  color: var(--danger);
  font-size: 0.7rem;
}

.available-survey-list {
  display: grid;
  gap: 0.55rem;
}

.available-survey {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.available-survey__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.available-survey h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.8rem;
}

.available-survey__head p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.available-survey__course {
  display: inline-block;
  margin-top: 0.2rem;
  color: var(--accent);
  font-size: 0.6rem;
  font-weight: 700;
}

.available-survey__form {
  margin-top: 0.7rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border-color);
}

.available-question + .available-question {
  margin-top: 0.65rem;
}

.available-question__prompt {
  margin: 0 0 0.3rem;
  color: var(--text-primary);
  font-size: 0.7rem;
  font-weight: 600;
}

.available-scale {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  flex-wrap: wrap;
}

.available-scale__option {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
}

.available-scale__option--active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent);
}

.available-scale__hint {
  color: var(--text-muted);
  font-size: 0.58rem;
}

.available-input {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.72rem;
}

.available-survey__actions {
  margin-top: 0.7rem;
}
</style>
