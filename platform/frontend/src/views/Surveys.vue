<template>
  <div class="surveys-page">
    <header class="surveys-head">
      <div>
        <p class="surveys-head__eyebrow">V2 feedback</p>
        <h1>Surveys</h1>
        <p>Create course surveys, attach them to courses, and review response history.</p>
      </div>
      <button type="button" class="btn btn--primary btn--sm" @click="showCreate = !showCreate">
        {{ showCreate ? 'Close builder' : 'Create survey' }}
      </button>
    </header>

    <p class="opt-in-note">
      Survey participation is opt-in. Learners who have not opted in under
      <strong>Privacy and data</strong> receive no survey prompt and cannot submit responses.
    </p>

    <section v-if="pulse" class="pulse-summary">
      <div>
        <span class="pulse-summary__label">Quick Pulse history</span>
        <strong>{{ pulse.totals?.pulse_responses || 0 }}</strong>
        <span>responses across your courses</span>
      </div>
      <div v-if="pulse.trending_topics?.length" class="pulse-summary__topics">
        <span v-for="topic in pulse.trending_topics" :key="topic.key">
          {{ topic.label }} <b>{{ topic.count }}</b>
        </span>
      </div>
    </section>

    <section v-if="showCreate" class="survey-builder">
      <h2>Create a survey</h2>
      <div class="builder-row">
        <label class="field">
          <span>Title</span>
          <input v-model="form.title" type="text" maxlength="150" placeholder="End-of-unit reflection" />
        </label>
        <label class="field">
          <span>Description</span>
          <input v-model="form.description" type="text" maxlength="2000" placeholder="Optional context for learners" />
        </label>
      </div>

      <div class="builder-questions">
        <article v-for="(question, index) in form.questions" :key="question.key" class="builder-question">
          <div class="builder-question__head">
            <strong>Question {{ index + 1 }}</strong>
            <button type="button" class="builder-remove" @click="removeQuestion(index)">Remove</button>
          </div>
          <div class="builder-row builder-row--question">
            <label class="field">
              <span>Prompt</span>
              <input v-model="question.prompt" type="text" maxlength="500" placeholder="What should learners reflect on?" />
            </label>
            <label class="field field--type">
              <span>Type</span>
              <select v-model="question.type">
                <option value="scale">Scale 1–5</option>
                <option value="choice">Multiple choice</option>
                <option value="text">Text</option>
              </select>
            </label>
          </div>
          <label v-if="question.type === 'choice'" class="field">
            <span>Options (comma-separated)</span>
            <input v-model="question.optionsText" type="text" placeholder="Yes, No, Unsure" />
          </label>
        </article>
      </div>

      <div class="builder-actions">
        <button type="button" class="btn btn--outline btn--sm" @click="addQuestion">+ Add question</button>
      </div>

      <div class="builder-attach">
        <span class="builder-attach__label">Attach to courses</span>
        <label v-for="course in courses" :key="course.id" class="builder-course">
          <input v-model="form.course_ids" type="checkbox" :value="course.id" />
          <span>{{ course.code }} — {{ course.name }}</span>
        </label>
      </div>

      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <div class="builder-footer">
        <button type="button" class="btn btn--primary btn--sm" :disabled="saving" @click="createSurvey">
          {{ saving ? 'Creating...' : 'Create survey' }}
        </button>
      </div>
    </section>

    <p v-if="loading" class="surveys-state">Loading surveys...</p>
    <div v-else-if="!surveys.length" class="surveys-state">No surveys yet.</div>
    <div v-else class="survey-list">
      <article v-for="survey in surveys" :key="survey.id" class="survey-card">
        <header class="survey-card__head">
          <div>
            <h2>{{ survey.title }}</h2>
            <p v-if="survey.description">{{ survey.description }}</p>
          </div>
          <span class="survey-card__count">{{ survey.response_count }} responses</span>
        </header>
        <div class="survey-card__meta">
          <span v-for="course in survey.courses" :key="course.id" class="survey-course">{{ course.code }}</span>
          <span>{{ survey.questions.length }} questions</span>
        </div>
        <button
          type="button"
          class="btn btn--outline btn--xs"
          @click="toggleResponses(survey.id)"
        >
          {{ openSurvey === survey.id ? 'Hide responses' : 'View responses' }}
        </button>

        <div v-if="openSurvey === survey.id" class="survey-responses">
          <p v-if="responsesLoading" class="surveys-state">Loading responses...</p>
          <template v-else-if="responseData">
            <div v-for="(summary, key) in responseData.summary" :key="key" class="response-summary">
              <strong>{{ summary.prompt }}</strong>
              <div v-if="summary.type === 'text'" class="response-texts">
                <p v-for="(text, i) in summary.texts" :key="i">{{ text }}</p>
                <span v-if="!summary.texts.length">No text responses yet.</span>
              </div>
              <div v-else class="response-counts">
                <span v-for="(count, value) in summary.counts" :key="value">{{ value }}: {{ count }}</span>
                <span v-if="!Object.keys(summary.counts).length">No responses yet.</span>
              </div>
            </div>
            <div v-if="responseData.responses.length" class="response-recent">
              <span class="response-recent__label">Recent submissions</span>
              <span v-for="response in responseData.responses.slice(0, 8)" :key="response.user_id">
                {{ response.display_name }} · {{ formatDate(response.submitted_at) }}
              </span>
            </div>
          </template>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'

const surveys = ref([])
const courses = ref([])
const pulse = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const showCreate = ref(false)
const openSurvey = ref(null)
const responseData = ref(null)
const responsesLoading = ref(false)

let questionKey = 0
const newQuestion = () => ({
  key: `q-${questionKey++}`,
  prompt: '',
  type: 'scale',
  optionsText: '',
})

const form = reactive({
  title: '',
  description: '',
  course_ids: [],
  questions: [newQuestion()],
})

const addQuestion = () => form.questions.push(newQuestion())
const removeQuestion = (index) => {
  if (form.questions.length > 1) form.questions.splice(index, 1)
}

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.course_ids = []
  form.questions = [newQuestion()]
  error.value = ''
}

const load = async () => {
  loading.value = true
  try {
    const [surveyRes, courseRes, pulseRes] = await Promise.all([
      axios.get('/analytics/surveys'),
      axios.get('/instructor/courses'),
      axios.get('/analytics/reports/overview'),
    ])
    surveys.value = surveyRes.data.surveys || []
    courses.value = courseRes.data || []
    pulse.value = pulseRes.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load surveys.'
  } finally {
    loading.value = false
  }
}

const createSurvey = async () => {
  error.value = ''
  if (!form.title.trim()) {
    error.value = 'Give the survey a title.'
    return
  }
  if (!form.course_ids.length) {
    error.value = 'Attach the survey to at least one course.'
    return
  }
  const questions = form.questions.map((question) => ({
    prompt: question.prompt.trim(),
    type: question.type,
    options: question.type === 'choice'
      ? question.optionsText.split(',').map((item) => item.trim()).filter(Boolean)
      : [],
  }))
  if (questions.some((question) => !question.prompt)) {
    error.value = 'Every question needs a prompt.'
    return
  }
  saving.value = true
  try {
    await axios.post('/analytics/surveys', {
      title: form.title.trim(),
      description: form.description.trim() || null,
      questions,
      course_ids: form.course_ids,
    })
    resetForm()
    showCreate.value = false
    await load()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not create the survey.'
  } finally {
    saving.value = false
  }
}

const toggleResponses = async (surveyId) => {
  if (openSurvey.value === surveyId) {
    openSurvey.value = null
    responseData.value = null
    return
  }
  openSurvey.value = surveyId
  responseData.value = null
  responsesLoading.value = true
  try {
    const { data } = await axios.get(`/analytics/surveys/${surveyId}/responses`)
    responseData.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load survey responses.'
  } finally {
    responsesLoading.value = false
  }
}

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

onMounted(load)
</script>

<style scoped>
.surveys-page {
  max-width: 1120px;
  margin: 0 auto;
  padding: 2rem;
}

.surveys-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.8rem;
}

.surveys-head__eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.surveys-head h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.7rem, 4vw, 2.3rem);
}

.surveys-head p:last-child {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.opt-in-note {
  margin: 0 0 1rem;
  padding: 0.65rem 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.72rem;
}

.pulse-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.pulse-summary > div:first-child {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.pulse-summary__label {
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.pulse-summary strong {
  color: var(--text-primary);
  font-size: 1.4rem;
}

.pulse-summary span {
  color: var(--text-muted);
  font-size: 0.7rem;
}

.pulse-summary__topics {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.pulse-summary__topics span {
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
}

.pulse-summary__topics b {
  color: var(--accent);
}

.survey-builder {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.survey-builder h2 {
  margin: 0 0 0.7rem;
  color: var(--text-primary);
  font-size: 1rem;
}

.builder-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.3fr);
  gap: 0.6rem;
}

.builder-row--question {
  grid-template-columns: minmax(0, 1fr) 150px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
  color: var(--text-secondary);
  font-size: 0.7rem;
  font-weight: 600;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
}

.builder-questions {
  display: grid;
  gap: 0.55rem;
  margin-top: 0.7rem;
}

.builder-question {
  padding: 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.builder-question__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.45rem;
  color: var(--text-primary);
  font-size: 0.7rem;
}

.builder-remove {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.62rem;
  text-decoration: underline;
  cursor: pointer;
}

.builder-actions {
  margin-top: 0.55rem;
}

.builder-attach {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  margin-top: 0.8rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border-color);
}

.builder-attach__label {
  width: 100%;
  color: var(--text-muted);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.builder-course {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.builder-footer {
  margin-top: 0.8rem;
}

.surveys-state {
  padding: 0.8rem;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.survey-list {
  display: grid;
  gap: 0.65rem;
}

.survey-card {
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.survey-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.survey-card h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.92rem;
}

.survey-card p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.7rem;
}

.survey-card__count {
  flex-shrink: 0;
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
}

.survey-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0.5rem 0;
  color: var(--text-muted);
  font-size: 0.62rem;
}

.survey-course {
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-weight: 700;
}

.survey-responses {
  margin-top: 0.7rem;
  padding-top: 0.7rem;
  border-top: 1px solid var(--border-color);
}

.response-summary {
  margin-bottom: 0.55rem;
}

.response-summary > strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.7rem;
}

.response-counts,
.response-texts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  margin-top: 0.25rem;
  color: var(--text-muted);
  font-size: 0.64rem;
}

.response-texts {
  flex-direction: column;
}

.response-texts p {
  margin: 0;
}

.response-recent {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 0.7rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.62rem;
}

.response-recent__label {
  color: var(--text-secondary);
  font-weight: 700;
}

@media (max-width: 720px) {
  .surveys-page { padding: 1rem; }
  .surveys-head { flex-direction: column; }
  .builder-row,
  .builder-row--question { grid-template-columns: 1fr; }
}
</style>
