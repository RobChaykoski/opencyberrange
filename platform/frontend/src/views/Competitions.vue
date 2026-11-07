<template>
  <div class="competitions-page">
    <header class="page-head">
      <div>
        <p class="page-head__eyebrow">Special events</p>
        <h1>Events</h1>
        <p class="page-head__subtitle">
          Opt-in, time-boxed events using selected exercises. Joining is optional;
          leaving is always allowed.
        </p>
      </div>
      <button
        v-if="isInstructor"
        type="button"
        class="btn btn--primary btn--sm"
        @click="showCreate = !showCreate"
      >
        {{ showCreate ? 'Close form' : 'Create event' }}
      </button>
    </header>

    <div v-if="error" class="error-card" role="alert">
      <p>{{ error }}</p>
      <button type="button" class="btn btn--outline btn--sm" @click="loadCompetitions">Try again</button>
    </div>

    <section v-if="isInstructor && showCreate" class="create-panel" aria-labelledby="create-heading">
      <h2 id="create-heading">Create an event</h2>
      <p class="create-panel__note">
        Only solves inside the event window count. Scores reuse the course
        scoring rules: completion, no-hint, first-attempt, speed, and event first blood.
      </p>
      <form class="create-form" @submit.prevent="createCompetition">
        <div class="create-form__row">
          <label class="field">
            <span>Name</span>
            <input v-model="newCompetition.name" type="text" maxlength="150" required />
          </label>
          <label class="field">
            <span>Starts</span>
            <input v-model="newCompetition.start_at" type="datetime-local" required />
          </label>
          <label class="field">
            <span>Ends</span>
            <input v-model="newCompetition.end_at" type="datetime-local" required />
          </label>
        </div>
        <label class="field">
          <span>Description</span>
          <textarea v-model="newCompetition.description" rows="3" placeholder="What should participants know?" />
        </label>

        <div class="event-logo-field">
          <div class="event-logo-field__preview">
            <img
              v-if="newCompetition.logo_data"
              :src="newCompetition.logo_data"
              alt="Event mark preview"
            />
            <TrophyIcon v-else class="event-logo-field__placeholder" />
          </div>
          <div class="event-logo-field__body">
            <strong>Event mark</strong>
            <p>Optional PNG, JPEG, or WebP shown on the event card and detail header.</p>
            <div class="event-logo-field__actions">
              <label class="btn btn--outline btn--xs">
                {{ newCompetition.logo_data ? 'Replace mark' : 'Upload mark' }}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  class="sr-only"
                  @change="onCompetitionLogoSelected"
                />
              </label>
              <button
                v-if="newCompetition.logo_data"
                type="button"
                class="btn btn--outline btn--xs"
                @click="newCompetition.logo_data = null"
              >
                Remove mark
              </button>
            </div>
          </div>
        </div>

        <section class="sponsor-editor" aria-labelledby="sponsor-editor-title">
          <div class="sponsor-editor__head">
            <div>
              <h3 id="sponsor-editor-title">Sponsored by</h3>
              <p>Optional. Add one or more event partners and choose their recognition tier.</p>
            </div>
            <button type="button" class="btn btn--outline btn--xs" @click="addSponsor">
              + Add sponsor
            </button>
          </div>

          <p v-if="!newCompetition.sponsors.length" class="sponsor-editor__empty">
            No sponsors yet. Events can recognise Gold, Silver, and Bronze partners.
          </p>

          <div
            v-for="(sponsor, index) in newCompetition.sponsors"
            :key="sponsor.key"
            class="sponsor-row"
            :class="`sponsor-row--${sponsor.tier}`"
          >
            <div class="sponsor-row__logo">
              <div class="sponsor-row__logo-preview">
                <img v-if="sponsor.logo_data" :src="sponsor.logo_data" :alt="`${sponsor.name || 'Sponsor'} logo`" />
                <span v-else aria-hidden="true">{{ sponsorInitials(sponsor.name) }}</span>
              </div>
              <label class="sponsor-row__upload">
                {{ sponsor.logo_data ? 'Replace logo' : 'Upload logo' }}
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  @change="onSponsorLogoSelected($event, index)"
                />
              </label>
              <button
                v-if="sponsor.logo_data"
                type="button"
                class="sponsor-row__logo-remove"
                @click="removeSponsorLogo(index)"
              >
                Remove logo
              </button>
            </div>
            <label class="field sponsor-row__tier">
              <span>Tier</span>
              <select v-model="sponsor.tier">
                <option value="gold">Gold</option>
                <option value="silver">Silver</option>
                <option value="bronze">Bronze</option>
              </select>
            </label>
            <label class="field sponsor-row__name">
              <span>Sponsor name</span>
              <input v-model="sponsor.name" type="text" maxlength="150" placeholder="Organisation name" />
            </label>
            <button
              type="button"
              class="sponsor-row__remove"
              :aria-label="`Remove sponsor ${index + 1}`"
              @click="removeSponsor(index)"
            >
              Remove
            </button>
            <label class="field sponsor-row__website">
              <span>Website (optional)</span>
              <input v-model="sponsor.website_url" type="text" maxlength="500" placeholder="https://example.com" />
            </label>
            <label class="field sponsor-row__description">
              <span>Description</span>
              <textarea
                v-model="sponsor.description"
                rows="2"
                maxlength="500"
                placeholder="A short note about this partner (optional)"
              />
            </label>
          </div>
        </section>

        <div class="lab-picker">
          <div class="lab-picker__head">
            <span class="lab-picker__label">
              Exercises
              <small>{{ newCompetition.lab_ids.length }} selected</small>
            </span>
            <div class="lab-picker__actions">
              <button type="button" class="btn btn--outline btn--xs" @click="selectAllLabs">
                Select all
              </button>
              <button type="button" class="btn btn--outline btn--xs" @click="clearLabs">
                Clear
              </button>
            </div>
          </div>
          <div v-if="labsLoading" class="muted-note">Loading exercises...</div>
          <div v-else-if="!labTracks.length" class="muted-note">
            No exercises are available for event selection.
          </div>
          <div v-else class="lab-picker__groups">
            <section v-for="track in labTracks" :key="track.slug" class="lab-group">
              <h3>{{ track.name }} <small>{{ track.labs.length }}</small></h3>
              <label v-for="lab in track.labs" :key="lab.id" class="lab-option">
                <input v-model="newCompetition.lab_ids" type="checkbox" :value="lab.id" />
                <span>{{ lab.name }}</span>
              </label>
            </section>
          </div>
        </div>

        <p v-if="createError" class="form-error" role="alert">{{ createError }}</p>
        <div class="create-form__footer">
          <button type="submit" class="btn btn--primary btn--sm" :disabled="creating">
            {{ creating ? 'Creating...' : 'Create event' }}
          </button>
        </div>
      </form>
    </section>

    <div v-if="loading" class="muted-note">Loading events...</div>

    <div v-else-if="!competitions.length" class="empty-state">
      <TrophyIcon class="empty-state__icon" />
      <p class="empty-state__title">No events yet.</p>
      <p class="empty-state__hint">
        {{ isInstructor ? 'Create a short event for your learners.' : 'Check back when an instructor opens an event.' }}
      </p>
    </div>

    <div v-else class="competitions-layout">
      <section class="competition-list" aria-label="Events">
        <button
          v-if="archivedCount"
          type="button"
          class="archive-toggle"
          :aria-pressed="showArchived"
          @click="showArchived = !showArchived"
        >
          {{ showArchived ? 'Hide archived events' : `Show archived events (${archivedCount})` }}
        </button>
        <button
          v-for="comp in visibleCompetitions"
          :key="comp.id"
          type="button"
          class="comp-card"
          :class="{ 'comp-card--selected': selectedId === comp.id }"
          @click="selectCompetition(comp.id)"
        >
          <span class="comp-card__top">
            <span class="status-pill" :class="`status-pill--${comp.status}`">{{ statusLabel(comp.status) }}</span>
            <span v-if="comp.joined" class="joined-pill">Joined</span>
          </span>
          <span class="comp-card__identity">
            <img v-if="comp.logo_data" class="comp-card__logo" :src="comp.logo_data" :alt="`${comp.name} event mark`" />
            <span class="comp-card__name">{{ comp.name }}</span>
          </span>
          <span class="comp-card__meta">
            {{ formatDate(comp.start_at) }} – {{ formatDate(comp.end_at) }}
          </span>
          <span class="comp-card__stats">
            {{ comp.lab_count }} {{ comp.lab_count === 1 ? 'exercise' : 'exercises' }}
            · {{ comp.participant_count }} {{ comp.participant_count === 1 ? 'participant' : 'participants' }}
            <template v-if="comp.sponsors?.length">
              · {{ comp.sponsors.length }} {{ comp.sponsors.length === 1 ? 'sponsor' : 'sponsors' }}
            </template>
          </span>
        </button>
      </section>

      <section v-if="selected" class="comp-detail" aria-live="polite">
        <div class="comp-detail__head">
          <div class="comp-detail__identity">
            <img
              v-if="selected.competition.logo_data"
              class="comp-detail__logo"
              :src="selected.competition.logo_data"
              :alt="`${selected.competition.name} event mark`"
            />
            <div>
              <span class="status-pill" :class="`status-pill--${selected.competition.status}`">
                {{ statusLabel(selected.competition.status) }}
              </span>
              <h2>{{ selected.competition.name }}</h2>
              <p class="comp-detail__dates">
                <ClockIcon />
                {{ formatDate(selected.competition.start_at) }} – {{ formatDate(selected.competition.end_at) }}
              </p>
            </div>
          </div>
          <div class="comp-detail__actions">
            <router-link
              :to="`/events/${selected.competition.id}`"
              class="btn btn--outline btn--sm"
            >
              Open dashboard
            </router-link>
            <router-link
              v-if="!selected.competition.joined && selected.labs.length"
              :to="practiceLink"
              class="btn btn--outline btn--sm"
            >
              Practice without joining
            </router-link>
            <button
              v-if="canJoinSelected"
              type="button"
              class="btn btn--primary btn--sm"
              :disabled="joining"
              @click="joinSelected"
            >
              {{ joining ? 'Joining...' : 'Join event' }}
            </button>
            <button
              v-else-if="selected.competition.joined"
              type="button"
              class="btn btn--outline btn--sm"
              :disabled="joining"
              @click="leaveSelected"
            >
              {{ joining ? 'Leaving...' : 'Leave event' }}
            </button>
            <button
              v-if="selected.competition.can_manage"
              type="button"
              class="btn btn--outline btn--sm"
              :disabled="archiving"
              @click="toggleArchiveSelected"
            >
              {{ archiving
                ? 'Saving...'
                : (selected.competition.is_archived ? 'Restore event' : 'Archive event') }}
            </button>
            <button
              v-if="selected.competition.can_manage"
              type="button"
              class="btn btn--outline btn--sm comp-delete"
              :disabled="deleting"
              @click="deleteSelected"
            >
              {{ deleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>

        <p v-if="selected.competition.description" class="comp-detail__description">
          {{ selected.competition.description }}
        </p>
        <SponsorShowcase :sponsors="selected.competition.sponsors || []" />
        <p class="privacy-note">
          Joining is optional. You can practise the exercises without joining and
          nothing is published until you choose to join. Joining shows your display
          name on this event leaderboard using the preference from your
          Celebration Wall: real name, username, or “Anonymous participant”. You can leave at any time.
        </p>
        <p v-if="actionError" class="form-error" role="alert">{{ actionError }}</p>

        <div class="comp-detail__grid">
          <section class="detail-card">
            <h3>Exercises</h3>
            <ol v-if="selected.labs.length" class="event-labs">
              <li v-for="lab in selected.labs" :key="lab.id">
                <router-link class="event-lab-link" :to="labPracticeLink(lab)">
                  {{ lab.name }}
                </router-link>
                <small>{{ labMeta(lab) }}</small>
              </li>
            </ol>
            <p v-else class="muted-note">No exercises selected yet.</p>
          </section>

          <section class="detail-card detail-card--wide">
            <div class="detail-card__head">
              <h3>Leaderboard</h3>
              <button type="button" class="btn btn--outline btn--xs" :disabled="refreshing" @click="refreshSelected">
                {{ refreshing ? 'Refreshing...' : 'Refresh' }}
              </button>
            </div>
            <div v-if="selected.leaderboard.entries.length" class="leaderboard-wrap">
              <table class="leaderboard-table">
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Participant</th>
                    <th>Score</th>
                    <th>Solved</th>
                    <th>Last solve</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="entry in selected.leaderboard.entries"
                    :key="entry.user_id"
                    :class="{ 'leaderboard-row--me': entry.is_me }"
                  >
                    <td>{{ entry.rank }}</td>
                    <td>
                      {{ entry.display_name || entry.username }}
                      <small v-if="entry.is_me">you</small>
                    </td>
                    <td>{{ entry.score }}</td>
                    <td>{{ entry.solved_count }}</td>
                    <td>{{ entry.last_solved_at ? formatDate(entry.last_solved_at) : '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else-if="selected.competition.status === 'upcoming'" class="muted-note">
              The event has not started yet. Join now and be ready when it opens.
            </p>
            <p v-else class="muted-note">No solves yet. Be the first on the board.</p>
          </section>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import axios from '../api/axios'
import TrophyIcon from '../components/icons/TrophyIcon.vue'
import ClockIcon from '../components/icons/ClockIcon.vue'
import SponsorShowcase from '../components/SponsorShowcase.vue'
import { resizeImageFile } from '../utils/imageResize'

const competitions = ref([])
const selected = ref(null)
const selectedId = ref(null)
const loading = ref(true)
const refreshing = ref(false)
const joining = ref(false)
const error = ref('')
const actionError = ref('')

const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')
const labsLoading = ref(false)
const availableLabs = ref([])
const showArchived = ref(false)
const archiving = ref(false)
const deleting = ref(false)
const newCompetition = reactive({
  name: '',
  description: '',
  logo_data: null,
  start_at: '',
  end_at: '',
  lab_ids: [],
  sponsors: [],
})

const onCompetitionLogoSelected = async (event) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  createError.value = ''
  if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
    createError.value = 'Event marks must be a PNG, JPEG, or WebP image.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    createError.value = 'Choose an event mark smaller than 5 MB.'
    return
  }
  try {
    newCompetition.logo_data = await resizeImageFile(file, {
      maxDimension: 512,
      quality: 0.88,
    })
  } catch {
    createError.value = 'Could not process that event mark.'
  }
}

const addSponsor = () => {
  newCompetition.sponsors.push({
    key: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name: '',
    description: '',
    logo_data: null,
    website_url: '',
    tier: 'gold',
  })
}

const removeSponsor = (index) => {
  newCompetition.sponsors.splice(index, 1)
}

const sponsorInitials = (name) => {
  const words = String(name || '').trim().split(/\s+/).filter(Boolean)
  if (!words.length) return '+'
  if (words.length === 1) return Array.from(words[0]).slice(0, 2).join('').toUpperCase()
  return `${Array.from(words[0])[0]}${Array.from(words[words.length - 1])[0]}`.toUpperCase()
}

const onSponsorLogoSelected = async (event, index) => {
  const file = event.target.files?.[0]
  event.target.value = ''
  if (!file) return
  createError.value = ''
  if (!/^image\/(png|jpeg|webp)$/.test(file.type)) {
    createError.value = 'Sponsor logos must be a PNG, JPEG, or WebP image.'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    createError.value = 'Choose a sponsor logo smaller than 5 MB.'
    return
  }
  try {
    const logo = await resizeImageFile(file, { maxDimension: 512, quality: 0.88 })
    const sponsor = newCompetition.sponsors[index]
    if (sponsor) sponsor.logo_data = logo
  } catch {
    createError.value = 'Could not process that sponsor logo.'
  }
}

const removeSponsorLogo = (index) => {
  const sponsor = newCompetition.sponsors[index]
  if (sponsor) sponsor.logo_data = null
}

const isInstructor = computed(() => {
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return ['instructor', 'admin'].includes(user.role)
  } catch {
    return false
  }
})

const statusOrder = { active: 0, upcoming: 1, ended: 2, inactive: 3, archived: 4 }
const sortedCompetitions = computed(() => (
  [...competitions.value].sort((a, b) => {
    const byStatus = (statusOrder[a.status] ?? 9) - (statusOrder[b.status] ?? 9)
    if (byStatus !== 0) return byStatus
    return new Date(b.start_at) - new Date(a.start_at)
  })
))

const archivedCount = computed(
  () => competitions.value.filter(c => c.is_archived).length
)
const visibleCompetitions = computed(() => (
  sortedCompetitions.value.filter(c => showArchived.value || !c.is_archived)
))

const labTracks = computed(() => {
  const groups = new Map()
  for (const lab of availableLabs.value) {
    const key = lab.track_slug || 'uncategorized'
    if (!groups.has(key)) {
      groups.set(key, {
        slug: key,
        name: lab.track_name || 'Uncategorized',
        labs: [],
      })
    }
    groups.get(key).labs.push(lab)
  }
  return [...groups.values()]
})

const canJoinSelected = computed(() => {
  if (!selected.value) return false
  return !selected.value.competition.joined
    && ['upcoming', 'active'].includes(selected.value.competition.status)
})

const practiceLink = computed(() => {
  const lab = selected.value?.labs?.[0]
  if (!lab?.track_slug) return '/exercises'
  return {
    path: `/exercises/${lab.track_slug}`,
    query: { labId: String(lab.id) },
  }
})

const statusLabel = (status) => ({
  active: 'Live',
  upcoming: 'Upcoming',
  ended: 'Finished',
  inactive: 'Hidden',
  archived: 'Archived',
}[status] || status)

const labPracticeLink = (lab) => (
  lab?.track_slug
    ? { path: `/exercises/${lab.track_slug}`, query: { labId: String(lab.id) } }
    : '/exercises'
)

// High-school lessons carry no level label: the track name alone is the context.
const labMeta = (lab) => (
  lab.level_label ? `${lab.track_name} · ${lab.level_label}` : lab.track_name
)

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

const toLocalInput = (date) => {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return local.toISOString().slice(0, 16)
}

const resetNewCompetition = () => {
  const now = new Date()
  newCompetition.name = ''
  newCompetition.description = ''
  newCompetition.logo_data = null
  newCompetition.start_at = toLocalInput(now)
  newCompetition.end_at = toLocalInput(new Date(now.getTime() + 2 * 60 * 60 * 1000))
  newCompetition.lab_ids = []
  newCompetition.sponsors = []
  createError.value = ''
}

const loadCompetitions = async (preserveSelection = false) => {
  loading.value = true
  error.value = ''
  const currentId = selectedId.value
  try {
    const response = await axios.get('/competitions')
    competitions.value = response.data.competitions || []
    const keepCurrent = preserveSelection
      && currentId
      && competitions.value.some(c => c.id === currentId)
    const preferred = keepCurrent
      ? competitions.value.find(c => c.id === currentId)
      : sortedCompetitions.value.find(c => ['active', 'upcoming'].includes(c.status))
        || sortedCompetitions.value[0]
    if (preferred) {
      await selectCompetition(preferred.id)
    } else {
      selected.value = null
      selectedId.value = null
    }
  } catch {
    error.value = 'We could not load events. Check your connection and try again.'
  } finally {
    loading.value = false
  }
}

const selectCompetition = async (id) => {
  selectedId.value = id
  actionError.value = ''
  try {
    const response = await axios.get(`/competitions/${id}`)
    selected.value = response.data
  } catch (err) {
    selected.value = null
    actionError.value = err.response?.data?.detail || 'Could not load that event.'
  }
}

const refreshSelected = async () => {
  if (!selectedId.value) return
  refreshing.value = true
  await selectCompetition(selectedId.value)
  refreshing.value = false
}

const joinSelected = async () => {
  if (!selectedId.value) return
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`/competitions/${selectedId.value}/join`)
    await loadCompetitions(true)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not join that event.'
  } finally {
    joining.value = false
  }
}

const leaveSelected = async () => {
  if (!selectedId.value) return
  joining.value = true
  actionError.value = ''
  try {
    await axios.post(`/competitions/${selectedId.value}/leave`)
    await loadCompetitions(true)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not leave that event.'
  } finally {
    joining.value = false
  }
}

const toggleArchiveSelected = async () => {
  if (!selectedId.value || !selected.value) return
  archiving.value = true
  actionError.value = ''
  const id = selectedId.value
  const action = selected.value.competition.is_archived ? 'unarchive' : 'archive'
  try {
    await axios.post(`/competitions/${id}/${action}`)
    await loadCompetitions(true)
    await selectCompetition(id)
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not change the archive state.'
  } finally {
    archiving.value = false
  }
}

const deleteSelected = async () => {
  if (!selectedId.value || !selected.value) return
  const name = selected.value.competition.name
  const confirmed = window.confirm(
    `Delete "${name}"?\n\nThis removes the event and its leaderboard rows permanently. ` +
    'Archive it instead if you only want it out of the active list.'
  )
  if (!confirmed) return
  deleting.value = true
  actionError.value = ''
  try {
    await axios.delete(`/competitions/${selectedId.value}`)
    selected.value = null
    selectedId.value = null
    await loadCompetitions()
  } catch (err) {
    actionError.value = err.response?.data?.detail || 'Could not delete that event.'
  } finally {
    deleting.value = false
  }
}

const loadAvailableLabs = async () => {
  labsLoading.value = true
  try {
    const response = await axios.get('/instructor/labs')
    availableLabs.value = response.data.labs || []
  } catch {
    availableLabs.value = []
  } finally {
    labsLoading.value = false
  }
}

const selectAllLabs = () => {
  newCompetition.lab_ids = availableLabs.value.map(lab => lab.id)
}

const clearLabs = () => {
  newCompetition.lab_ids = []
}

const createCompetition = async () => {
  createError.value = ''
  if (!newCompetition.name.trim()) {
    createError.value = 'Give the event a name.'
    return
  }
  if (!newCompetition.start_at || !newCompetition.end_at) {
    createError.value = 'Choose a start and end time.'
    return
  }
  if (!newCompetition.lab_ids.length) {
    createError.value = 'Select at least one exercise.'
    return
  }
  const sponsors = newCompetition.sponsors
    .map(({ name, description, tier, logo_data, website_url }) => ({
      name: name.trim(),
      description: description.trim() || null,
      tier,
      logo_data: logo_data || null,
      website_url: website_url.trim() || null,
    }))
    .filter((sponsor) => sponsor.name)
  creating.value = true
  try {
    const response = await axios.post('/competitions', {
      name: newCompetition.name.trim(),
      description: newCompetition.description.trim() || null,
      logo_data: newCompetition.logo_data || null,
      start_at: new Date(newCompetition.start_at).toISOString(),
      end_at: new Date(newCompetition.end_at).toISOString(),
      lab_ids: newCompetition.lab_ids,
      sponsors,
    })
    showCreate.value = false
    await loadCompetitions()
    await selectCompetition(response.data.id)
    resetNewCompetition()
  } catch (err) {
    createError.value = err.response?.data?.detail || 'Could not create the event.'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  resetNewCompetition()
  if (isInstructor.value) await loadAvailableLabs()
  await loadCompetitions()
})
</script>

<style scoped>
.competitions-page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 2rem;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.page-head__eyebrow {
  margin: 0 0 0.2rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}

.page-head h1 {
  margin: 0;
  font-size: clamp(1.7rem, 4vw, 2.4rem);
  line-height: 1.1;
  color: var(--text-primary);
}

.page-head__subtitle {
  max-width: 62ch;
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.create-panel {
  margin-bottom: 1.25rem;
  padding: 1.3rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.create-panel h2 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.create-panel__note {
  margin: 0 0 1rem;
  font-size: 0.76rem;
  color: var(--text-muted);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.event-logo-field {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.event-logo-field__preview {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: var(--text-muted);
}

.event-logo-field__preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 9px;
}

.event-logo-field__placeholder {
  width: 26px;
  height: 26px;
}

.event-logo-field__body {
  min-width: 0;
}

.event-logo-field__body strong {
  display: block;
  color: var(--text-primary);
  font-size: 0.85rem;
}

.event-logo-field__body p {
  margin: 0.15rem 0 0.5rem;
  color: var(--text-secondary);
  font-size: 0.74rem;
  line-height: 1.45;
}

.event-logo-field__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.create-form__row {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.field input,
.field textarea,
.field select {
  width: 100%;
  padding: 0.5rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
}

.field input:focus,
.field textarea:focus,
.field select:focus {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

/* Sponsors */
.sponsor-editor {
  padding: 0.85rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-primary);
}

.sponsor-editor__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.6rem;
}

.sponsor-editor__head h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 0.92rem;
}

.sponsor-editor__head p {
  margin: 0.15rem 0 0;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.sponsor-editor__empty {
  margin: 0;
  padding: 0.6rem 0.7rem;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.72rem;
}

.sponsor-row {
  --tier-accent: #d4a017;
  display: grid;
  grid-template-columns: 92px 130px minmax(0, 1fr) auto;
  grid-template-areas:
    "logo tier name remove"
    "logo website website website"
    "logo description description description";
  gap: 0.5rem 0.65rem;
  margin-top: 0.55rem;
  padding: 0.7rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--tier-accent);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.sponsor-row--gold { --tier-accent: #d4a017; }
.sponsor-row--silver { --tier-accent: #94a3b8; }
.sponsor-row--bronze { --tier-accent: #b87333; }

.sponsor-row__logo {
  grid-area: logo;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
}

.sponsor-row__logo-preview {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-tertiary);
  color: var(--tier-accent);
  font-size: 0.82rem;
  font-weight: 800;
}

.sponsor-row__logo-preview img {
  width: 100%;
  height: 100%;
  padding: 4px;
  object-fit: contain;
}

.sponsor-row__upload {
  position: relative;
  color: var(--accent);
  font-size: 0.62rem;
  font-weight: 700;
  text-align: center;
  cursor: pointer;
}

.sponsor-row__upload input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.sponsor-row__logo-remove {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.58rem;
  cursor: pointer;
  text-decoration: underline;
}

.sponsor-row__tier { grid-area: tier; }
.sponsor-row__name { grid-area: name; }
.sponsor-row__website { grid-area: website; }
.sponsor-row__description { grid-area: description; }

.sponsor-row__remove {
  grid-area: remove;
  align-self: end;
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.64rem;
  cursor: pointer;
}

.sponsor-row__remove:hover {
  border-color: var(--danger);
  color: var(--danger);
}

@media (max-width: 720px) {
  .sponsor-row {
    grid-template-columns: 82px minmax(0, 1fr) auto;
    grid-template-areas:
      "logo tier remove"
      "logo name name"
      "website website website"
      "description description description";
  }

  .comp-detail__head {
    flex-direction: column;
  }

  .comp-detail__actions {
    width: 100%;
  }

  .event-logo-field {
    flex-direction: column;
  }
}

.lab-picker {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 0.75rem;
  background: var(--bg-primary);
}

.lab-picker__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.lab-picker__label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.lab-picker__label small {
  margin-left: 0.35rem;
  font-weight: 500;
  color: var(--text-muted);
}

.lab-picker__actions {
  display: flex;
  gap: 0.35rem;
}

.lab-picker__groups {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.75rem;
  max-height: 260px;
  overflow-y: auto;
}

.lab-group h3 {
  margin: 0 0 0.35rem;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.lab-group h3 small {
  color: var(--text-muted);
  font-weight: 500;
}

.lab-option {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 0.2rem 0;
  font-size: 0.74rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.lab-option input {
  margin-top: 0.15rem;
  accent-color: var(--accent);
}

.create-form__footer {
  display: flex;
  justify-content: flex-end;
}

.form-error {
  margin: 0;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--danger);
  border-radius: 7px;
  background: var(--danger-bg);
  color: var(--text-primary);
  font-size: 0.76rem;
}

.competitions-layout {
  display: grid;
  grid-template-columns: minmax(260px, 0.8fr) minmax(0, 1.4fr);
  gap: 1rem;
  align-items: start;
}

.competition-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.comp-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
  width: 100%;
  padding: 0.8rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
  color: inherit;
  text-align: left;
  cursor: pointer;
  font: inherit;
  transition: border-color 0.15s, background 0.15s;
}

.comp-card:hover {
  border-color: var(--accent);
}

.comp-card--selected {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.comp-card__top {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.comp-card__identity {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}

.comp-card__logo {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 6px;
  object-fit: contain;
  background: var(--bg-primary);
}

.comp-card__name {
  font-size: 0.86rem;
  font-weight: 700;
  color: var(--text-primary);
  overflow-wrap: anywhere;
}

.comp-card__meta,
.comp-card__stats {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.comp-detail {
  padding: 1.2rem;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background: var(--bg-secondary);
}

.comp-detail__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.comp-detail__identity {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  min-width: 0;
}

.comp-detail__logo {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 10px;
  object-fit: contain;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.comp-detail__head h2 {
  margin: 0.35rem 0 0.2rem;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.comp-detail__dates {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.comp-detail__dates :deep(svg) {
  width: 14px;
  height: 14px;
}

.comp-detail__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  flex-shrink: 0;
}

.comp-detail__description {
  margin: 0.7rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.55;
}

.privacy-note {
  margin: 0.7rem 0 0;
  padding: 0.55rem 0.7rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 7px 7px 0;
  background: var(--accent-bg);
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.comp-detail__grid {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.9rem;
}

.detail-card {
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.detail-card h3 {
  margin: 0 0 0.55rem;
  font-size: 0.7rem;
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

.detail-card__head h3 {
  margin: 0;
}

.event-labs {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.event-labs li + li {
  margin-top: 0.35rem;
}

.event-labs small {
  display: block;
  color: var(--text-muted);
  font-size: 0.66rem;
}

.leaderboard-wrap {
  overflow-x: auto;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.76rem;
}

.leaderboard-table th,
.leaderboard-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  white-space: nowrap;
}

.leaderboard-table th {
  font-size: 0.64rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}

.leaderboard-table td:nth-child(1),
.leaderboard-table td:nth-child(3),
.leaderboard-table td:nth-child(4) {
  font-variant-numeric: tabular-nums;
}

.leaderboard-row--me {
  background: var(--accent-bg);
}

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

.status-pill,
.joined-pill {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.status-pill--active {
  background: var(--success-bg);
  color: var(--success);
}

.status-pill--upcoming {
  background: var(--accent-bg);
  color: var(--accent);
}

.status-pill--ended {
  background: var(--bg-tertiary);
  color: var(--text-muted);
}

.status-pill--inactive {
  background: var(--danger-bg);
  color: var(--danger);
}

.status-pill--archived {
  background: rgba(120, 113, 108, 0.2);
  color: #d6d3d1;
  border: 1px solid rgba(168, 162, 158, 0.35);
}

.archive-toggle {
  align-self: flex-start;
  margin-bottom: 0.5rem;
  padding: 0.25rem 0.6rem;
  border: 1px dashed var(--border-color);
  border-radius: 999px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.75rem;
  cursor: pointer;
}

.archive-toggle:hover {
  color: var(--text-primary);
  border-color: var(--text-muted);
}

.event-lab-link {
  color: var(--text-primary);
  text-decoration: none;
  border-bottom: 1px dotted var(--border-color);
}

.event-lab-link:hover {
  color: var(--accent);
  border-bottom-color: var(--accent);
}

.comp-delete {
  border-color: rgba(248, 113, 113, 0.5);
  color: #fca5a5;
}

.joined-pill {
  background: var(--warning-bg);
  color: var(--warning);
}

.muted-note {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--text-secondary);
}

.empty-state__icon {
  width: 36px;
  height: 36px;
  margin-bottom: 0.35rem;
  color: var(--text-muted);
}

.empty-state__title {
  margin: 0;
  font-size: 0.9rem;
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

@media (max-width: 980px) {
  .competitions-layout {
    grid-template-columns: 1fr;
  }

  .create-form__row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .competitions-page {
    padding: 1rem;
  }

  .page-head {
    flex-direction: column;
  }

  .comp-detail__head {
    flex-direction: column;
  }
}
</style>
