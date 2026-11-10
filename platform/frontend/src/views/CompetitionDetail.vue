<template>
  <div class="competition-detail-page">
    <div v-if="error" class="error-card" role="alert">
      <p>{{ error }}</p>
      <router-link to="/events" class="btn btn--outline btn--sm">Back to events</router-link>
    </div>

    <div v-else-if="loading" class="muted-note">Loading event...</div>

    <template v-else-if="detail">
      <header class="detail-head">
        <div class="detail-head__identity">
          <img
            v-if="detail.competition.logo_data"
            class="detail-head__logo"
            :src="detail.competition.logo_data"
            :alt="`${detail.competition.name} event mark`"
          />
          <div>
            <router-link to="/events" class="back-link">← All events</router-link>
            <span class="status-pill" :class="`status-pill--${detail.competition.status}`">
              {{ statusLabel(detail.competition.status) }}
            </span>
            <h1>{{ detail.competition.name }}</h1>
            <p class="detail-dates">
              <ClockIcon />
              {{ formatDate(detail.competition.start_at) }} – {{ formatDate(detail.competition.end_at) }}
            </p>
          </div>
        </div>
        <div class="detail-actions">
          <router-link
            v-if="!detail.competition.joined && detail.labs.length"
            :to="practiceLink"
            class="btn btn--outline btn--sm"
          >
            Practice without joining
          </router-link>
          <button
            v-if="!detail.competition.joined && ['upcoming', 'active'].includes(detail.competition.status)"
            type="button"
            class="btn btn--primary btn--sm"
            :disabled="joining"
            @click="join"
          >
            {{ joining ? 'Joining...' : 'Join event' }}
          </button>
          <button
            v-else-if="detail.competition.joined"
            type="button"
            class="btn btn--outline btn--sm"
            :disabled="joining"
            @click="leave"
          >
            {{ joining ? 'Leaving...' : 'Leave event' }}
          </button>
        </div>
      </header>

      <p v-if="detail.competition.description" class="detail-description">
        {{ detail.competition.description }}
      </p>
      <SponsorShowcase :sponsors="detail.competition.sponsors || []" />

      <section v-if="certificates.length" class="event-certificates">
        <h2>Your event certificates</h2>
        <p>
          Participation, placement, and trophy-challenge certificates are available
          after the event ends. Each certificate includes the event logo and sponsors.
        </p>
        <div class="event-certificates__grid">
          <router-link
            v-for="cert in certificates"
            :key="cert.award"
            :to="cert.url"
            class="btn btn--outline btn--sm"
          >
            {{ cert.label }} certificate
          </router-link>
        </div>
      </section>
      <p class="privacy-note">
        Joining is optional. You can practise the exercises without joining and
        nothing is published until you choose to join. This event uses the name
        preference from your Celebration Wall: real name, username, or
        “Anonymous participant”. You can leave at any time.
      </p>
      <p v-if="actionError" class="form-error" role="alert">{{ actionError }}</p>

      <section v-if="detail.competition.can_manage" class="organizer-panel">
        <div class="organizer-panel__head">
          <div>
            <h2>Organizer dashboard</h2>
            <p>Registration and participant view for this event.</p>
          </div>
        </div>

        <div class="registration-stats">
          <div class="registration-stat">
            <strong>{{ counts.total || 0 }}</strong>
            <span>Total participants</span>
          </div>
          <div class="registration-stat registration-stat--new">
            <strong>{{ counts.new_user || 0 }}</strong>
            <span>New sign-ups</span>
          </div>
          <div class="registration-stat">
            <strong>{{ counts.opt_in || 0 }}</strong>
            <span>Existing users opted in</span>
          </div>
        </div>

        <div class="signup-link">
          <label for="signup-link">New participant sign-up link</label>
          <div class="signup-link__row">
            <input id="signup-link" :value="signupLink" type="text" readonly />
            <button type="button" class="btn btn--outline btn--sm" @click="copySignupLink">
              {{ copied ? 'Copied' : 'Copy' }}
            </button>
          </div>
          <p class="muted-note">
            New accounts created through this link are marked as “New sign-up”.
            Existing accounts use the Join event button.
          </p>
        </div>

        <div class="participant-table-wrap">
          <table class="participant-table">
            <thead>
              <tr>
                <th>Participant</th>
                <th>Source</th>
                <th>Joined</th>
                <th>Score</th>
                <th>Solved</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in detail.leaderboard.entries" :key="entry.user_id">
                <td>{{ entry.display_name || entry.username || 'Deleted participant' }}<small v-if="entry.is_me">you</small></td>
                <td>
                  <span class="source-pill" :class="`source-pill--${entry.source}`">
                    {{ sourceLabel(entry.source) }}
                  </span>
                </td>
                <td>{{ entry.joined_at ? formatDate(entry.joined_at) : '—' }}</td>
                <td>{{ entry.score }}</td>
                <td>{{ entry.solved_count }}</td>
              </tr>
            </tbody>
          </table>
          <p v-if="!detail.leaderboard.entries.length" class="muted-note">
            No participants yet. Share the sign-up link to get started.
          </p>
        </div>
      </section>

      <div class="detail-grid">
        <section class="detail-card">
          <h2>Exercises</h2>
          <ol v-if="detail.labs.length" class="event-labs">
            <li v-for="lab in detail.labs" :key="lab.id">
              <router-link class="event-lab-link" :to="labLink(lab)">{{ lab.name }}</router-link>
              <small>{{ labMeta(lab) }}</small>
            </li>
          </ol>
          <p v-else class="muted-note">No exercises selected yet.</p>
        </section>

        <section class="detail-card detail-card--wide">
          <div class="detail-card__head">
            <h2>Leaderboard</h2>
            <button type="button" class="btn btn--outline btn--xs" :disabled="refreshing" @click="loadDetail">
              {{ refreshing ? 'Refreshing...' : 'Refresh' }}
            </button>
          </div>
          <div v-if="detail.leaderboard.entries.length" class="table-wrap">
            <table class="leaderboard-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Participant</th>
                  <th>Score</th>
                  <th>Solved</th>
                  <th>Badges</th>
                  <th>Last solve</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entry in detail.leaderboard.entries"
                  :key="entry.user_id"
                  :class="{ 'row--me': entry.is_me }"
                >
                  <td>{{ entry.rank }}</td>
                  <td>{{ entry.display_name || entry.username || 'Deleted participant' }}<small v-if="entry.is_me">you</small></td>
                  <td>{{ entry.score }}</td>
                  <td>{{ entry.solved_count }}</td>
                  <td class="leaderboard-badges">
                    <span
                      v-for="badge in entry.achievements"
                      :key="badge.type"
                      class="leaderboard-badge"
                      :title="badge.description"
                    >{{ badge.icon }}</span>
                    <span v-if="!entry.achievements?.length" class="muted-note">—</span>
                  </td>
                  <td>{{ entry.last_solved_at ? formatDate(entry.last_solved_at) : '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else-if="detail.competition.status === 'upcoming'" class="muted-note">
            The event has not started yet. Join now and be ready when it opens.
          </p>
          <p v-else class="muted-note">No solves yet. Be the first on the board.</p>
        </section>
      </div>

      <section v-if="eventBadges.length" class="detail-card event-badges">
        <div class="detail-card__head">
          <div>
            <h2>Event badges</h2>
            <p class="muted-note">Earned only for solves inside this event window.</p>
          </div>
        </div>
        <div class="event-badge-grid">
          <article v-for="badge in eventBadges" :key="badge.code" class="event-badge">
            <span class="event-badge__icon" aria-hidden="true">{{ badge.icon }}</span>
            <div>
              <h3>{{ badge.label }}</h3>
              <p>{{ badge.description }}</p>
              <small>
                {{ badge.count }} awarded to
                {{ badge.earners }} {{ badge.earners === 1 ? 'participant' : 'participants' }}
              </small>
            </div>
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '../api/axios'
import ClockIcon from '../components/icons/ClockIcon.vue'
import SponsorShowcase from '../components/SponsorShowcase.vue'

const route = useRoute()
const detail = ref(null)
const certificates = ref([])
const loading = ref(true)
const refreshing = ref(false)
const joining = ref(false)
const error = ref('')
const actionError = ref('')
const copied = ref(false)

const counts = computed(() => (
  detail.value?.leaderboard?.registration_counts || { total: 0, new_user: 0, opt_in: 0 }
))

const eventBadges = computed(() => (
  detail.value?.leaderboard?.badges || []
))

const signupLink = computed(() => {
  if (!detail.value) return ''
  return `${window.location.origin}/register?event=${detail.value.competition.id}`
})

const practiceLink = computed(() => {
  const lab = detail.value?.labs?.[0]
  if (!lab?.track_slug) return '/exercises'
  return {
    path: `/exercises/${lab.track_slug}`,
    query: { labId: String(lab.id) },
  }
})

const labLink = (lab) => (
  lab?.track_slug
    ? { path: `/exercises/${lab.track_slug}`, query: { labId: String(lab.id) } }
    : '/exercises'
)

// High-school lessons carry no level label: the track name alone is the context.
const labMeta = (lab) => (
  lab.level_label ? `${lab.track_name} · ${lab.level_label}` : lab.track_name
)

const statusLabel = (status) => ({
  active: 'Live',
  upcoming: 'Upcoming',
  ended: 'Finished',
  inactive: 'Hidden',
}[status] || status)

const sourceLabel = (source) => source === 'new_user' ? 'New sign-up' : 'Existing opt-in'

const eventEnded = computed(() => {
  const competition = detail.value?.competition
  if (!competition) return false
  if (['ended', 'archived'].includes(competition.status)) return true
  const end = new Date(competition.end_at).getTime()
  return Number.isFinite(end) && Date.now() >= end
})

const loadCertificates = async () => {
  certificates.value = []
  if (!detail.value?.competition?.joined || !eventEnded.value) return
  try {
    const { data } = await axios.get(
      `/competitions/${route.params.id}/certificates`
    )
    certificates.value = data.certificates || []
  } catch {
    certificates.value = []
  }
}

const formatDate = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

const loadDetail = async () => {
  refreshing.value = true
  error.value = ''
  try {
    const { data } = await axios.get(`/competitions/${route.params.id}`)
    detail.value = data
    await loadCertificates()
  } catch (err) {
    error.value = err.response?.data?.detail || 'We could not load this event.'
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

const join = async () => {
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`/competitions/${route.params.id}/join`)
    await loadDetail()
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not join the event.'
  } finally {
    joining.value = false
  }
}

const leave = async () => {
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`/competitions/${route.params.id}/leave`)
    await loadDetail()
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not leave the event.'
  } finally {
    joining.value = false
  }
}

const copySignupLink = async () => {
  try {
    await navigator.clipboard.writeText(signupLink.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 1800)
  } catch {
    actionError.value = 'Could not copy the sign-up link. Select and copy it manually.'
  }
}

onMounted(loadDetail)
</script>

<style scoped>
.competition-detail-page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 2rem;
}

.detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.4rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.detail-head__identity {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  min-width: 0;
}

.detail-head__logo {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  object-fit: contain;
  background: var(--bg-primary);
}

.back-link {
  display: block;
  margin-bottom: 0.4rem;
  font-size: 0.74rem;
  color: var(--text-muted);
  text-decoration: none;
}

.back-link:hover { color: var(--accent); }

.detail-head h1 {
  margin: 0.35rem 0 0.2rem;
  font-size: clamp(1.4rem, 4vw, 2.1rem);
  color: var(--text-primary);
}

.detail-dates {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  font-size: 0.74rem;
  color: var(--text-muted);
}

.detail-dates :deep(svg) { width: 15px; height: 15px; }

.detail-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  flex-shrink: 0;
}

.detail-description {
  margin: 0.8rem 0 0;
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.event-certificates {
  margin-top: 1rem;
  padding: 1.2rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.event-certificates h2 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.event-certificates p {
  margin: 0 0 0.8rem;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.event-certificates__grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.privacy-note {
  margin: 0.8rem 0 0;
  padding: 0.6rem 0.75rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  background: var(--accent-bg);
  color: var(--text-secondary);
  font-size: 0.74rem;
}

.organizer-panel {
  margin-top: 1rem;
  padding: 1.2rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.organizer-panel__head h2 {
  margin: 0;
  font-size: 1rem;
  color: var(--text-primary);
}

.organizer-panel__head p {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.74rem;
}

.registration-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin-top: 0.8rem;
}

.registration-stat {
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.registration-stat strong {
  display: block;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--text-primary);
}

.registration-stat span {
  font-size: 0.66rem;
  color: var(--text-muted);
}

.registration-stat--new strong { color: var(--warning); }

.signup-link {
  margin-top: 0.9rem;
}

.signup-link label {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.signup-link__row {
  display: flex;
  gap: 0.4rem;
}

.signup-link__row input {
  flex: 1;
  min-width: 0;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.74rem;
}

.participant-table-wrap {
  margin-top: 1rem;
  overflow-x: auto;
}

.participant-table,
.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.76rem;
}

.participant-table th,
.participant-table td,
.leaderboard-table th,
.leaderboard-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  white-space: nowrap;
}

.participant-table th,
.leaderboard-table th {
  font-size: 0.64rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.participant-table td small,
.leaderboard-table td small {
  margin-left: 0.3rem;
  padding: 0.05rem 0.3rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent);
  font-size: 0.58rem;
  font-weight: 700;
  text-transform: uppercase;
}

.leaderboard-badges {
  white-space: nowrap;
}

.leaderboard-badge {
  display: inline-grid;
  place-items: center;
  width: 20px;
  height: 20px;
  margin-right: 0.2rem;
  border-radius: 50%;
  background: var(--bg-tertiary);
  font-size: 0.7rem;
}

.event-badges {
  margin-top: 0.9rem;
}

.event-badge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 0.55rem;
}

.event-badge {
  display: flex;
  gap: 0.55rem;
  padding: 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.event-badge__icon {
  flex-shrink: 0;
  font-size: 1.3rem;
  line-height: 1;
}

.event-badge h3 {
  margin: 0;
  font-size: 0.78rem;
}

.event-badge p {
  margin: 0.15rem 0;
  color: var(--text-secondary);
  font-size: 0.7rem;
}

.event-badge small {
  color: var(--text-muted);
  font-size: 0.64rem;
}

.source-pill {
  display: inline-block;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  font-size: 0.6rem;
  font-weight: 700;
}

.source-pill--new_user {
  background: var(--warning-bg);
  color: var(--warning);
}

.source-pill--opt_in {
  background: var(--accent-bg);
  color: var(--accent);
}

.detail-grid {
  display: grid;
  gap: 0.8rem;
  margin-top: 0.9rem;
}

.detail-card {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.detail-card h2 {
  margin: 0 0 0.55rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.detail-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.detail-card__head h2 { margin: 0; }

.event-labs {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.event-labs li + li { margin-top: 0.35rem; }
.event-labs small { display: block; color: var(--text-muted); font-size: 0.66rem; }

.event-lab-link {
  color: var(--text-primary);
  text-decoration: none;
  border-bottom: 1px dotted var(--border-color);
}

.event-lab-link:hover {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.table-wrap { overflow-x: auto; }
.row--me { background: var(--accent-bg); }

.status-pill {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.status-pill--active { background: var(--success-bg); color: var(--success); }
.status-pill--upcoming { background: var(--accent-bg); color: var(--accent); }
.status-pill--ended { background: var(--bg-tertiary); color: var(--text-muted); }
.status-pill--inactive { background: var(--danger-bg); color: var(--danger); }

.muted-note { margin: 0.5rem 0 0; color: var(--text-muted); font-size: 0.76rem; }

.form-error {
  margin: 0.7rem 0 0;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--danger);
  border-radius: 7px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.76rem;
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--danger);
  border-radius: 10px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.85rem;
}

.error-card p { margin: 0; }

@media (max-width: 760px) {
  .competition-detail-page { padding: 1rem; }
  .detail-head { flex-direction: column; }
  .registration-stats { grid-template-columns: 1fr; }
}
</style>
