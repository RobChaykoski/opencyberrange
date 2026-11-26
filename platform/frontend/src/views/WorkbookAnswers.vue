<template>
  <div class="workbook-answers">
    <header class="workbook-answers__head">
      <p class="workbook-answers__eyebrow">Written evidence</p>
      <h1>Analyst answers</h1>
      <p>
        Write a short analyst answer for an exercise. Each distinct version is
        saved as evidence and sent to an instructor for review; editing creates
        a new version instead of rewriting the old one.
      </p>
    </header>

    <p v-if="message" class="workbook-answers__message" role="status">{{ message }}</p>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>

    <div class="workbook-answers__layout">
      <section class="workbook-answers__picker" aria-labelledby="answer-picker-title">
        <div class="workbook-answers__picker-head">
          <div>
            <p class="workbook-answers__eyebrow">Exercise library</p>
            <h2 id="answer-picker-title">Choose an exercise</h2>
          </div>
          <span class="workbook-answers__count">{{ savedCount }} saved</span>
        </div>

        <label class="workbook-answers__search">
          <span class="sr-only">Search exercises</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            v-model="query"
            type="search"
            placeholder="Search by exercise or track"
            autocomplete="off"
          />
        </label>

        <p class="workbook-answers__note" aria-live="polite">
          <template v-if="loadingOptions">Loading exercises...</template>
          <template v-else-if="!options.length">No workbook exercises are available to your account yet.</template>
          <template v-else>
            {{ filteredOptions.length }} of {{ options.length }} exercises
            <template v-if="query.trim()"> matching “{{ query.trim() }}”</template>
          </template>
        </p>

        <p v-if="!loadingOptions && options.length && !filteredOptions.length" class="workbook-answers__empty">
          No exercises match that search. Try a shorter term or clear the search.
        </p>

        <div v-else class="workbook-answers__groups">
          <section
            v-for="group in groupedOptions"
            :key="group.track"
            class="workbook-answers__group"
            :aria-labelledby="`answer-group-${group.key}`"
          >
            <h3 :id="`answer-group-${group.key}`">{{ group.track }}</h3>
            <ul>
              <li v-for="item in group.items" :key="item.slug">
                <button
                  type="button"
                  class="workbook-answers__option"
                  :class="{ 'workbook-answers__option--selected': selectedSlug === item.slug }"
                  :aria-pressed="selectedSlug === item.slug"
                  @click="selectExercise(item.slug)"
                >
                  <span class="workbook-answers__option-main">
                    <span class="workbook-answers__option-name">{{ item.name }}</span>
                    <span class="workbook-answers__option-meta">
                      <template v-if="savedFor(item.id)">
                        Saved {{ formatDate(savedFor(item.id).updated_at) }}
                      </template>
                      <template v-else>Not started</template>
                    </span>
                  </span>
                  <span
                    class="workbook-answers__state"
                    :class="savedFor(item.id) ? 'workbook-answers__state--saved' : 'workbook-answers__state--new'"
                  >
                    {{ savedFor(item.id) ? 'Saved' : 'Start' }}
                  </span>
                </button>
              </li>
            </ul>
          </section>
        </div>
      </section>

      <section class="workbook-answers__editor" aria-labelledby="answer-editor-title">
        <div v-if="!selectedSlug" class="workbook-answers__editor-empty">
          <h2 id="answer-editor-title">Pick an exercise to begin</h2>
          <p>
            Choose an exercise from the library. Your saved answer, if there is one,
            opens here and you can add a new version for review.
          </p>
        </div>

        <template v-else>
          <header class="workbook-answers__editor-head">
            <div>
              <p class="workbook-answers__eyebrow">{{ selectedOption?.track || 'Exercise' }}</p>
              <h2 id="answer-editor-title">{{ selectedOption?.name || 'Analyst answer' }}</h2>
            </div>
            <span
              class="workbook-answers__state"
              :class="savedAt ? 'workbook-answers__state--saved' : 'workbook-answers__state--new'"
            >
              {{ savedAt ? 'Saved for review' : 'Not saved yet' }}
            </span>
          </header>

          <p class="workbook-answers__note">
            <template v-if="savedAt">
              Last saved {{ formatDate(savedAt) }}. Editing and saving adds a new version.
            </template>
            <template v-else>
              No answer saved for this exercise yet.
            </template>
          </p>

          <label class="workbook-answers__field">
            <span>Your answer</span>
            <textarea
              v-model="answer"
              class="form-input workbook-answers__textarea"
              rows="12"
              maxlength="20000"
              :disabled="loadingAnswer"
              aria-describedby="answer-help answer-count"
              placeholder="What did you observe, how do you know it, what did you conclude, and what would you do next?"
            />
          </label>

          <div class="workbook-answers__editor-meta">
            <span id="answer-help">Write at least 10 characters. Saving sends this version to instructor review.</span>
            <span id="answer-count">{{ answer.length.toLocaleString() }} / 20,000</span>
          </div>

          <div class="workbook-answers__actions">
            <button
              type="button"
              class="btn btn--primary"
              :disabled="saving || loadingAnswer || !canSave"
              @click="saveAnswer"
            >
              {{ saving ? 'Saving...' : 'Save and submit for review' }}
            </button>
            <span v-if="!canSave" class="workbook-answers__note">
              Write at least 10 characters to enable saving.
            </span>
            <span v-else class="workbook-answers__note">
              Instructor review uses the analyst-answer rubric.
            </span>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import axios from '../api/axios'

const options = ref([])
const answers = ref([])
const selectedSlug = ref('')
const answer = ref('')
const savedAt = ref(null)
const query = ref('')
const loadingOptions = ref(false)
const loadingAnswer = ref(false)
const saving = ref(false)
const message = ref('')
const error = ref('')
let answerRequest = 0

const savedByLabId = computed(() => {
  const map = new Map()
  for (const row of answers.value) map.set(row.lab_id, row)
  return map
})

const savedCount = computed(() => answers.value.length)
const selectedOption = computed(
  () => options.value.find((item) => item.slug === selectedSlug.value) || null
)
const canSave = computed(
  () => !loadingAnswer.value && answer.value.trim().length >= 10
)

const filteredOptions = computed(() => {
  const term = query.value.trim().toLowerCase()
  if (!term) return options.value
  return options.value.filter((item) =>
    `${item.name} ${item.track || ''}`.toLowerCase().includes(term)
  )
})

const groupedOptions = computed(() => {
  const groups = new Map()
  for (const item of filteredOptions.value) {
    const track = item.track || 'Other exercises'
    if (!groups.has(track)) groups.set(track, [])
    groups.get(track).push(item)
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([track, items]) => ({
      track,
      key: track.toLowerCase().replace(/[^a-z0-9]+/g, '-'),
      items: [...items].sort((a, b) => a.name.localeCompare(b.name)),
    }))
})

function savedFor(labId) {
  return savedByLabId.value.get(labId) || null
}

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadOptions() {
  loadingOptions.value = true
  error.value = ''
  const [optionsResult, answersResult] = await Promise.allSettled([
    axios.get('/workbook-answers/options'),
    axios.get('/workbook-answers'),
  ])

  if (optionsResult.status === 'fulfilled') {
    options.value = optionsResult.value.data.exercises || []
  } else {
    error.value =
      optionsResult.reason?.response?.data?.detail ||
      'Could not load the workbook exercises.'
  }

  if (answersResult.status === 'fulfilled') {
    answers.value = answersResult.value.data.answers || []
  }

  loadingOptions.value = false

  if (options.value.length && !selectedSlug.value) {
    const recent = answers.value[0]
    const match = recent
      ? options.value.find((item) => item.id === recent.lab_id)
      : null
    if (match) {
      selectedSlug.value = match.slug
      await loadAnswer()
    }
  }
}

async function loadAnswer() {
  message.value = ''
  error.value = ''
  if (!selectedSlug.value) {
    answerRequest += 1
    answer.value = ''
    savedAt.value = null
    return
  }
  const request = ++answerRequest
  loadingAnswer.value = true
  answer.value = ''
  savedAt.value = null
  try {
    const response = await axios.get(`/workbook-answers/${selectedSlug.value}`)
    if (request !== answerRequest) return
    const item = response.data.answer
    answer.value = item?.answer_text || ''
    savedAt.value = item?.updated_at || null
  } catch (err) {
    if (request !== answerRequest) return
    error.value = err.response?.data?.detail || 'Could not load your saved answer.'
  } finally {
    if (request === answerRequest) loadingAnswer.value = false
  }
}

function selectExercise(slug) {
  if (slug === selectedSlug.value) return
  selectedSlug.value = slug
  loadAnswer()
}

async function saveAnswer() {
  const slug = selectedSlug.value
  if (!slug || !canSave.value) return
  saving.value = true
  message.value = ''
  error.value = ''
  try {
    const response = await axios.put(`/workbook-answers/${slug}`, {
      answer: answer.value,
    })
    const saved = response.data.answer
    if (saved) {
      answers.value = [
        saved,
        ...answers.value.filter((row) => row.lab_id !== saved.lab_id),
      ]
      if (selectedSlug.value === slug) savedAt.value = saved.updated_at || savedAt.value
    }
    if (selectedSlug.value === slug) {
      message.value = response.data.created
        ? 'Answer saved and sent for instructor review.'
        : 'This version was already saved for review.'
    }
  } catch (err) {
    error.value =
      err.response?.data?.detail || 'Could not save the answer. Check the length and try again.'
  } finally {
    saving.value = false
  }
}

onMounted(loadOptions)
</script>

<style scoped>
.workbook-answers {
  max-width: 1180px;
  margin: 0 auto;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
}

.workbook-answers__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.workbook-answers__head h1 {
  margin: 0 0 0.5rem;
}

.workbook-answers__head p {
  margin: 0;
  max-width: 72ch;
  color: var(--text-secondary);
}

.workbook-answers__layout {
  display: grid;
  grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  gap: 1rem;
  align-items: start;
}

.workbook-answers__picker,
.workbook-answers__editor {
  border: 1px solid var(--border-color);
  border-radius: 0.9rem;
  background: var(--bg-secondary);
  padding: 1rem;
}

.workbook-answers__picker {
  display: grid;
  gap: 0.75rem;
}

.workbook-answers__picker-head,
.workbook-answers__editor-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.workbook-answers__picker-head h2,
.workbook-answers__editor-head h2 {
  margin: 0;
  font-size: 1rem;
}

.workbook-answers__count {
  padding: 0.22rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}

.workbook-answers__search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
}

.workbook-answers__search:focus-within {
  border-color: var(--accent);
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.workbook-answers__search svg {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  color: var(--text-muted);
}

.workbook-answers__search input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  font-size: 0.85rem;
}

.workbook-answers__search input::placeholder {
  color: var(--text-muted);
}

.workbook-answers__groups {
  display: grid;
  gap: 0.85rem;
  max-height: min(58vh, 560px);
  overflow-y: auto;
  padding-right: 0.25rem;
}

.workbook-answers__group h3 {
  margin: 0 0 0.35rem;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.workbook-answers__group ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.35rem;
}

.workbook-answers__option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.55rem 0.6rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.workbook-answers__option:hover {
  border-color: var(--accent);
}

.workbook-answers__option:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.workbook-answers__option--selected {
  border-color: var(--accent);
  background: var(--accent-bg);
  box-shadow: inset 0 0 0 1px var(--accent);
}

.workbook-answers__option-main {
  display: grid;
  gap: 0.1rem;
  min-width: 0;
}

.workbook-answers__option-name {
  font-size: 0.84rem;
  font-weight: 600;
  overflow-wrap: anywhere;
}

.workbook-answers__option-meta {
  color: var(--text-muted);
  font-size: 0.72rem;
}

.workbook-answers__state {
  flex-shrink: 0;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.workbook-answers__state--saved {
  background: var(--success-bg);
  color: var(--success);
}

.workbook-answers__state--new {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.workbook-answers__editor {
  display: grid;
  gap: 0.75rem;
  min-height: 26rem;
}

.workbook-answers__editor-empty {
  display: grid;
  gap: 0.4rem;
  align-content: center;
  justify-items: start;
  min-height: 22rem;
  padding: 1rem;
}

.workbook-answers__editor-empty h2 {
  margin: 0;
  font-size: 1.05rem;
}

.workbook-answers__editor-empty p {
  margin: 0;
  max-width: 52ch;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.workbook-answers__field {
  display: grid;
  gap: 0.35rem;
}

.workbook-answers__field > span {
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
}

.workbook-answers__textarea {
  resize: vertical;
  min-height: 16rem;
  line-height: 1.5;
}

.workbook-answers__editor-meta,
.workbook-answers__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
}

.workbook-answers__note,
.workbook-answers__editor-meta {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.workbook-answers__editor-meta span:first-child {
  flex: 1 1 18rem;
}

.workbook-answers__actions {
  justify-content: flex-start;
  padding-top: 0.25rem;
  border-top: 1px solid var(--border-color);
}

.workbook-answers__actions .btn {
  min-height: 44px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.workbook-answers__actions .btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.workbook-answers__empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.workbook-answers__message {
  color: var(--success);
  background: var(--success-bg);
  border: 1px solid var(--success);
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}

@media (max-width: 900px) {
  .workbook-answers__layout {
    grid-template-columns: 1fr;
  }

  .workbook-answers__groups {
    max-height: 42vh;
  }
}

@media (max-width: 640px) {
  .workbook-answers {
    padding: 1rem;
  }

  .workbook-answers__picker-head,
  .workbook-answers__editor-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .workbook-answers__state,
  .workbook-answers__count {
    align-self: flex-start;
  }

  .workbook-answers__actions .btn {
    width: 100%;
  }
}
</style>
