<template>
  <section class="feedback-panel" aria-labelledby="course-feedback-title">
    <header class="feedback-head">
      <div>
        <p class="feedback-eyebrow">Two-way feedback</p>
        <h2 id="course-feedback-title">Student experience and instructor coaching</h2>
        <p class="feedback-lead">
          A private, descriptive view of how the course is landing. It is not a
          public ranking. Student comments are aggregated; coaching notes are
          visible only to the instructor and the student they address.
        </p>
      </div>
      <button type="button" class="btn btn--ghost btn--sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </header>

    <div v-if="loading" class="feedback-state">Loading feedback...</div>
    <div v-else-if="error" class="feedback-state feedback-state--error" role="alert">
      {{ error }}
      <button type="button" class="btn btn--secondary btn--sm" @click="load">Try again</button>
    </div>

    <template v-else-if="summary">
      <div v-if="!summary.has_data" class="feedback-empty">
        <h3>Start the feedback loop</h3>
        <p>{{ summary.prompt }}</p>
      </div>

      <div class="feedback-metrics">
        <article class="feedback-metric feedback-metric--score">
          <span class="feedback-metric__label">Overall feedback</span>
          <strong class="feedback-metric__value">{{ displayScore(summary.aggregate.overall_score) }}</strong>
          <span class="feedback-metric__hint">Weighted from the data below</span>
        </article>
        <article class="feedback-metric">
          <span class="feedback-metric__label">Response rate</span>
          <strong class="feedback-metric__value">{{ displayPercent(summary.aggregate.response_rate) }}</strong>
          <span class="feedback-metric__hint">
            {{ summary.aggregate.respondents }} of {{ summary.aggregate.enrolled }} students
          </span>
        </article>
        <article class="feedback-metric">
          <span class="feedback-metric__label">Clarity</span>
          <strong class="feedback-metric__value">{{ displayRating(summary.aggregate.clarity) }}</strong>
          <span class="feedback-metric__hint">Course check-in average</span>
        </article>
        <article class="feedback-metric">
          <span class="feedback-metric__label">Challenge fit</span>
          <strong class="feedback-metric__value">{{ challengeFit }}</strong>
          <span class="feedback-metric__hint">
            Pulse difficulty {{ displayRating(summary.pulse.difficulty) }} / 5
          </span>
        </article>
        <article class="feedback-metric">
          <span class="feedback-metric__label">Engagement</span>
          <strong class="feedback-metric__value">{{ displayPercent(engagementPercent) }}</strong>
          <span class="feedback-metric__hint">
            {{ summary.reactions.likes }} likes · {{ summary.reactions.dislikes }} dislikes
          </span>
        </article>
        <article class="feedback-metric">
          <span class="feedback-metric__label">Instructor coaching</span>
          <strong class="feedback-metric__value">{{ summary.instructor_coaching.notes }}</strong>
          <span class="feedback-metric__hint">
            {{ summary.instructor_coaching.students_coached }} students coached
          </span>
        </article>
      </div>

      <div class="feedback-sources" aria-label="Feedback data sources">
        <span
          v-for="source in summary.aggregate.data_sources"
          :key="source"
          class="feedback-source"
        >
          {{ sourceLabel(source) }}
        </span>
        <span v-if="!summary.aggregate.data_sources.length" class="feedback-source feedback-source--muted">
          No data yet
        </span>
      </div>

      <div class="feedback-grid">
        <section class="feedback-card">
          <header class="feedback-card__head">
            <div>
              <h3>Student voice</h3>
              <p>Aggregated and anonymous. Comments are shown without names.</p>
            </div>
            <span class="feedback-card__count">{{ summary.course_checkin.responses }} check-ins</span>
          </header>

          <div class="feedback-bars">
            <div v-for="bar in ratingBars" :key="bar.key" class="feedback-bar">
              <div class="feedback-bar__head">
                <span>{{ bar.label }}</span>
                <strong>{{ displayRating(bar.value) }}</strong>
              </div>
              <div class="feedback-bar__track">
                <span :style="{ width: `${bar.value ? (bar.value / 5) * 100 : 0}%` }"></span>
              </div>
            </div>
          </div>

          <div class="feedback-split">
            <div class="feedback-split__item">
              <span class="feedback-split__label">Pulse responses</span>
              <strong>{{ summary.pulse.responses }}</strong>
              <small>{{ summary.pulse.unclear }} unclear notes</small>
            </div>
            <div class="feedback-split__item">
              <span class="feedback-split__label">Like ratio</span>
              <strong>{{ displayPercent(summary.reactions.like_ratio === null ? null : summary.reactions.like_ratio * 100) }}</strong>
              <small>{{ summary.reactions.likes + summary.reactions.dislikes }} reactions</small>
            </div>
          </div>

          <div v-if="summary.recent_comments?.length" class="feedback-comments">
            <h4>Recent comments</h4>
            <ul>
              <li v-for="(comment, index) in summary.recent_comments" :key="index">
                <p>{{ comment.comment }}</p>
                <span>{{ comment.anonymous_label }} · {{ sourceLabel(comment.source) }}</span>
              </li>
            </ul>
          </div>
          <p v-else class="feedback-muted">No written feedback yet.</p>
        </section>

        <section class="feedback-card">
          <header class="feedback-card__head">
            <div>
              <h3>{{ isInstructor ? 'Coaching and check-ins' : 'Your feedback' }}</h3>
              <p v-if="isInstructor">
                Add a private note for one student. Ratings are optional; a short
                comment is usually more useful.
              </p>
              <p v-else>
                Share a one-minute check-in. Your instructor sees the aggregate,
                not your name beside a comment.
              </p>
            </div>
          </header>

          <template v-if="isInstructor">
            <div v-if="summary.students?.length" class="coaching-list">
              <button
                v-for="student in summary.students"
                :key="student.user_id"
                type="button"
                class="coaching-student"
                :class="{ 'coaching-student--active': selectedStudent === student.user_id }"
                @click="selectStudent(student)"
              >
                <span class="coaching-student__name">{{ student.name }}</span>
                <span class="coaching-student__meta">
                  {{ student.completed_labs }}/{{ student.total_labs }} labs ·
                  {{ student.pulse_responses }} pulse
                </span>
                <span v-if="student.coaching" class="coaching-student__state">Coached</span>
                <span v-else class="coaching-student__state coaching-student__state--open">Open</span>
              </button>
            </div>
            <p v-else class="feedback-muted">No students are enrolled yet.</p>

            <p class="feedback-optin-note">
              {{ summary.survey_opt_in_count || 0 }} of {{ summary.enrolled }} students have opted in to surveys.
              <router-link to="/surveys">Manage the check-in survey</router-link>
            </p>

            <form v-if="summary.students?.length" class="feedback-form" @submit.prevent="submitCoaching">
              <fieldset class="feedback-form__ratings">
                <legend>Coaching ratings (optional)</legend>
                <label v-for="field in ratingFields" :key="`coach-${field.key}`">
                  <span>{{ field.label }}</span>
                  <select v-model.number="coaching[field.key]">
                    <option :value="null">Not rated</option>
                    <option v-for="value in 5" :key="value" :value="value">{{ value }}</option>
                  </select>
                </label>
              </fieldset>
              <label class="feedback-form__comment">
                <span>Coaching note</span>
                <textarea v-model="coaching.comment" rows="3" maxlength="2000" placeholder="What should this student try next?"></textarea>
              </label>
              <div class="feedback-form__actions">
                <button type="submit" class="btn btn--primary btn--sm" :disabled="saving">
                  {{ saving ? 'Saving...' : 'Save coaching note' }}
                </button>
                <span v-if="statusMessage" class="feedback-form__status" role="status">{{ statusMessage }}</span>
              </div>
            </form>
          </template>

          <template v-else>
            <div v-if="!summary.survey_opt_in" class="feedback-optin">
              <h4>Turn on survey participation</h4>
              <p>
                The course check-in uses the platform survey engine. Turn it on
                under
                <router-link to="/profile?tab=security">Privacy and data</router-link>
                to take the check-in. Your instructor still sees only aggregate
                results.
              </p>
            </div>
            <div v-else-if="summary.my_survey_response" class="feedback-checkin-done">
              <h4>Check-in recorded</h4>
              <p>Thank you. Your response is included in the course aggregate.</p>
              <span>{{ formatDate(summary.my_survey_response.submitted_at) }}</span>
            </div>

            <AvailableSurveys v-if="summary.survey_opt_in" :course-id="courseId" />

            <div v-if="summary.instructor_feedback_for_me?.length" class="feedback-coaching">
              <h4>From your instructor</h4>
              <article v-for="note in summary.instructor_feedback_for_me" :key="note.id">
                <p>{{ note.comment || 'Coaching note' }}</p>
                <span>{{ note.instructor }} · {{ formatDate(note.updated_at || note.created_at) }}</span>
              </article>
            </div>
            <p v-else class="feedback-muted">No instructor coaching notes yet.</p>
          </template>
        </section>

        <section v-if="summary.quizzes" class="feedback-card">
          <header class="feedback-card__head">
            <div>
              <h3>Knowledge checks</h3>
              <p>Optional benchmark practice. Scores are not grades; ratings feed course experience.</p>
            </div>
            <span class="feedback-card__count">{{ summary.quizzes.attempts }} attempts</span>
          </header>
          <div class="feedback-bars">
            <div v-for="bar in quizBars" :key="bar.key" class="feedback-bar">
              <div class="feedback-bar__head">
                <span>{{ bar.label }}</span>
                <strong>{{ displayRating(bar.value) }}</strong>
              </div>
              <div class="feedback-bar__track">
                <span :style="{ width: `${bar.value ? (bar.value / 5) * 100 : 0}%` }"></span>
              </div>
            </div>
          </div>
          <div class="feedback-split">
            <div class="feedback-split__item">
              <span class="feedback-split__label">Accuracy</span>
              <strong>{{ displayPercent(summary.quizzes.accuracy) }}</strong>
              <small>{{ summary.quizzes.labs }} exercises benchmarked</small>
            </div>
            <div class="feedback-split__item">
              <span class="feedback-split__label">Responses</span>
              <strong>{{ summary.quizzes.respondents }}</strong>
              <small>{{ summary.quizzes.feedback_responses }} experience ratings</small>
            </div>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import axios from '../api/axios'
import AvailableSurveys from './AvailableSurveys.vue'

const props = defineProps({
  courseId: { type: [Number, String], required: true },
  isInstructor: { type: Boolean, default: false },
})

const summary = ref(null)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const statusMessage = ref('')
const selectedStudent = ref(null)

const ratingFields = [
  { key: 'clarity', label: 'Clarity' },
  { key: 'challenge', label: 'Challenge' },
  { key: 'engagement', label: 'Engagement' },
  { key: 'confidence', label: 'Confidence' },
]

const coaching = reactive({
  clarity: null,
  challenge: null,
  engagement: null,
  confidence: null,
  comment: '',
})

const ratingBars = computed(() => ([
  { key: 'clarity', label: 'Clarity', value: summary.value?.course_checkin.clarity },
  { key: 'challenge', label: 'Challenge', value: summary.value?.course_checkin.challenge },
  { key: 'engagement', label: 'Engagement', value: summary.value?.course_checkin.engagement },
  { key: 'confidence', label: 'Confidence', value: summary.value?.course_checkin.confidence },
]))

const quizBars = computed(() => ([
  { key: 'satisfaction', label: 'Satisfaction', value: summary.value?.quizzes?.satisfaction },
  { key: 'relevance', label: 'Relevance', value: summary.value?.quizzes?.relevance },
  { key: 'usefulness', label: 'Usefulness', value: summary.value?.quizzes?.usefulness },
  { key: 'ease_of_use', label: 'Ease of use', value: summary.value?.quizzes?.ease_of_use },
]))

const challengeFit = computed(() => {
  const difficulty = summary.value?.pulse.difficulty
  if (difficulty === null || difficulty === undefined) return '—'
  return `${Math.round(Math.max(0, 100 - Math.abs(difficulty - 3) * 25))}%`
})

const engagementPercent = computed(() => {
  const reactions = summary.value?.reactions
  if (!reactions || reactions.like_ratio === null) return null
  return reactions.like_ratio * 100
})

const displayRating = (value) => (value === null || value === undefined ? '—' : `${value} / 5`)
const displayPercent = (value) => (value === null || value === undefined ? '—' : `${Math.round(value)}%`)
const displayScore = (value) => (value === null || value === undefined ? '—' : `${Math.round(value)}`)

const sourceLabel = (source) => ({
  course_checkin: 'Course check-in',
  exercise_pulse: 'Exercise pulse',
  exercise_reactions: 'Reactions',
  instructor_coaching: 'Instructor coaching',
  knowledge_checks: 'Knowledge checks',
}[source] || source)

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleDateString()
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get(`/courses/${props.courseId}/feedback/summary`)
    summary.value = data
    if (props.isInstructor && data.students?.length) {
      const first = data.students[0]
      selectStudent(first)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load feedback.'
  } finally {
    loading.value = false
  }
}

const selectStudent = (student) => {
  selectedStudent.value = student.user_id
  const note = student.coaching || {}
  for (const field of ratingFields) {
    coaching[field.key] = note[field.key] ?? null
  }
  coaching.comment = note.comment || ''
}

const flash = (message) => {
  statusMessage.value = message
  setTimeout(() => { statusMessage.value = '' }, 3500)
}

const submitCoaching = async () => {
  if (!selectedStudent.value) return
  saving.value = true
  try {
    await axios.post(`/courses/${props.courseId}/feedback`, {
      ...coaching,
      comment: coaching.comment || null,
      subject_user_id: selectedStudent.value,
    })
    flash('Coaching note saved.')
    await load()
  } catch (e) {
    flash(e.response?.data?.detail || 'Could not save the coaching note.')
  } finally {
    saving.value = false
  }
}

watch(() => props.courseId, load)
onMounted(load)
</script>

<style scoped>
.feedback-panel { display: grid; gap: 1rem; }
.feedback-head { display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }
.feedback-eyebrow { margin: 0 0 0.2rem; color: var(--accent); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
.feedback-head h2 { margin: 0; font-size: 1.25rem; color: var(--text-primary); }
.feedback-lead { margin: 0.35rem 0 0; max-width: 70ch; color: var(--text-secondary); font-size: 0.85rem; line-height: 1.55; }
.feedback-state { padding: 1.5rem; border: 1px solid var(--border-color); border-radius: 10px; color: var(--text-secondary); }
.feedback-state--error { border-color: var(--danger); color: var(--danger); display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }
.feedback-empty { padding: 1rem 1.1rem; border: 1px dashed var(--border-color); border-radius: 10px; background: var(--bg-secondary); }
.feedback-empty h3 { margin: 0 0 0.25rem; font-size: 0.95rem; color: var(--text-primary); }
.feedback-empty p { margin: 0; color: var(--text-secondary); font-size: 0.85rem; }
.feedback-optin, .feedback-checkin-done { padding: 0.65rem 0.75rem; border-radius: 8px; background: var(--bg-primary); border: 1px solid var(--border-color); }
.feedback-optin h4, .feedback-checkin-done h4 { margin: 0 0 0.25rem; color: var(--text-primary); font-size: 0.82rem; }
.feedback-optin p, .feedback-checkin-done p { margin: 0; color: var(--text-secondary); font-size: 0.78rem; line-height: 1.5; }
.feedback-optin a { color: var(--accent); }
.feedback-checkin-done { border-color: var(--success); background: var(--success-bg); }
.feedback-checkin-done span { color: var(--text-muted); font-size: 0.68rem; }
.feedback-optin-note { margin: 0; color: var(--text-muted); font-size: 0.72rem; }
.feedback-optin-note a { color: var(--accent); }
.feedback-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.65rem; }
.feedback-metric { display: grid; gap: 0.2rem; padding: 0.8rem 0.9rem; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-secondary); }
.feedback-metric--score { border-color: var(--accent); background: var(--accent-bg); }
.feedback-metric__label { color: var(--text-muted); font-size: 0.67rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }
.feedback-metric__value { color: var(--text-primary); font-size: 1.45rem; line-height: 1.1; }
.feedback-metric__hint { color: var(--text-muted); font-size: 0.7rem; }
.feedback-sources { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.feedback-source { padding: 0.15rem 0.5rem; border-radius: 999px; background: var(--bg-tertiary); color: var(--text-secondary); font-size: 0.68rem; font-weight: 600; }
.feedback-source--muted { color: var(--text-muted); }
.feedback-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.85rem; align-items: start; }
.feedback-card { padding: 1rem; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-secondary); display: grid; gap: 0.85rem; }
.feedback-card__head { display: flex; justify-content: space-between; gap: 0.75rem; align-items: flex-start; }
.feedback-card__head h3 { margin: 0; font-size: 1rem; color: var(--text-primary); }
.feedback-card__head p { margin: 0.2rem 0 0; color: var(--text-muted); font-size: 0.76rem; line-height: 1.45; }
.feedback-card__count { color: var(--text-muted); font-size: 0.72rem; white-space: nowrap; }
.feedback-bars { display: grid; gap: 0.55rem; }
.feedback-bar__head { display: flex; justify-content: space-between; color: var(--text-secondary); font-size: 0.78rem; }
.feedback-bar__head strong { color: var(--text-primary); }
.feedback-bar__track { height: 6px; border-radius: 999px; background: var(--bg-tertiary); overflow: hidden; margin-top: 0.2rem; }
.feedback-bar__track span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), var(--info, #38bdf8)); }
.feedback-split { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.feedback-split__item { padding: 0.55rem 0.65rem; border-radius: 8px; background: var(--bg-primary); display: grid; gap: 0.1rem; }
.feedback-split__label { color: var(--text-muted); font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.06em; }
.feedback-split__item strong { color: var(--text-primary); font-size: 1rem; }
.feedback-split__item small { color: var(--text-muted); font-size: 0.68rem; }
.feedback-comments h4, .feedback-coaching h4 { margin: 0 0 0.4rem; font-size: 0.8rem; color: var(--text-primary); }
.feedback-comments ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.5rem; }
.feedback-comments li { padding: 0.55rem 0.65rem; border-left: 2px solid var(--accent); background: var(--bg-primary); border-radius: 0 8px 8px 0; }
.feedback-comments p { margin: 0; color: var(--text-secondary); font-size: 0.8rem; line-height: 1.45; }
.feedback-comments span { color: var(--text-muted); font-size: 0.67rem; }
.feedback-muted { margin: 0; color: var(--text-muted); font-size: 0.8rem; }
.coaching-list { display: grid; gap: 0.35rem; max-height: 16rem; overflow-y: auto; }
.coaching-student { display: grid; grid-template-columns: minmax(0, 1fr) auto auto; gap: 0.5rem; align-items: center; padding: 0.5rem 0.6rem; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-primary); text-align: left; cursor: pointer; }
.coaching-student--active { border-color: var(--accent); background: var(--accent-bg); }
.coaching-student__name { font-size: 0.8rem; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.coaching-student__meta { color: var(--text-muted); font-size: 0.68rem; white-space: nowrap; }
.coaching-student__state { padding: 0.1rem 0.4rem; border-radius: 999px; background: var(--success-bg); color: var(--success); font-size: 0.62rem; font-weight: 700; text-transform: uppercase; }
.coaching-student__state--open { background: var(--warning-bg); color: var(--warning); }
.feedback-form { display: grid; gap: 0.7rem; }
.feedback-form__ratings { border: 0; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.5rem; }
.feedback-form__ratings legend { grid-column: 1 / -1; color: var(--text-muted); font-size: 0.68rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; padding: 0; }
.feedback-form__ratings label { display: grid; gap: 0.2rem; color: var(--text-secondary); font-size: 0.75rem; }
.feedback-form select, .feedback-form textarea { width: 100%; background: var(--bg-primary); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 7px; padding: 0.45rem 0.5rem; font: inherit; font-size: 0.8rem; }
.feedback-form textarea { resize: vertical; }
.feedback-form__comment { display: grid; gap: 0.2rem; color: var(--text-secondary); font-size: 0.75rem; }
.feedback-form__actions { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
.feedback-form__status { color: var(--success); font-size: 0.75rem; }
.feedback-coaching { display: grid; gap: 0.5rem; }
.feedback-coaching article { padding: 0.55rem 0.65rem; border-left: 2px solid var(--accent); background: var(--bg-primary); border-radius: 0 8px 8px 0; }
.feedback-coaching p { margin: 0; color: var(--text-secondary); font-size: 0.8rem; }
.feedback-coaching span { color: var(--text-muted); font-size: 0.67rem; }
@media (max-width: 640px) {
  .feedback-head { flex-direction: column; }
  .feedback-form__ratings { grid-template-columns: 1fr; }
  .feedback-split { grid-template-columns: 1fr; }
}
</style>
