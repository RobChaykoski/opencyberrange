<template>
  <div class="student-dashboard" :aria-busy="loading">
    <!-- New-achievement celebration -->
    <div v-if="celebrating && newAchievements.length" class="celebration" role="status" aria-live="polite">
      <div class="celebration__confetti" aria-hidden="true">
        <span
          v-for="piece in confetti"
          :key="piece.id"
          class="confetti-piece"
          :style="piece.style"
        ></span>
      </div>
      <div class="celebration__icon" aria-hidden="true">
        <TrophyIcon />
      </div>
      <div class="celebration__body">
        <p class="celebration__kicker">New achievement unlocked</p>
        <h2 class="celebration__title">{{ newAchievements[0].label }}</h2>
        <p class="celebration__text">
          {{ newAchievements[0].description || 'Your work just earned a new badge.' }}
        </p>
        <p v-if="newAchievements.length > 1" class="celebration__more">
          +{{ newAchievements.length - 1 }} more badge{{ newAchievements.length === 2 ? '' : 's' }}
        </p>
      </div>
      <div class="celebration__actions">
        <button type="button" class="btn btn--primary btn--sm" @click="celebrating = false">
          Nice
        </button>
        <router-link to="/profile" class="btn btn--outline btn--sm">View trophy case</router-link>
      </div>
    </div>

    <div v-if="error" class="error-card" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--outline btn--sm" @click="loadDashboard">Try again</button>
    </div>

    <!-- Hero -->
    <header class="hero">
      <div class="hero__main">
        <img src="/ocr-logo-dark.png" alt="" class="hero__logo" />
        <div class="hero__copy">
          <p class="hero__eyebrow">{{ greeting }}, welcome back</p>
          <h1 class="hero__title">{{ displayName }}</h1>
          <p class="hero__subtitle">{{ heroMessage }}</p>
          <div class="hero__pills">
            <span class="hero-pill">
              <TrophyIcon />
              {{ achievements.length }} {{ achievements.length === 1 ? 'badge' : 'badges' }}
            </span>
            <span class="hero-pill">
              <FlagIcon />
              {{ completedLabs }} {{ completedLabs === 1 ? 'lab' : 'labs' }} cleared
            </span>
            <span v-if="data.scoreboard_rank" class="hero-pill hero-pill--rank">
              <TrophyIcon />
              #{{ data.scoreboard_rank }}<template v-if="data.course_name"> in {{ data.course_name }}</template>
            </span>
            <span v-if="streak.current > 0" class="hero-pill hero-pill--streak">
              <FlameIcon />
              {{ streak.current }}-day streak
            </span>
            <span v-if="certificateCount > 0" class="hero-pill">
              <ShieldCheckIcon />
              {{ certificateCount }} {{ certificateCount === 1 ? 'certificate' : 'certificates' }}
            </span>
          </div>
        </div>
      </div>

      <div
        class="hero__ring"
        role="img"
        :aria-label="`${progressPercent} percent complete: ${completedLabs} of ${totalLabs} exercises`"
      >
        <svg viewBox="0 0 120 120" class="hero__ring-svg" aria-hidden="true">
          <circle class="hero__ring-track" cx="60" cy="60" r="52" />
          <circle
            class="hero__ring-fill"
            cx="60"
            cy="60"
            r="52"
            :stroke-dasharray="ringCircumference"
            :stroke-dashoffset="ringOffset"
          />
        </svg>
        <div class="hero__ring-label">
          <strong>{{ progressPercent }}%</strong>
          <span>{{ completedLabs }}/{{ totalLabs }} exercises</span>
        </div>
      </div>
    </header>

    <!-- Next objective, VPN, rank / milestone -->
    <div class="dashboard-grid">
      <div class="card card--objective">
        <div class="card__header">
          <span class="card__icon card__icon--blue"><TargetIcon /></span>
          <h2 class="card__title">Next objective</h2>
        </div>
        <div v-if="data.next_objective" class="objective-info">
          <span class="objective-track">{{ data.next_objective.track_name }} · {{ data.next_objective.level_name }}</span>
          <h3 class="objective-name">{{ data.next_objective.lab_name }}</h3>
          <router-link :to="resumeLink" class="btn btn--primary">
            Resume training
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="btn-icon">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </router-link>
        </div>
        <div v-else class="objective-complete">
          <span class="complete-bar"></span>
          <p>Every available exercise is complete. Nice work.</p>
        </div>
      </div>

      <div class="card card--vpn">
        <div class="card__header">
          <span class="card__icon card__icon--cyan"><ServerIcon /></span>
          <h2 class="card__title">VPN status</h2>
        </div>
        <div class="vpn-info">
          <div class="vpn-row">
            <span class="vpn-dot" :class="data.vpn_status?.vpn_registered ? 'vpn-dot--on' : 'vpn-dot--off'"></span>
            <span class="vpn-text">{{ data.vpn_status?.vpn_registered ? 'Registered' : 'Not configured' }}</span>
          </div>
          <span v-if="data.vpn_status?.client_ip" class="vpn-ip">{{ data.vpn_status.client_ip }}</span>
          <router-link to="/vpn-setup" class="btn btn--outline btn--sm">
            {{ data.vpn_status?.has_config ? 'Download config' : 'Set up VPN' }}
          </router-link>
        </div>
      </div>

      <div class="card card--milestone">
        <div class="card__header">
          <span class="card__icon card__icon--green"><FlameIcon /></span>
          <h2 class="card__title">Next milestone</h2>
        </div>
        <div class="milestone-info">
          <span class="milestone-number">{{ remainingToMilestone }}</span>
          <span class="milestone-label">{{ remainingToMilestone === 1 ? 'lab' : 'labs' }} to {{ nextMilestone }}</span>
          <div class="milestone-bar">
            <span :style="{ width: milestonePercent + '%' }"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Trophy case -->
    <section class="card card--trophy">
      <div class="card__header card__header--split">
        <div class="card__heading">
          <span class="card__icon card__icon--gold"><TrophyIcon /></span>
          <div>
            <h2 class="card__title">Trophy case</h2>
            <p class="card__subtitle">Badges you have earned across your courses</p>
          </div>
        </div>
        <router-link to="/profile" class="btn btn--outline btn--sm">Full record</router-link>
      </div>

      <div v-if="profileLoading" class="trophy-loading" aria-hidden="true">
        <span v-for="n in 5" :key="n" class="skeleton-medallion"></span>
      </div>
      <div v-else-if="achievements.length" class="trophy-grid">
        <AchievementMedallion
          v-for="achievement in recentAchievements"
          :key="achievement.id"
          :type="achievement.type"
          :label="achievement.label"
          :description="achievement.description"
          :date-label="formatAwardDate(achievement.awarded_at)"
        />
      </div>
      <div v-else class="empty-state">
        <TrophyIcon class="empty-state__icon" />
        <p class="empty-state__title">Your trophy case is ready for its first badge.</p>
        <p class="empty-state__hint">Capture a flag to start the collection.</p>
      </div>

      <div class="next-badges">
        <h3 class="next-badges__title">Next up</h3>
        <div v-for="badge in nextBadges" :key="badge.key" class="next-badge">
          <span class="next-badge__icon" :class="`next-badge__icon--${badge.tone}`">
            <component :is="badge.icon" />
          </span>
          <div class="next-badge__body">
            <div class="next-badge__row">
              <span class="next-badge__label">{{ badge.label }}</span>
              <span class="next-badge__count">{{ badge.current }}/{{ badge.target }}</span>
            </div>
            <div class="next-badge__bar">
              <span :style="{ width: badge.percent + '%' }"></span>
            </div>
            <p class="next-badge__desc">{{ badge.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Track progress + recent victories -->
    <div class="dashboard-grid dashboard-grid--two">
      <section class="card">
        <div class="card__header">
          <span class="card__icon card__icon--purple"><TargetIcon /></span>
          <h2 class="card__title">Track progress</h2>
        </div>
        <div v-if="tracks.length" class="track-list">
          <router-link
            v-for="track in tracks"
            :key="track.track_slug"
            :to="`/exercises/${track.track_slug}`"
            class="track-row"
          >
            <span class="track-row__icon">
              <component :is="trackIcon(track.track_slug)" />
            </span>
            <span class="track-row__body">
              <span class="track-row__top">
                <span class="track-row__name">{{ track.track_name }}</span>
                <span class="track-row__count">{{ track.completed_labs }}/{{ track.total_labs }}</span>
              </span>
              <span class="track-row__bar">
                <span :style="{ width: track.progress_percent + '%' }"></span>
              </span>
            </span>
            <span class="track-row__state" :class="{ 'track-row__state--done': track.is_complete }">
              {{ track.is_complete ? 'Complete' : `${track.total_labs - track.completed_labs} left` }}
            </span>
          </router-link>
        </div>
        <p v-else class="empty-state empty-state--compact">Start an exercise to see your track progress.</p>
      </section>

      <section class="card">
        <div class="card__header">
          <span class="card__icon card__icon--green"><CheckCircleIcon /></span>
          <h2 class="card__title">Recent victories</h2>
        </div>
        <ol v-if="recentCompletions.length" class="victory-list">
          <li v-for="item in recentCompletions" :key="item.lab_id" class="victory">
            <span class="victory__icon"><CheckCircleIcon /></span>
            <span class="victory__body">
              <span class="victory__name">{{ item.lab_name }}</span>
              <span class="victory__meta">{{ item.track_name }} · {{ dateLabel(item.completed_at) }}</span>
            </span>
            <span class="victory__tag">
              {{ item.hints_used ? `${item.hints_used} hint${item.hints_used === 1 ? '' : 's'}` : 'No hints' }}
            </span>
          </li>
        </ol>
        <p v-else class="empty-state empty-state--compact">Your first capture will show up here.</p>
      </section>
    </div>

    <!-- Completion matrix: courses x levels -->
    <div v-if="matrix.columns.length" class="card card--matrix">
      <div class="card__header">
        <span class="card__icon card__icon--purple">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <line x1="9" y1="3" x2="9" y2="21" />
            <line x1="15" y1="3" x2="15" y2="21" />
            <line x1="3" y1="9" x2="21" y2="9" />
            <line x1="3" y1="15" x2="21" y2="15" />
          </svg>
        </span>
        <div>
          <h2 class="card__title">Exercise completion matrix</h2>
          <p class="card__subtitle">Exercises completed per course and level</p>
        </div>
      </div>

      <div class="matrix-groups">
        <section v-for="group in matrixGroups" :key="group.key" class="matrix-group">
          <div class="matrix-group__head">
            <span class="matrix-group__label">{{ group.label }}</span>
          </div>
          <div class="matrix-scroll">
            <table class="matrix-table">
              <thead>
                <tr>
                  <th class="matrix-corner">Course</th>
                  <th v-for="col in group.columns" :key="col.key" class="matrix-col-head">
                    <span class="matrix-track">{{ col.track_name }}</span>
                    <span class="matrix-level">Level {{ col.level_number }} · {{ col.level_name }}</span>
                  </th>
                  <th v-if="group.isLast" class="matrix-col-head matrix-col-head--total">Total</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in matrix.rows" :key="row.course_id">
                  <th class="matrix-row-head">
                    <span class="matrix-course-code">{{ row.course_code }}</span>
                    <span class="matrix-course-name">{{ row.course_name }}</span>
                  </th>
                  <td
                    v-for="col in group.columns"
                    :key="col.key"
                    class="matrix-cell"
                    :class="cellClass(row.cells[col.key])"
                  >
                    <template v-if="row.cells[col.key] && row.cells[col.key].total">
                      {{ row.cells[col.key].completed }}/{{ row.cells[col.key].total }}
                    </template>
                    <span v-else class="matrix-empty">&ndash;</span>
                  </td>
                  <td v-if="group.isLast" class="matrix-cell matrix-cell--total">
                    {{ row.completed }}/{{ row.total }}
                  </td>
                </tr>
              </tbody>
              <tfoot v-if="matrix.rows.length > 1">
                <tr>
                  <th class="matrix-row-head">All courses</th>
                  <td
                    v-for="col in group.columns"
                    :key="col.key"
                    class="matrix-cell"
                    :class="cellClass(matrix.totals.cells[col.key])"
                  >
                    <template v-if="matrix.totals.cells[col.key] && matrix.totals.cells[col.key].total">
                      {{ matrix.totals.cells[col.key].completed }}/{{ matrix.totals.cells[col.key].total }}
                    </template>
                    <span v-else class="matrix-empty">&ndash;</span>
                  </td>
                  <td v-if="group.isLast" class="matrix-cell matrix-cell--total">
                    {{ matrix.totals.completed }}/{{ matrix.totals.total }}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </section>
      </div>

      <div class="matrix-legend">
        <span><i class="matrix-swatch matrix-swatch--complete"></i> Complete</span>
        <span><i class="matrix-swatch matrix-swatch--partial"></i> In progress</span>
        <span><i class="matrix-swatch matrix-swatch--empty"></i> Not started</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, markRaw, onMounted, ref } from 'vue'
import axios from '../api/axios'
import { getTrackIcon } from '../components/icons/trackIcons.js'
import AchievementMedallion from '../components/AchievementMedallion.vue'
import TargetIcon from '../components/icons/TargetIcon.vue'
import TrophyIcon from '../components/icons/TrophyIcon.vue'
import FlameIcon from '../components/icons/FlameIcon.vue'
import FlagIcon from '../components/icons/FlagIcon.vue'
import CheckCircleIcon from '../components/icons/CheckCircleIcon.vue'
import ShieldCheckIcon from '../components/icons/ShieldCheckIcon.vue'
import BrainIcon from '../components/icons/BrainIcon.vue'
import ServerIcon from '../components/icons/ServerIcon.vue'

const data = ref({
  next_objective: null,
  progress_percent: 0,
  total_labs: 0,
  completed_labs: 0,
  vpn_status: null,
  scoreboard_rank: null,
  course_name: null,
})

const profile = ref(null)
const loading = ref(true)
const profileLoading = ref(true)
const error = ref('')
const celebrating = ref(false)
const newAchievements = ref([])
const confetti = ref([])

const username = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user.username) return 'Student'
    return user.username.charAt(0).toUpperCase() + user.username.slice(1).toLowerCase()
  } catch {
    return 'Student'
  }
})

const displayName = computed(() => {
  const user = profile.value?.user
  return user?.display_name || user?.first_name || username.value
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const totals = computed(() => profile.value?.totals || {})

const achievements = computed(() => {
  const list = profile.value?.achievements || []
  return [...list].sort((a, b) => new Date(b.awarded_at || 0) - new Date(a.awarded_at || 0))
})

const recentAchievements = computed(() => achievements.value.slice(0, 6))
const certificates = computed(() => profile.value?.certificates || [])
const certificateCount = computed(() => totals.value.certificates ?? certificates.value.length)

const completions = computed(() => {
  const list = profile.value?.completions || []
  return [...list].sort((a, b) => new Date(b.completed_at || 0) - new Date(a.completed_at || 0))
})

const recentCompletions = computed(() => completions.value.slice(0, 5))

const tracks = computed(() => (profile.value?.tracks || []).filter((track) => track.total_labs > 0))

const completedLabs = computed(
  () => data.value.completed_labs ?? totals.value.labs_completed ?? 0
)

const totalLabs = computed(
  () => data.value.total_labs ?? totals.value.labs_total ?? 0
)

const progressPercent = computed(() => {
  const raw = data.value.progress_percent ?? totals.value.progress_percent ?? 0
  return Math.max(0, Math.min(100, Number(raw) || 0))
})

const noHintCount = computed(
  () => completions.value.filter((item) => (item.hints_used || 0) === 0).length
)

const perfectCount = computed(
  () => completions.value.filter((item) => (item.attempts || 0) === 1).length
)

const nearestTrack = computed(
  () =>
    tracks.value
      .filter((track) => !track.is_complete && track.total_labs > 0)
      .sort((a, b) => b.progress_percent - a.progress_percent)[0] || null
)

const nextMilestone = computed(() => {
  const value = completedLabs.value
  return Math.max(5, Math.ceil((value + 1) / 5) * 5)
})

const remainingToMilestone = computed(() =>
  Math.max(0, nextMilestone.value - completedLabs.value)
)

const milestoneStart = computed(() => Math.max(0, nextMilestone.value - 5))

const milestonePercent = computed(() => {
  const span = nextMilestone.value - milestoneStart.value
  if (!span) return 0
  return Math.min(
    100,
    Math.round(((completedLabs.value - milestoneStart.value) / span) * 100)
  )
})

const BADGE_ICONS = {
  brain: markRaw(BrainIcon),
  check: markRaw(CheckCircleIcon),
  shield: markRaw(ShieldCheckIcon),
}

const nextThreshold = (value) =>
  [1, 3, 5, 10, 20, 50].find((threshold) => value < threshold) ?? value + 10

const nextBadges = computed(() => {
  const rows = [
    {
      key: 'no_hints',
      label: 'Self-Reliant',
      description: 'Finish exercises without using hints.',
      current: noHintCount.value,
      target: nextThreshold(noHintCount.value),
      icon: BADGE_ICONS.brain,
      tone: 'green',
    },
    {
      key: 'perfectionist',
      label: 'Perfectionist',
      description: 'Capture a flag on your first attempt.',
      current: perfectCount.value,
      target: nextThreshold(perfectCount.value),
      icon: BADGE_ICONS.check,
      tone: 'amber',
    },
  ]

  const matrixRows = (data.value.completion_matrix?.rows || []).filter(
    (row) => row.total > 0
  )
  const nearestCourse = matrixRows
    .filter((row) => row.completed < row.total)
    .sort((a, b) => b.completed / b.total - a.completed / a.total)[0]

  if (nearestCourse) {
    rows.push({
      key: 'clean_sweep',
      label: 'Clean Sweep',
      description: `Finish every exercise in ${nearestCourse.course_code}.`,
      current: nearestCourse.completed,
      target: nearestCourse.total,
      icon: BADGE_ICONS.shield,
      tone: 'blue',
    })
  } else if (nearestTrack.value) {
    rows.push({
      key: 'level_complete',
      label: 'Level complete',
      description: `Finish every exercise in ${nearestTrack.value.track_name}.`,
      current: nearestTrack.value.completed_labs,
      target: nearestTrack.value.total_labs,
      icon: BADGE_ICONS.shield,
      tone: 'blue',
    })
  }

  return rows.map((row) => ({
    ...row,
    percent: row.target > 0 ? Math.min(100, Math.round((row.current / row.target) * 100)) : 0,
  }))
})

const streak = computed(() => {
  const keys = [
    ...new Set(
      completions.value
        .map((item) => {
          const date = new Date(item.completed_at)
          return Number.isNaN(date.getTime()) ? null : localDateKey(date)
        })
        .filter(Boolean)
    ),
  ].sort().reverse()

  if (!keys.length) return { current: 0, best: 0 }

  const todayKey = localDateKey(new Date())
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  const yesterdayKey = localDateKey(yesterday)

  let current = 0
  if (keys[0] === todayKey || keys[0] === yesterdayKey) {
    current = 1
    let cursor = new Date(`${keys[0]}T12:00:00`)
    for (let index = 1; index < keys.length; index += 1) {
      const expected = new Date(cursor)
      expected.setDate(expected.getDate() - 1)
      if (keys[index] === localDateKey(expected)) {
        current += 1
        cursor = expected
      } else {
        break
      }
    }
  }

  let best = 1
  let run = 1
  for (let index = 1; index < keys.length; index += 1) {
    const previous = new Date(`${keys[index - 1]}T12:00:00`)
    const expected = new Date(previous)
    expected.setDate(expected.getDate() - 1)
    if (keys[index] === localDateKey(expected)) {
      run += 1
      best = Math.max(best, run)
    } else {
      run = 1
    }
  }

  return { current, best: Math.max(best, current) }
})

const heroMessage = computed(() => {
  if (streak.value.current >= 3) {
    return `You are on a ${streak.value.current}-day streak. Keep the momentum going.`
  }
  if (achievements.value.length > 0) {
    return `You have earned ${achievements.value.length} badge${achievements.value.length === 1 ? '' : 's'}. There is another one waiting.`
  }
  if (completedLabs.value > 0) {
    return `You have cleared ${completedLabs.value} exercise${completedLabs.value === 1 ? '' : 's'}. The next one is ready.`
  }
  return 'Your first flag is the start of the story.'
})

const ringCircumference = 2 * Math.PI * 52

const ringOffset = computed(
  () => ringCircumference * (1 - progressPercent.value / 100)
)

const resumeLink = computed(() => {
  const objective = data.value.next_objective
  if (objective?.track_slug && objective?.lab_id) {
    return {
      path: `/exercises/${objective.track_slug}`,
      query: { labId: String(objective.lab_id) },
    }
  }
  return '/exercises'
})

const matrix = computed(
  () =>
    data.value.completion_matrix || {
      columns: [],
      rows: [],
      totals: { cells: {}, completed: 0, total: 0 },
    }
)

// Keep each matrix table easy to scan. More than four level columns become a
// second table below the first, with the course column repeated for context.
const MATRIX_COLUMNS_PER_GROUP = 4
const matrixGroups = computed(() => {
  const columns = matrix.value.columns
  if (!columns.length) return []

  const groups = []
  for (let start = 0; start < columns.length; start += MATRIX_COLUMNS_PER_GROUP) {
    const end = Math.min(start + MATRIX_COLUMNS_PER_GROUP, columns.length)
    groups.push({
      key: `matrix-${start}`,
      columns: columns.slice(start, end),
      label: `Levels ${start + 1}–${end} of ${columns.length}`,
      isLast: end >= columns.length,
    })
  }

  if (groups.length === 1) {
    groups[0].label = `All ${columns.length} ${columns.length === 1 ? 'level' : 'levels'}`
  }
  return groups
})

const cellClass = (cell) => {
  if (!cell || !cell.total) return 'matrix-cell--empty'
  if (cell.completed >= cell.total) return 'matrix-cell--complete'
  if (cell.completed > 0) return 'matrix-cell--partial'
  return 'matrix-cell--empty'
}

const trackIcon = (slug) => getTrackIcon(slug || '')

const localDateKey = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`

const dateLabel = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  const startOfToday = new Date()
  startOfToday.setHours(0, 0, 0, 0)
  const startOfDate = new Date(date)
  startOfDate.setHours(0, 0, 0, 0)
  const days = Math.floor((startOfToday - startOfDate) / 86400000)
  if (days <= 0) return 'Today'
  if (days === 1) return 'Yesterday'
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const formatAwardDate = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

const SEEN_ACHIEVEMENTS_KEY = 'ocr_seen_achievement_ids'
const CONFETTI_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#a78bfa', '#06b6d4', '#fb923c']

const makeConfetti = () =>
  Array.from({ length: 24 }, (_, index) => ({
    id: index,
    style: {
      left: `${(index * 37) % 100}%`,
      background: CONFETTI_COLORS[index % CONFETTI_COLORS.length],
      animationDelay: `${(index % 7) * 45}ms`,
      animationDuration: `${1200 + (index % 5) * 180}ms`,
    },
  }))

const detectNewAchievements = (list) => {
  const ids = list.map((item) => String(item.id)).filter(Boolean)
  let stored = null
  try {
    stored = localStorage.getItem(SEEN_ACHIEVEMENTS_KEY)
  } catch {
    stored = null
  }

  if (stored === null) {
    try {
      localStorage.setItem(SEEN_ACHIEVEMENTS_KEY, JSON.stringify(ids))
    } catch {
      // Storage can be unavailable in private mode; the dashboard still works.
    }
    return
  }

  let seen = []
  try {
    seen = JSON.parse(stored)
  } catch {
    seen = []
  }

  const seenIds = new Set(Array.isArray(seen) ? seen.map(String) : [])
  const fresh = list.filter((item) => !seenIds.has(String(item.id)))

  try {
    localStorage.setItem(SEEN_ACHIEVEMENTS_KEY, JSON.stringify(ids))
  } catch {
    // Ignore storage failures.
  }

  if (fresh.length) {
    newAchievements.value = fresh
    confetti.value = makeConfetti()
    celebrating.value = true
  }
}

const loadDashboard = async () => {
  loading.value = true
  profileLoading.value = true
  error.value = ''

  const [dashboardResult, profileResult] = await Promise.allSettled([
    axios.get('/dashboard/student'),
    axios.get('/profile/summary'),
  ])

  if (dashboardResult.status === 'fulfilled') {
    data.value = dashboardResult.value.data
  }
  if (profileResult.status === 'fulfilled') {
    profile.value = profileResult.value.data
    detectNewAchievements(profile.value.achievements || [])
  }

  if (dashboardResult.status === 'rejected' && profileResult.status === 'rejected') {
    error.value = 'We could not load your dashboard. Check your connection and try again.'
  }

  loading.value = false
  profileLoading.value = false
}

onMounted(loadDashboard)
</script>

<style scoped>
.student-dashboard {
  max-width: 1040px;
  margin: 0 auto;
  padding: 2rem;
}

/* Celebration banner */
.celebration {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  overflow: hidden;
  margin-bottom: 1.25rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--success);
  border-radius: 14px;
  background:
    radial-gradient(circle at 0% 0%, rgba(34, 197, 94, 0.2), transparent 50%),
    var(--bg-secondary);
}

.celebration__icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 50%;
  color: var(--warning);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  box-shadow: inset 0 0 0 1px var(--warning);
}

.celebration__icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.celebration__body {
  flex: 1;
  min-width: 0;
}

.celebration__kicker {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--success);
}

.celebration__title {
  margin: 0.1rem 0 0.15rem;
  font-size: 1.15rem;
  color: var(--text-primary);
}

.celebration__text {
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.celebration__more {
  margin: 0.25rem 0 0;
  font-size: 0.72rem;
  color: var(--warning);
}

.celebration__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  flex-shrink: 0;
}

.celebration__confetti {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.confetti-piece {
  position: absolute;
  top: -12px;
  width: 6px;
  height: 10px;
  border-radius: 2px;
  animation-name: celebration-fall;
  animation-timing-function: ease-out;
  animation-fill-mode: forwards;
}

@keyframes celebration-fall {
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  100% { transform: translateY(150px) rotate(420deg); opacity: 0; }
}

/* Hero */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 1.25rem;
  padding: 1.6rem;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background:
    radial-gradient(circle at 12% 12%, rgba(59, 130, 246, 0.24), transparent 45%),
    radial-gradient(circle at 88% 0%, rgba(34, 197, 94, 0.16), transparent 42%),
    var(--bg-secondary);
}

.hero__main {
  display: flex;
  align-items: center;
  gap: 1.15rem;
  min-width: 0;
}

.hero__logo {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  object-fit: contain;
  border-radius: 14px;
  padding: 5px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.hero__copy {
  min-width: 0;
}

.hero__eyebrow {
  margin: 0 0 0.15rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.hero__title {
  margin: 0;
  font-size: clamp(1.75rem, 4vw, 2.4rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.hero__subtitle {
  margin: 0.35rem 0 0.75rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.hero__pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.hero-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
}

.hero-pill :deep(svg) {
  width: 14px;
  height: 14px;
  color: var(--accent);
}

.hero-pill--streak :deep(svg) {
  color: #fb923c;
}

.hero-pill--rank :deep(svg) {
  color: var(--warning);
}

.hero__ring {
  position: relative;
  display: grid;
  place-items: center;
  width: 150px;
  height: 150px;
  flex-shrink: 0;
}

.hero__ring-svg {
  width: 150px;
  height: 150px;
  transform: rotate(-90deg);
}

.hero__ring-track,
.hero__ring-fill {
  fill: none;
  stroke-width: 9;
}

.hero__ring-track {
  stroke: var(--bg-tertiary);
}

.hero__ring-fill {
  stroke: var(--accent);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
  filter: drop-shadow(0 0 6px rgba(59, 130, 246, 0.45));
}

.hero__ring-label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
  text-align: center;
}

.hero__ring-label strong {
  font-size: 1.7rem;
  line-height: 1;
  color: var(--text-primary);
}

.hero__ring-label span {
  font-size: 0.66rem;
  color: var(--text-muted);
}

/* Layout */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.dashboard-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.35rem;
}

.card--objective {
  grid-column: span 2;
}

.card__header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 1rem;
}

.card__header--split {
  justify-content: space-between;
}

.card__heading {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.card__icon {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 8px;
  background: var(--bg-primary);
}

.card__icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.card__icon--blue { color: var(--accent); }
.card__icon--green { color: var(--success); }
.card__icon--cyan { color: #06b6d4; }
.card__icon--amber { color: var(--warning); }
.card__icon--gold { color: var(--warning); }
.card__icon--purple { color: #a78bfa; }

.card__title {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card__subtitle {
  margin: 0.1rem 0 0;
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Objective */
.objective-track {
  display: block;
  margin-bottom: 0.25rem;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.objective-name {
  margin: 0 0 1rem;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-primary);
}

.objective-complete {
  padding: 0.75rem 0;
  text-align: center;
}

.complete-bar {
  display: inline-block;
  width: 40px;
  height: 4px;
  margin-bottom: 0.5rem;
  border-radius: 2px;
  background: var(--success);
}

.objective-complete p {
  margin: 0;
  color: var(--text-secondary);
}

.btn-icon {
  width: 16px;
  height: 16px;
}

/* VPN */
.vpn-info {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.vpn-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.vpn-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.vpn-dot--on {
  background: var(--success);
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
}

.vpn-dot--off {
  background: var(--nav-label);
}

.vpn-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
}

.vpn-ip {
  font-family: monospace;
  font-size: 0.82rem;
  color: var(--accent);
}

/* Milestone */
.milestone-info {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: baseline;
  gap: 0.15rem 0.5rem;
}

.milestone-number {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
  color: var(--success);
}

.milestone-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.milestone-bar {
  grid-column: 1 / -1;
  height: 7px;
  margin-top: 0.5rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.milestone-bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--success));
  transition: width 0.6s ease;
}

/* Trophy case */
.card--trophy {
  margin-bottom: 1rem;
}

.trophy-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 1.25rem;
  padding: 0.35rem 0 0.5rem;
}

.trophy-loading {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 1.25rem;
  padding: 0.35rem 0 0.5rem;
}

.skeleton-medallion {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: var(--bg-tertiary);
  opacity: 0.6;
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.75; }
}

.next-badges {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.next-badges__title {
  margin: 0 0 0.7rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.next-badge {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.55rem 0;
}

.next-badge + .next-badge {
  border-top: 1px solid var(--border-color);
}

.next-badge__icon {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--accent);
}

.next-badge__icon--green { color: var(--success); }
.next-badge__icon--amber { color: var(--warning); }
.next-badge__icon--blue { color: var(--accent); }

.next-badge__icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.next-badge__body {
  flex: 1;
  min-width: 0;
}

.next-badge__row {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.78rem;
}

.next-badge__label {
  font-weight: 600;
  color: var(--text-primary);
}

.next-badge__count {
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.next-badge__bar {
  height: 5px;
  margin: 0.3rem 0 0.25rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.next-badge__bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: var(--accent);
  transition: width 0.6s ease;
}

.next-badge__desc {
  margin: 0;
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* Track progress */
.track-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.track-row {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 0.25rem;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: background 0.15s ease;
}

.track-row:hover {
  background: var(--bg-primary);
}

.track-row__icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--accent);
}

.track-row__icon :deep(svg) {
  width: 18px;
  height: 18px;
}

.track-row__body {
  flex: 1;
  min-width: 0;
}

.track-row__top {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.78rem;
}

.track-row__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--text-primary);
}

.track-row__count {
  flex-shrink: 0;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.track-row__bar {
  display: block;
  height: 5px;
  margin-top: 0.3rem;
  overflow: hidden;
  border-radius: 999px;
  background: var(--bg-tertiary);
}

.track-row__bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--success));
}

.track-row__state {
  flex-shrink: 0;
  font-size: 0.66rem;
  color: var(--text-muted);
}

.track-row__state--done {
  color: var(--success);
  font-weight: 600;
}

/* Recent victories */
.victory-list {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.victory {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.5rem 0;
}

.victory + .victory {
  border-top: 1px solid var(--border-color);
}

.victory__icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--success-bg);
  color: var(--success);
}

.victory__icon :deep(svg) {
  width: 15px;
  height: 15px;
}

.victory__body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.victory__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
}

.victory__meta {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.victory__tag {
  flex-shrink: 0;
  padding: 0.15rem 0.45rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  font-size: 0.64rem;
  color: var(--text-secondary);
}

/* Empty and error states */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 1.5rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state--compact {
  padding: 1rem;
}

.empty-state__icon {
  width: 34px;
  height: 34px;
  margin-bottom: 0.35rem;
  color: var(--text-muted);
}

.empty-state__title {
  margin: 0;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state__hint {
  margin: 0;
  font-size: 0.74rem;
  color: var(--text-muted);
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--danger);
  border-radius: 10px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.error-card p {
  margin: 0;
}

/* Completion matrix */
.card--matrix {
  margin-top: 0;
}

.matrix-groups {
  display: grid;
  gap: 1rem;
}

.matrix-group__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.4rem;
}

.matrix-group__label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.matrix-scroll {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 10px;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
  min-width: 560px;
}

.matrix-table th,
.matrix-table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--border-color);
  border-right: 1px solid var(--border-color);
  text-align: center;
  white-space: nowrap;
}

.matrix-table thead th {
  background: var(--bg-tertiary);
  vertical-align: bottom;
}

.matrix-table tbody tr:last-child th,
.matrix-table tbody tr:last-child td {
  border-bottom: 0;
}

.matrix-table th:last-child,
.matrix-table td:last-child {
  border-right: 0;
}

.matrix-corner,
.matrix-row-head {
  position: sticky;
  left: 0;
  z-index: 1;
  background: var(--bg-secondary);
  text-align: left;
}

.matrix-table thead .matrix-corner {
  background: var(--bg-tertiary);
}

.matrix-row-head {
  min-width: 150px;
  max-width: 190px;
  white-space: normal;
}

.matrix-course-code {
  display: block;
  font-weight: 700;
  color: var(--text-primary);
}

.matrix-course-name {
  display: block;
  font-size: 0.68rem;
  font-weight: 400;
  color: var(--text-muted);
}

.matrix-col-head {
  min-width: 92px;
}

.matrix-track {
  display: block;
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  font-weight: 600;
}

.matrix-level {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.matrix-col-head--total {
  min-width: 64px;
}

.matrix-cell {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--text-secondary);
}

.matrix-cell--complete {
  background: rgba(34, 197, 94, 0.16);
  color: var(--success);
}

.matrix-cell--partial {
  background: rgba(245, 158, 11, 0.16);
  color: var(--warning);
}

.matrix-cell--empty {
  color: var(--text-muted);
}

.matrix-cell--total {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.matrix-empty {
  opacity: 0.5;
}

.matrix-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.75rem;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.matrix-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.matrix-swatch {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.matrix-swatch--complete { background: rgba(34, 197, 94, 0.5); }
.matrix-swatch--partial { background: rgba(245, 158, 11, 0.5); }
.matrix-swatch--empty { background: var(--bg-tertiary); }

/* Responsive */
@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .card--objective {
    grid-column: span 2;
  }

  .hero {
    grid-template-columns: minmax(0, 1fr);
  }

  .hero__ring {
    justify-self: center;
  }
}

@media (max-width: 768px) {
  .student-dashboard {
    padding: 1rem;
  }

  .dashboard-grid,
  .dashboard-grid--two {
    grid-template-columns: 1fr;
  }

  .card--objective {
    grid-column: span 1;
  }

  .celebration {
    flex-direction: column;
    align-items: flex-start;
  }

  .celebration__actions {
    width: 100%;
  }

  .hero__main {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .hero {
    padding: 1.1rem;
  }

  .hero__ring {
    width: 120px;
    height: 120px;
  }

  .hero__ring-svg {
    width: 120px;
    height: 120px;
  }

  .hero__ring-label strong {
    font-size: 1.3rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .celebration__confetti {
    display: none;
  }

  .hero__ring-fill,
  .milestone-bar span,
  .next-badge__bar span,
  .skeleton-medallion {
    transition: none;
    animation: none;
  }
}
</style>
