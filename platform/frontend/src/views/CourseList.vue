<template>
  <div class="courses-page">
    <div class="courses-container">
      <!-- Header -->
      <div class="courses-header">
        <div>
          <p class="header-eyebrow">Academy</p>
          <h1>{{ isStaff ? 'Programme progress' : 'Course workspace' }}</h1>
          <p class="header-subtitle">
            {{ isStaff
              ? 'Semester goals, course health, and the next action'
              : 'Your courses, content, and feedback in one place' }}
          </p>
        </div>
      </div>

      <ProgrammeOverview v-if="isStaff && !loading" :courses="courses" />

      <!-- Student workspace summary -->
      <div v-if="!isStaff && courses.length" class="workspace-summary">
        <div class="workspace-summary__stat">
          <strong>{{ activeCourses }}</strong>
          <span>active {{ activeCourses === 1 ? 'course' : 'courses' }}</span>
        </div>
        <div class="workspace-summary__stat">
          <strong>{{ totalLabs }}</strong>
          <span>assigned exercises</span>
        </div>
        <div class="workspace-summary__stat">
          <strong>{{ totalCompleted }}<span class="workspace-summary__of">/{{ totalLabs }}</span></strong>
          <span>exercises complete</span>
        </div>
        <div class="workspace-summary__stat">
          <strong>{{ totalStudents }}</strong>
          <span>classmates</span>
        </div>
        <p class="workspace-summary__note">
          Feedback is private. Open a course to see the aggregate and add your check-in.
        </p>
      </div>

      <!-- Join Course -->
      <div v-if="!isStaff" class="join-section">
        <div class="join-card">
          <h3>Join a Course</h3>
          <p>Enter the invite code provided by your instructor</p>
          <div class="join-form">
            <input
              v-model="inviteCode"
              type="text"
              placeholder="Enter invite code"
              class="join-input"
              aria-label="Course invite code"
              autocomplete="off"
              autocapitalize="characters"
              spellcheck="false"
              maxlength="64"
              @keyup.enter="joinCourse"
            />
            <button @click="joinCourse" :disabled="!inviteCode || joining" class="join-btn">
              {{ joining ? 'Joining...' : 'Join' }}
            </button>
          </div>
          <p v-if="joinMessage" :class="['join-message', joinError ? 'error' : 'success']">
            {{ joinMessage }}
          </p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading">Loading courses...</div>

      <!-- Empty state -->
      <div v-else-if="courses.length === 0" class="empty-state">
        <p v-if="isStaff">No courses are available yet. Create a course from the instructor workspace.</p>
        <p v-else>You are not enrolled in any courses. Enter an invite code above to join.</p>
      </div>

      <!-- Course Cards (student view) -->
      <template v-else>
        <div v-if="!isStaff" class="course-grid">
        <router-link
          v-for="course in courses"
          :key="course.id"
          :to="`/courses/${course.id}`"
          class="course-card"
          :aria-label="`Open ${course.name} workspace`"
        >
          <div class="course-card__header">
            <span class="course-code">{{ course.code }}</span>
            <span :class="['course-status', courseStatus(course).class]">
              {{ courseStatus(course).text }}
            </span>
          </div>
          <h3 class="course-name">{{ course.name }}</h3>
          <p class="course-semester">{{ course.semester }}</p>
          <p v-if="course.description" class="course-description">{{ course.description }}</p>
          <div v-if="course.level_label || course.difficulty || course.track_count" class="course-card__tags">
            <span v-if="course.level_label" class="course-tag course-tag--level">
              {{ course.level_label }}
            </span>
            <span
              v-if="course.difficulty"
              class="course-tag"
              :class="`course-tag--${course.difficulty}`"
            >
              {{ course.difficulty }}
            </span>
            <span
              v-if="course.track_count"
              class="course-tag course-tag--muted"
              :title="(course.track_names || []).join(', ')"
            >
              {{ trackLabel(course) }}
            </span>
          </div>
          <div class="course-card__stats">
            <span class="stat">{{ course.student_count }} students</span>
            <span class="stat">{{ course.lab_count }} exercises</span>
          </div>
          <div
            v-if="course.progress_percent != null"
            class="course-progress"
            role="progressbar"
            :aria-valuenow="course.progress_percent"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`${course.name} progress`"
          >
            <div class="course-progress__label">
              <span>Your progress</span>
              <strong>{{ course.completed_labs }}/{{ course.lab_count }} · {{ course.progress_percent }}%</strong>
            </div>
            <div class="course-progress__track">
              <span
                :class="{ 'course-progress__fill--complete': course.progress_percent === 100 }"
                :style="{ width: course.progress_percent + '%' }"
              ></span>
            </div>
          </div>
          <div class="course-card__action">
            Open workspace
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <line x1="5" y1="12" x2="19" y2="12"/>
              <polyline points="12 5 19 12 12 19"/>
            </svg>
          </div>
        </router-link>
      </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import axios from '../api/axios'
import ProgrammeOverview from '../components/ProgrammeOverview.vue'

const currentUser = ref({})
try {
  currentUser.value = JSON.parse(localStorage.getItem('user') || '{}')
} catch {
  currentUser.value = {}
}
const isStaff = computed(() => ['admin', 'instructor'].includes(currentUser.value.role))

const courses = ref([])
const loading = ref(true)
const inviteCode = ref('')
const joining = ref(false)
const joinMessage = ref('')
const joinError = ref(false)

const activeCourses = computed(
  () => courses.value.filter((course) => courseStatus(course).text === 'Active').length
)
const totalLabs = computed(
  () => courses.value.reduce((sum, course) => sum + (course.lab_count || 0), 0)
)
const totalCompleted = computed(
  () => courses.value.reduce((sum, course) => sum + (course.completed_labs || 0), 0)
)
const totalStudents = computed(
  () => courses.value.reduce((sum, course) => sum + (course.student_count || 0), 0)
)

function courseStatus(course) {
  const now = new Date()
  const end = new Date(course.end_date)
  const start = new Date(course.start_date)

  if (!course.is_active) return { text: 'Inactive', class: 'status-inactive' }
  if (now > end) return { text: 'Ended', class: 'status-ended' }
  if (now < start) return { text: 'Upcoming', class: 'status-upcoming' }
  return { text: 'Active', class: 'status-active' }
}

function trackLabel(course) {
  const names = course.track_names || []
  if (!names.length) return ''
  if (names.length <= 2) return names.join(' · ')
  return `${names.slice(0, 2).join(' · ')} +${names.length - 2}`
}

async function fetchCourses() {
  loading.value = true
  try {
    const res = await axios.get('/courses/')
    courses.value = res.data.courses
  } catch (e) {
    console.error('Failed to fetch courses', e)
  } finally {
    loading.value = false
  }
}

async function fetchMe() {
  try {
    const { data } = await axios.get('/auth/me')
    currentUser.value = data
  } catch {
    // Keep the localStorage role as a fallback.
  }
}

async function joinCourse() {
  const code = inviteCode.value.trim()
  if (!code) return
  joining.value = true
  joinMessage.value = ''
  try {
    const res = await axios.post('/courses/join', { invite_code: code })
    joinMessage.value = res.data.message
    joinError.value = false
    inviteCode.value = ''
    fetchCourses()
  } catch (e) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      joinMessage.value = detail.map((item) => item.msg || String(item)).join(' ')
    } else {
      joinMessage.value = detail || 'Failed to join course'
    }
    joinError.value = true
  } finally {
    joining.value = false
  }
}


onMounted(() => {
  fetchMe()
  fetchCourses()
})
</script>

<style scoped>
.courses-page {
  min-height: calc(100vh - 64px);
  background: var(--bg-primary);
  padding: 2rem 1.5rem;
}

.courses-container {
  max-width: 1100px;
  margin: 0 auto;
}

.courses-header {
  margin-bottom: 2rem;
}

.courses-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-subtitle {
  color: var(--text-secondary);
  margin-top: 0.25rem;
  font-size: 0.9rem;
}

.header-eyebrow {
  margin: 0 0 0.2rem;
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.workspace-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.5rem;
  margin-bottom: 1.5rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.workspace-summary__stat {
  display: grid;
  gap: 0.05rem;
  min-width: 90px;
}

.workspace-summary__stat strong {
  color: var(--text-primary);
  font-size: 1.35rem;
  line-height: 1.1;
}

.workspace-summary__stat span {
  color: var(--text-muted);
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.workspace-summary__note {
  flex: 1 1 240px;
  margin: 0;
  color: var(--text-muted);
  font-size: 0.75rem;
  line-height: 1.45;
}

/* Join Section */
.join-section {
  margin-bottom: 2rem;
}

.join-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
}

.join-card h3 {
  font-size: 1rem;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.join-card > p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.join-form {
  display: flex;
  gap: 0.75rem;
  max-width: 400px;
}

.join-input {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
}

.join-input:focus {
  border-color: var(--accent);
}

.join-btn {
  background: var(--accent);
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.join-btn:hover:not(:disabled) {
  background: #2563eb;
}

.join-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.join-message {
  margin-top: 0.75rem;
  font-size: 0.85rem;
}

.join-message.success {
  color: var(--success);
}

.join-message.error {
  color: var(--danger);
}


/* Loading & Empty */
.loading {
  color: var(--text-secondary);
  text-align: center;
  padding: 3rem;
}

.empty-state {
  color: var(--text-muted);
  text-align: center;
  padding: 3rem;
  font-size: 0.95rem;
}

/* Course Grid */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.25rem;
}

.course-card {
  display: flex;
  flex-direction: column;
  color: inherit;
  text-decoration: none;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.25rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.course-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}

.course-card:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.course-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.course-code {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-bg);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.course-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.status-active {
  color: var(--badge-green);
  background: rgba(34, 197, 94, 0.1);
}

.status-ended {
  color: var(--text-secondary);
  background: rgba(148, 163, 184, 0.1);
}

.status-upcoming {
  color: var(--warning);
  background: rgba(245, 158, 11, 0.1);
}

.status-inactive {
  color: var(--danger);
  background: var(--danger-bg);
}

.course-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.15rem;
}

.course-semester {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.course-description {
  font-size: 0.83rem;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.course-card__stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.course-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
}

.course-tag {
  max-width: 100%;
  padding: 0.14rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  color: var(--text-secondary);
  background: var(--bg-primary);
  font-size: 0.68rem;
  font-weight: 600;
  line-height: 1.4;
  overflow-wrap: anywhere;
  text-transform: capitalize;
}

.course-tag--level {
  border-color: color-mix(in srgb, var(--accent) 45%, transparent);
  color: var(--accent-text);
  background: var(--accent-bg);
}

.course-tag--beginner {
  border-color: color-mix(in srgb, var(--success) 45%, transparent);
  color: var(--success);
  background: var(--success-bg);
}

.course-tag--intermediate {
  border-color: color-mix(in srgb, var(--warning) 45%, transparent);
  color: var(--warning);
  background: var(--warning-bg);
}

.course-tag--advanced {
  border-color: color-mix(in srgb, var(--danger) 45%, transparent);
  color: var(--danger);
  background: var(--danger-bg);
}

.course-tag--muted {
  color: var(--text-muted);
}

.course-progress {
  margin: 0.15rem 0 0.6rem;
}

.course-progress__label {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
  font-size: 0.76rem;
  color: var(--text-secondary);
}

.course-progress__label strong {
  color: var(--text-primary);
  font-weight: 600;
}

.course-progress__track {
  height: 7px;
  border-radius: 999px;
  background: var(--bg-tertiary, rgba(148, 163, 184, 0.2));
  overflow: hidden;
}

.course-progress__track > span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
  transition: width 0.3s ease;
}

.course-progress__track > .course-progress__fill--complete {
  background: var(--success);
}

.workspace-summary__of {
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.8em;
}

.course-card__action {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-top: auto;
  padding-top: 0.35rem;
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 600;
}

.stat {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .course-grid {
    grid-template-columns: 1fr;
  }
}
</style>
