<template>
  <div class="journey">
    <header class="journey__head">
      <p class="journey__eyebrow">Direction, not a score</p>
      <h1>Who are you trying to become?</h1>
      <p>
        Do not declare an identity. Choose a mission, and the Living Archive
        observes what your verified work becomes. You can change missions; your
        evidence stays with you.
      </p>
    </header>

    <p v-if="message" class="journey__message" role="status">{{ message }}</p>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="journey__empty">Loading journeys...</p>

    <template v-else>
      <section v-if="archive" class="journey__archive">
        <p class="journey__eyebrow">The Living Archive</p>
        <template v-if="archive.status === 'undetermined'">
          <h2>Still observing</h2>
          <p>
            The archive has not seen enough of a pattern yet. It records
            verified contribution, not what you say you enjoy.
          </p>
        </template>
        <template v-else>
          <h2 v-if="archive.status === 'recognized'">
            The {{ archive.tradition.archetype }} have taken notice
          </h2>
          <h2 v-else>
            You may be walking the Path of {{ archive.tradition.title }}
          </h2>
          <p v-if="archive.tradition.future_view" class="journey__future">
            {{ archive.tradition.future_view }}
          </p>
        </template>
        <ul class="journey__notes">
          <li v-for="note in archive.notes" :key="note">{{ note }}</li>
        </ul>
        <p class="journey__hint">
          {{ archive.observed.contributions }} verified contributions across
          {{ archive.observed.kinds }} kinds. An observation, not a score.
        </p>
      </section>
      <section v-if="selected" class="journey__current">
        <div>
          <p class="journey__eyebrow">Your current journey</p>
          <h2>{{ selected.journey.title }}</h2>
          <p>{{ selected.journey.mission }}</p>
        </div>
        <button
          type="button"
          class="btn btn--outline btn--sm"
          :disabled="changing"
          @click="showPicker = !showPicker"
        >
          {{ showPicker ? 'Keep this journey' : 'Choose another journey' }}
        </button>
      </section>

      <section v-if="!selected || showPicker" class="journey__picker">
        <p class="journey__hint">
          Pick the mission that would get you out of bed on a Saturday. The
          competencies stay underneath.
        </p>
        <ul class="journey__grid">
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
  color: var(--accent);
}

.journey__head h1 {
  margin: 0 0 0.5rem;
}

.journey__head p {
  margin: 0;
  max-width: 70ch;
  color: var(--text-muted, #64748b);
}

.journey__current {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
  border: 1px solid var(--accent, #2563eb);
  border-radius: 0.9rem;
  background: var(--surface, #fff);
  padding: 1.1rem;
}

.journey__current h2 {
  margin: 0.15rem 0 0.35rem;
}

.journey__current p {
  margin: 0;
}

.journey__archive {
  border: 1px solid var(--border, #dbe3ee);
  border-left: 4px solid var(--accent, #2563eb);
  border-radius: 0.9rem;
  background: linear-gradient(135deg, #f8fbff, #ffffff);
  padding: 1rem;
}

.journey__archive h2 {
  margin: 0.2rem 0 0.4rem;
}

.journey__notes {
  margin: 0.5rem 0;
  padding-left: 1.1rem;
  display: grid;
  gap: 0.25rem;
}

.journey__future {
  margin: 0.6rem 0 0;
  color: var(--text-muted, #64748b);
  font-size: 0.9rem;
  max-width: 80ch;
}

.journey__hint {
  margin: 0 0 0.75rem;
  color: var(--text-muted, #64748b);
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
  border: 1px solid var(--border, #dbe3ee);
  border-radius: 0.9rem;
  background: var(--surface, #fff);
  padding: 1rem;
  display: grid;
  gap: 0.45rem;
  align-content: start;
}

.journey__card--active {
  border-color: var(--accent, #2563eb);
  box-shadow: inset 0 0 0 1px var(--accent, #2563eb);
}

.journey__identity {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
}

.journey__card h2 {
  margin: 0;
  font-size: 1.05rem;
}

.journey__mission {
  margin: 0;
  font-weight: 600;
}

.journey__summary,
.journey__quest {
  margin: 0;
  font-size: 0.88rem;
  color: var(--text-muted, #64748b);
}

.journey__tradition {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--text-muted, #64748b);
}

.journey__competencies {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.journey__competencies span {
  padding: 0.12rem 0.42rem;
  border-radius: 999px;
  background: var(--accent-soft, #e0ecff);
  color: var(--accent, #2563eb);
  font-size: 0.72rem;
  font-weight: 600;
}

.journey__message {
  color: #166534;
  background: #dcfce7;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.journey__empty {
  color: var(--text-muted, #64748b);
  padding: 1rem 0;
}
</style>
