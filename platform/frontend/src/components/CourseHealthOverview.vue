<template>
  <section class="health" aria-labelledby="course-health-title">
    <header class="health-head">
      <div>
        <p class="health-eyebrow">{{ isInstructor ? 'Course health' : 'Your course' }}</p>
        <h2 id="course-health-title">
          {{ isInstructor ? 'How this course is landing' : course.name }}
        </h2>
        <p class="health-lead">
          <template v-if="isInstructor">
            A private organizational view of student satisfaction, instructor
            engagement, and the next action for this course.
          </template>
          <template v-else>
            Your progress, next exercise, and feedback in one place.
          </template>
        </p>
      </div>
      <span v-if="isInstructor && !loading && !error" class="health-status" :class="`health-status--${status}`">
        {{ statusLabel }}
      </span>
    </header>

    <div v-if="loading" class="health-state">Loading course health...</div>
    <div v-else-if="error" class="health-state health-state--error" role="alert">
      {{ error }}
    </div>

    <template v-else>
      <template v-if="isInstructor">
        <div class="health-metrics">
          <article class="health-metric health-metric--score">
            <span>Overall feedback</span>
            <strong>{{ scoreDisplay(summary?.aggregate?.overall_score) }}</strong>
            <small>{{ summary?.has_data ? 'Weighted, descriptive summary' : 'No data yet' }}</small>
          </article>
          <article class="health-metric">
            <span>Student satisfaction</span>
            <strong>{{ ratingDisplay(satisfaction) }}</strong>
            <small>{{ satisfactionSample }}</small>
          </article>
          <article class="health-metric">
            <span>Instructor engagement</span>
            <strong>{{ percentDisplay(coachingCoverage) }}</strong>
            <small>{{ summary?.instructor_coaching?.notes || 0 }} coaching notes</small>
          </article>
          <article class="health-metric">
            <span>Response rate</span>
            <strong>{{ percentDisplay(summary?.aggregate?.response_rate) }}</strong>
            <small>{{ summary?.aggregate?.respondents || 0 }} of {{ summary?.enrolled || 0 }} students</small>
          </article>
          <article class="health-metric">
            <span>Knowledge checks</span>
            <strong>{{ summary?.quizzes?.attempts || 0 }}</strong>
            <small>{{ percentDisplay(summary?.quizzes?.accuracy) }} average best score</small>
          </article>
        </div>

        <div class="health-grid">
          <section class="health-card">
            <header class="health-card__head">
              <div>
                <h3>What needs attention</h3>
                <p>Prioritized from this course's own feedback and engagement data.</p>
              </div>
            </header>
            <ul class="health-actions">
              <li v-for="(action, index) in actions" :key="index" :class="`health-action--${action.tone}`">
                <span>{{ action.text }}</span>
              </li>
            </ul>
            <button type="button" class="btn btn--secondary btn--sm" @click="$emit('open-feedback')">
              Open feedback workspace
            </button>
          </section>

          <section class="health-card">
            <header class="health-card__head">
              <div>
                <h3>Student voice</h3>
                <p>Anonymous comments from the course check-in and exercise pulse.</p>
              </div>
              <span class="health-card__count">{{ summary?.recent_comments?.length || 0 }}</span>
            </header>
            <ul v-if="recentComments.length" class="health-comments">
              <li v-for="(comment, index) in recentComments" :key="index">
                <p>{{ comment.comment }}</p>
                <span>{{ comment.source === 'exercise_pulse' ? 'Exercise pulse' : 'Course check-in' }}</span>
              </li>
            </ul>
            <p v-else class="health-muted">No written feedback yet.</p>
          </section>
        </div>

        <div class="health-context">
          <span><strong>{{ summary?.enrolled || course.student_count || 0 }}</strong> students</span>
          <span><strong>{{ course.lab_count || labs.length }}</strong> assigned exercises</span>
          <span v-if="course.instructor_name"><strong>{{ course.instructor_name }}</strong> instructor</span>
          <span v-if="course.semester"><strong>{{ course.semester }}</strong> term</span>
        </div>
      </template>

      <template v-else>
        <div class="health-grid">
          <section class="health-card health-card--progress">
            <header class="health-card__head">
              <div>
                <h3>Your progress</h3>
                <p>{{ completedLabs }} of {{ totalLabs }} assigned exercises complete.</p>
              </div>
              <strong class="health-progress__value">{{ progressPercent }}%</strong>
            </header>
            <div class="health-progress">
              <span :style="{ width: `${progressPercent}%` }"></span>
            </div>
            <template v-if="nextLab">
              <p class="health-next">
                <span>Next:</span> {{ nextLab.name }}
              </p>
              <button type="button" class="btn btn--primary btn--sm" @click="$emit('open-lab', nextLab)">
                Continue exercise
              </button>
            </template>
            <p v-else class="health-muted">Every assigned exercise is complete.</p>
          </section>

          <section class="health-card">
            <header class="health-card__head">
              <div>
                <h3>Your feedback</h3>
                <p>Optional. It helps the course team improve the next exercise.</p>
              </div>
            </header>
            <div v-if="summary?.my_survey_response" class="health-checkin">
              <strong>Check-in recorded</strong>
              <span>{{ formatDate(summary.my_survey_response.submitted_at) }}</span>
            </div>
            <div v-else-if="!summary?.survey_opt_in" class="health-checkin health-checkin--muted">
              <strong>Survey participation is off</strong>
              <span>Turn it on under Privacy and data to take the check-in.</span>
            </div>
            <div v-else class="health-checkin health-checkin--muted">
              <strong>No check-in yet</strong>
              <span>A one-minute check-in helps the course team.</span>
            </div>

            <template v-if="summary?.instructor_feedback_for_me?.length">
              <h4 class="health-subhead">From your instructor</h4>
              <article v-for="note in summary.instructor_feedback_for_me" :key="note.id" class="health-coaching">
                <p>{{ note.comment || 'Coaching note' }}</p>
                <span>{{ note.instructor }} · {{ formatDate(note.updated_at || note.created_at) }}</span>
              </article>
            </template>
            <button type="button" class="btn btn--secondary btn--sm" @click="$emit('open-feedback')">
              Open feedback
            </button>
          </section>
        </div>

        <div class="health-context">
          <span v-if="course.description">{{ course.description }}</span>
          <span v-if="course.instructor_name"><strong>{{ course.instructor_name }}</strong> instructor</span>
          <span v-if="course.semester"><strong>{{ course.semester }}</strong> term</span>
        </div>
      </template>
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  course: { type: Object, required: true },
  labs: { type: Array, default: () => [] },
  courseId: { type: [Number, String], required: true },
  isInstructor: { type: Boolean, default: false },
})

defineEmits(['open-feedback', 'open-lab'])

const summary = ref(null)
const loading = ref(true)
const error = ref('')

const completedLabs = computed(() => props.labs.filter((lab) => lab.is_completed).length)
const totalLabs = computed(() => props.labs.length)
const progressPercent = computed(() => (
  totalLabs.value ? Math.round((completedLabs.value / totalLabs.value) * 100) : 0
))
const nextLab = computed(
  () => props.labs.find((lab) => !lab.is_completed && !lab.locked) || null
)

const satisfaction = computed(() => {
  const quizzes = summary.value?.quizzes || {}
  const ratings = [
    quizzes.satisfaction,
    quizzes.relevance,
    quizzes.usefulness,
    quizzes.ease_of_use,
  ].filter((value) => value !== null && value !== undefined)
  if (ratings.length) {
    return ratings.reduce((sum, value) => sum + value, 0) / ratings.length
  }
  const clarity = summary.value?.course_checkin?.clarity
  return clarity === null || clarity === undefined ? null : clarity
})

const satisfactionSample = computed(() => {
  const count = summary.value?.quizzes?.feedback_responses || 0
  if (count) return `${count} experience rating${count === 1 ? '' : 's'}`
  if (summary.value?.course_checkin?.responses) {
    return `${summary.value.course_checkin.responses} course check-in${summary.value.course_checkin.responses === 1 ? '' : 's'}`
  }
  return 'No experience ratings yet'
})

const coachingCoverage = computed(() => {
  const enrolled = summary.value?.enrolled || 0
  const coached = summary.value?.instructor_coaching?.students_coached || 0
  return enrolled ? (coached / enrolled) * 100 : null
})

const recentComments = computed(() => {
  const seen = new Set()
  return (summary.value?.recent_comments || [])
    .filter((comment) => {
      const text = (comment.comment || '').trim()
      if (!text || seen.has(text)) return false
      seen.add(text)
      return true
    })
    .slice(0, 3)
})

const status = computed(() => {
  const data = summary.value
  if (!data?.has_data) return 'attention'
  if ((data.aggregate?.response_rate || 0) < 50) return 'attention'
  if (satisfaction.value !== null && satisfaction.value < 3.5) return 'attention'
  if (!data.instructor_coaching?.notes) return 'attention'
  if ((data.aggregate?.response_rate || 0) < 70) return 'watch'
  if ((coachingCoverage.value || 0) < 50) return 'watch'
  if (!data.quizzes?.attempts) return 'watch'
  return 'healthy'
})

const statusLabel = computed(() => ({
  healthy: 'Healthy',
  watch: 'Watch',
  attention: 'Needs attention',
}[status.value] || 'Watch'))

const actions = computed(() => {
  const data = summary.value
  const items = []
  if (!data?.has_data) {
    items.push({ tone: 'high', text: 'Start the feedback loop: invite students to complete the one-minute check-in.' })
  }
  if ((data?.aggregate?.response_rate || 0) < 50) {
    items.push({ tone: 'high', text: 'Response rate is below 50%; ask the cohort for a check-in before changing the course.' })
  }
  if (satisfaction.value !== null && satisfaction.value < 3.5) {
    items.push({ tone: 'high', text: 'Student satisfaction is below 3.5/5; review the recent comments and the next exercise.' })
  }
  if (!data?.instructor_coaching?.notes) {
    items.push({ tone: 'medium', text: 'No coaching notes yet; add one private note for a student this week.' })
  }
  if (!data?.quizzes?.attempts) {
    items.push({ tone: 'low', text: 'No knowledge checks yet; introduce one after the next exercise.' })
  }
  if (!items.length) {
    items.push({ tone: 'ok', text: 'No urgent action. Keep the feedback loop going and re-check after the next exercise.' })
  }
  return items
})

const scoreDisplay = (value) => (value === null || value === undefined ? '—' : `${Math.round(value)}`)
const ratingDisplay = (value) => (value === null || value === undefined ? '—' : `${value.toFixed(1)} / 5`)
const percentDisplay = (value) => (value === null || value === undefined ? '—' : `${Math.round(value)}%`)
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
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load course health.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.health { display: grid; gap: 1rem; }

.health-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}

.health-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.health-head h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(1.2rem, 2.5vw, 1.55rem);
}

.health-lead {
  margin: 0.3rem 0 0;
  max-width: 72ch;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.health-status {
  flex-shrink: 0;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.health-status--healthy { background: var(--success-bg); color: var(--success); }
.health-status--watch { background: var(--warning-bg); color: var(--warning); }
.health-status--attention { background: var(--danger-bg); color: var(--danger); }

.health-state { padding: 1rem; border: 1px solid var(--border-color); border-radius: 10px; color: var(--text-secondary); font-size: 0.85rem; }
.health-state--error { border-color: var(--danger); color: var(--danger); }

.health-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.65rem;
}

.health-metric {
  display: grid;
  gap: 0.2rem;
  padding: 0.8rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.health-metric--score { border-color: var(--accent); background: var(--accent-bg); }
.health-metric span { color: var(--text-muted); font-size: 0.66rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.health-metric strong { color: var(--text-primary); font-size: 1.35rem; line-height: 1.1; }
.health-metric small { color: var(--text-muted); font-size: 0.68rem; }

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 0.85rem;
  align-items: start;
}

.health-card {
  display: grid;
  gap: 0.65rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.health-card__head { display: flex; justify-content: space-between; gap: 0.75rem; align-items: flex-start; }
.health-card__head h3 { margin: 0; color: var(--text-primary); font-size: 0.95rem; }
.health-card__head p { margin: 0.2rem 0 0; color: var(--text-muted); font-size: 0.74rem; line-height: 1.45; }
.health-card__count { color: var(--text-muted); font-size: 0.72rem; }

.health-actions { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.45rem; }
.health-actions li { padding: 0.55rem 0.65rem; border-left: 3px solid var(--border-color); border-radius: 0 8px 8px 0; background: var(--bg-primary); color: var(--text-secondary); font-size: 0.79rem; line-height: 1.45; }
.health-action--high { border-left-color: var(--danger) !important; }
.health-action--medium { border-left-color: var(--warning) !important; }
.health-action--low { border-left-color: var(--accent) !important; }
.health-action--ok { border-left-color: var(--success) !important; }

.health-comments { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.45rem; }
.health-comments li { padding: 0.55rem 0.65rem; border-left: 2px solid var(--accent); border-radius: 0 8px 8px 0; background: var(--bg-primary); }
.health-comments p { margin: 0; color: var(--text-secondary); font-size: 0.79rem; line-height: 1.45; }
.health-comments span { color: var(--text-muted); font-size: 0.65rem; }

.health-context {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1.2rem;
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-muted);
  font-size: 0.74rem;
}
.health-context strong { color: var(--text-primary); }

.health-progress { height: 8px; border-radius: 999px; background: var(--bg-tertiary); overflow: hidden; }
.health-progress span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, var(--accent), var(--info, #38bdf8)); }
.health-progress__value { color: var(--text-primary); font-size: 1.1rem; }
.health-next { margin: 0; color: var(--text-secondary); font-size: 0.8rem; }
.health-next span { color: var(--text-muted); }

.health-checkin { display: grid; gap: 0.15rem; padding: 0.55rem 0.65rem; border-radius: 8px; background: var(--success-bg); border: 1px solid var(--success); }
.health-checkin strong { color: var(--text-primary); font-size: 0.8rem; }
.health-checkin span { color: var(--text-secondary); font-size: 0.72rem; }
.health-checkin--muted { background: var(--bg-primary); border-color: var(--border-color); }
.health-subhead { margin: 0.4rem 0 0; color: var(--text-primary); font-size: 0.78rem; }
.health-coaching { padding: 0.5rem 0.6rem; border-left: 2px solid var(--accent); background: var(--bg-primary); border-radius: 0 8px 8px 0; }
.health-coaching p { margin: 0; color: var(--text-secondary); font-size: 0.78rem; }
.health-coaching span { color: var(--text-muted); font-size: 0.65rem; }
.health-muted { margin: 0; color: var(--text-muted); font-size: 0.78rem; }

@media (max-width: 640px) {
  .health-head { flex-direction: column; }
  .health-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
