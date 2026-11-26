<template>
  <main class="briefing-page">
    <header class="briefing-page__bar">
      <div class="briefing-page__heading">
        <p class="briefing-page__eyebrow">Exercise briefing</p>
        <p class="briefing-page__hint">
          Read-only. The desktop, flag, and lab controls stay in the exercise
          workspace.
        </p>
      </div>
      <div class="briefing-page__actions">
        <button
          v-if="state === 'ready'"
          type="button"
          class="btn btn--secondary btn--sm"
          @click="printBriefing"
        >
          Print briefing
        </button>
        <router-link :to="backLink" class="btn btn--secondary btn--sm">
          Back to exercise
        </router-link>
      </div>
    </header>

    <p v-if="state === 'loading'" class="briefing-page__status" role="status">
      Loading the exercise briefing...
    </p>

    <section v-else-if="state === 'error'" class="briefing-page__status" role="alert">
      <h1>Briefing unavailable</h1>
      <p>
        Open the exercise workspace and choose the Briefing tab. The briefing
        needs the active exercise session to load.
      </p>
    </section>

    <ExerciseBrief
      v-else
      :lab="lab"
      :track="track"
      :level="level"
      :hostnames="hostnames"
      :hints="hints"
      :workbook-url="workbookUrl"
      popout
      @open-workbook="openWorkbook"
    />
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import axios from '../api/axios'
import ExerciseBrief from '../components/ExerciseBrief.vue'
import { setWikiAuthCookie } from '../utils/wikiAuth'
import { resolveWorkbookUrl } from '../utils/workbook'

const route = useRoute()
const state = ref('loading')
const lab = ref(null)
const track = ref(null)
const level = ref(null)
const hostnames = ref([])
const hints = ref([])
const workbookUrl = ref('')

const labId = computed(() => Number(route.query.labId || 0))

const backLink = computed(() => {
  const query = {}
  if (labId.value > 0) query.labId = String(labId.value)
  if (route.query.courseId) query.courseId = String(route.query.courseId)
  if (route.query.wikiSlug) query.wikiSlug = String(route.query.wikiSlug)
  if (typeof route.query.launch === 'string' && route.query.launch) {
    query.launch = route.query.launch
  }
  query.tab = 'briefing'
  return {
    name: 'TrackDetail',
    params: { trackSlug: route.params.trackSlug },
    query,
  }
})

const openWorkbook = () => {
  if (!workbookUrl.value) return
  setWikiAuthCookie()
  window.open(workbookUrl.value, '_blank', 'noopener,noreferrer')
}

const printBriefing = () => window.print()

onMounted(async () => {
  if (!Number.isInteger(labId.value) || labId.value <= 0) {
    state.value = 'error'
    return
  }

  try {
    const params = {}
    if (route.query.courseId) {
      const courseId = Number(route.query.courseId)
      if (Number.isInteger(courseId) && courseId > 0) params.course_id = courseId
    }
    if (typeof route.query.launch === 'string' && route.query.launch) {
      params.launch = route.query.launch
    }
    const { data } = await axios.get(`/exercises/labs/${labId.value}`, { params })
    lab.value = data.lab
    track.value = data.track
    level.value = data.level
    hostnames.value = Array.isArray(data.hostnames) ? data.hostnames : []
    hints.value = Array.isArray(data.lab?.requested_hints)
      ? data.lab.requested_hints
      : []
    workbookUrl.value = resolveWorkbookUrl(
      data.lab?.workbook,
      route.query.wikiSlug ? String(route.query.wikiSlug) : ''
    )
    state.value = 'ready'
    if (data.lab?.workbook) await setWikiAuthCookie()
  } catch {
    state.value = 'error'
  }
})
</script>

<style scoped>
.briefing-page {
  width: min(100%, 52rem);
  margin: 0 auto;
  padding: 1.25rem;
}

.briefing-page__bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.briefing-page__heading {
  flex: 1 1 16rem;
}

.briefing-page__eyebrow {
  margin: 0;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.briefing-page__hint {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.briefing-page__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-left: auto;
}

.briefing-page__status {
  padding: 2rem 0;
  color: var(--text-secondary);
}

.briefing-page__status h1 {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 1.2rem;
}

.briefing-page__status p {
  margin: 0;
  max-width: 34rem;
}

@media (max-width: 480px) {
  .briefing-page {
    padding: 0.75rem;
  }

  .briefing-page__actions,
  .briefing-page__actions .btn {
    width: 100%;
    margin-left: 0;
  }
}

@media print {
  .briefing-page {
    width: 100%;
    padding: 0;
  }

  .briefing-page__bar {
    display: none;
  }
}
</style>
