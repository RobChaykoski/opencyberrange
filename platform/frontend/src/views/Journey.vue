<template>
  <div class="journey">
    <header class="journey__head">
      <p class="journey__eyebrow">Direction, not a score</p>
      <h1>Journey &amp; mission</h1>
      <p>
        Choose the direction you are working toward. The Living Archive observes
        what your verified work becomes, not what you say you enjoy. You can
        change missions; your evidence stays with you.
      </p>
    </header>

    <p v-if="message" class="journey__message" role="status">{{ message }}</p>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="journey__empty">Loading journeys...</p>

    <template v-else>
      <section v-if="archive" class="journey__archive" aria-labelledby="journey-archive-title">
        <div class="journey__archive-main">
          <p class="journey__eyebrow">The Living Archive</p>
          <template v-if="archive.status === 'undetermined'">
            <h2 id="journey-archive-title">Still observing</h2>
            <p>
              The archive has not seen enough of a pattern yet. It records
              verified contribution, not what you say you enjoy.
            </p>
          </template>
          <template v-else>
            <h2 id="journey-archive-title">
              <template v-if="archive.status === 'recognized'">
                The {{ archive.tradition.archetype }} have taken notice
              </template>
              <template v-else>
                You may be walking the Path of {{ archive.tradition.title }}
              </template>
            </h2>
            <p v-if="archive.tradition.future_view" class="journey__future">
              {{ archive.tradition.future_view }}
            </p>
          </template>
        </div>
        <div class="journey__archive-side">
          <div class="journey__observed">
            <div>
              <strong>{{ archive.observed?.contributions ?? 0 }}</strong>
              <span>verified contributions</span>
            </div>
            <div>
              <strong>{{ archive.observed?.kinds ?? 0 }}</strong>
              <span>kinds of evidence</span>
            </div>
          </div>
          <ul v-if="archive.notes?.length" class="journey__notes">
            <li v-for="note in archive.notes" :key="note">{{ note }}</li>
          </ul>
          <p class="journey__hint">An observation, not a score.</p>
        </div>
      </section>

      <section v-if="selected" class="journey__current" aria-labelledby="journey-current-title">
        <div class="journey__current-main">
          <p class="journey__eyebrow">
            Your current journey
            <template v-if="selected.journey.tradition">
              · Path of {{ selected.journey.tradition }}
            </template>
          </p>
          <h2 id="journey-current-title">{{ selected.journey.title }}</h2>
          <p>{{ selected.journey.mission }}</p>
          <p v-if="selected.journey.summary" class="journey__current-summary">
            {{ selected.journey.summary }}
          </p>
          <p v-if="selected.journey.first_quest" class="journey__current-step">
            <strong>First step:</strong> {{ selected.journey.first_quest }}
          </p>
          <div v-if="selected.journey.competencies?.length" class="journey__competencies">
            <span v-for="competency in selected.journey.competencies" :key="competency">
              {{ competency }}
            </span>
          </div>
        </div>
        <div class="journey__current-actions">
          <span class="journey__status">Current mission</span>
          <button
            type="button"
            class="btn btn--outline btn--sm"
            :disabled="changing"
            @click="showPicker = !showPicker"
          >
            {{ showPicker ? 'Keep this journey' : 'Choose another journey' }}
          </button>
        </div>
      </section>

      <section v-if="!selected || showPicker" class="journey__picker" aria-labelledby="journey-picker-title">
        <div class="journey__picker-head">
          <div>
            <p class="journey__eyebrow">{{ selected ? 'Change direction' : 'Get started' }}</p>
            <h2 id="journey-picker-title">
              {{ selected ? 'Choose another journey' : 'Choose your journey' }}
            </h2>
            <p class="journey__hint">
              Pick the mission that would get you out of bed on a Saturday. The
              competencies stay underneath.
            </p>
          </div>
          <span class="journey__count">
            {{ journeys.length }} mission{{ journeys.length === 1 ? '' : 's' }}
          </span>
        </div>
        <p v-if="!journeys.length" class="journey__empty">
          No journeys are available right now. Check back after your course team
          publishes one.
        </p>
        <ul v-else class="journey__grid">
          <li
            v-for="item in journeys"
            :key="item.id"
            class="journey__card"
            :class="{ 'journey__card--active': selected && selected.journey_id === item.id }"
          >
            <span class="journey__identity">{{ item.identity }}</span>
            <h2>{{ item.title }}</h2>
            <span v-if="item.tradition" class="journey__tradition">
              Path of {{ item.tradition }}
            </span>
            <p class="journey__mission">{{ item.mission }}</p>
            <p class="journey__summary">{{ item.summary }}</p>
            <div class="journey__competencies">
              <span v-for="competency in item.competencies" :key="competency">
                {{ competency }}
              </span>
            </div>
            <p class="journey__quest"><strong>First step:</strong> {{ item.first_quest }}</p>
            <button
              type="button"
              class="btn btn--primary btn--sm"
              :disabled="changing || (selected && selected.journey_id === item.id)"
              @click="choose(item)"
            >
              {{
                selected && selected.journey_id === item.id
                  ? 'Current journey'
                  : 'Choose this journey'
              }}
            </button>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const journeys = ref([])
const archive = ref(null)
const selected = ref(null)
const loading = ref(false)
const changing = ref(false)
const showPicker = ref(false)
const error = ref('')
const message = ref('')

async function loadJourneys() {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('/journeys')
    journeys.value = response.data.journeys || []
    selected.value = response.data.selected || null
    const archiveResponse = await axios.get('/archive/me')
    archive.value = archiveResponse.data
    if (!selected.value) {
      message.value = 'Choose a journey to see a suggested first step.'
    } else {
      message.value = ''
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load journeys.'
  } finally {
    loading.value = false
  }
}

async function choose(item) {
  changing.value = true
  error.value = ''
  message.value = ''
  try {
    const response = await axios.put('/journeys/mine', { journey_id: item.id })
    selected.value = response.data.journey
    showPicker.value = false
    message.value = `Journey set to ${item.title}.`
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not save your journey.'
  } finally {
    changing.value = false
  }
}

onMounted(loadJourneys)
</script>

<style scoped>
.journey {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1.25rem;
}

.journey__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.journey__head h1 {
  margin: 0 0 0.5rem;
}

.journey__head p {
  margin: 0;
  max-width: 70ch;
  color: var(--text-secondary);
}

.journey__archive {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
  gap: 1.25rem;
  border: 1px solid var(--border-color);
  border-left: 4px solid var(--accent);
  border-radius: 0.9rem;
  background:
    linear-gradient(135deg, var(--accent-bg), transparent 60%),
    var(--bg-secondary);
  padding: 1.15rem;
}

.journey__archive h2 {
  margin: 0.2rem 0 0.4rem;
  font-size: 1.15rem;
}

.journey__archive p {
  margin: 0;
  color: var(--text-secondary);
}

.journey__archive-side {
  display: grid;
  gap: 0.65rem;
  align-content: start;
  padding-left: 1.1rem;
  border-left: 1px solid var(--border-color);
}

.journey__observed {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
}

.journey__observed div {
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.journey__observed strong {
  display: block;
  color: var(--text-primary);
  font-size: 1.35rem;
  line-height: 1.2;
}

.journey__observed span {
  display: block;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.35;
}

.journey__notes {
  margin: 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.2rem;
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.journey__future {
  margin: 0.6rem 0 0 !important;
  font-size: 0.9rem;
  max-width: 80ch;
}

.journey__hint {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.86rem;
}

.journey__current {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  border: 1px solid var(--accent);
  border-radius: 0.9rem;
  background:
    linear-gradient(135deg, var(--accent-bg), transparent 65%),
    var(--bg-secondary);
  padding: 1.1rem;
}

.journey__current h2 {
  margin: 0.15rem 0 0.35rem;
}

.journey__current p {
  margin: 0;
  color: var(--text-secondary);
  max-width: 70ch;
}

.journey__current-summary {
  margin-top: 0.35rem !important;
  font-size: 0.9rem;
}

.journey__current-step {
  margin-top: 0.55rem !important;
  padding: 0.5rem 0.65rem;
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
  background: var(--bg-primary);
  font-size: 0.86rem;
}

.journey__current .journey__competencies {
  margin-top: 0.55rem;
}

.journey__current-actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.journey__status {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: var(--success-bg);
  color: var(--success);
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.journey__picker {
  display: grid;
  gap: 0.75rem;
}

.journey__picker-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.journey__picker-head h2 {
  margin: 0 0 0.25rem;
}

.journey__count {
  padding: 0.22rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.journey__grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.9rem;
}

.journey__card {
  border: 1px solid var(--border-color);
  border-radius: 0.9rem;
  background: var(--bg-secondary);
  padding: 1rem;
  display: grid;
  gap: 0.45rem;
  align-content: start;
}

.journey__card--active {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
  background: var(--accent-bg);
}

.journey__identity {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.journey__card h2 {
  margin: 0;
  font-size: 1.05rem;
}

.journey__mission {
  margin: 0;
  color: var(--text-primary);
  font-weight: 600;
}

.journey__summary,
.journey__quest {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.journey__tradition {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.journey__competencies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.journey__competencies span {
  padding: 0.12rem 0.42rem;
  border-radius: 999px;
  background: var(--accent-bg);
  color: var(--accent-text);
  font-size: 0.72rem;
  font-weight: 600;
}

.journey__message {
  color: var(--success);
  background: var(--success-bg);
  border: 1px solid var(--success);
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.journey__empty {
  color: var(--text-secondary);
  padding: 1rem 0;
}

@media (max-width: 900px) {
  .journey__archive {
    grid-template-columns: 1fr;
  }

  .journey__archive-side {
    padding-left: 0;
    border-left: 0;
    border-top: 1px solid var(--border-color);
    padding-top: 0.9rem;
  }
}

@media (max-width: 640px) {
  .journey__current,
  .journey__picker-head {
    flex-direction: column;
    align-items: stretch;
  }

  .journey__current-actions {
    justify-content: space-between;
  }

  .journey__observed {
    grid-template-columns: 1fr;
  }
}
</style>
