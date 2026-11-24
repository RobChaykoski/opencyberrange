<template>
  <div class="workbook-answers">
    <header class="workbook-answers__head">
      <p class="workbook-answers__eyebrow">Learning evidence</p>
      <h1>Workbook answers</h1>
      <p>
        Write a short analyst answer for an exercise. Each distinct version is
        saved as evidence and sent to an instructor for review; editing creates
        a new version instead of rewriting the old one.
      </p>
    </header>

    <p v-if="message" class="workbook-answers__message" role="status">{{ message }}</p>
    <p v-if="error" class="form-error" role="alert">{{ error }}</p>

    <section class="workbook-answers__panel">
      <label class="workbook-answers__field">
        <span>Exercise</span>
        <select v-model="selectedSlug" class="form-input" @change="loadAnswer">
          <option value="">Select an exercise with a workbook page</option>
          <option v-for="item in options" :key="item.slug" :value="item.slug">
            {{ item.track ? `${item.track} · ` : '' }}{{ item.name }}
          </option>
        </select>
      </label>

      <p v-if="loadingOptions" class="workbook-answers__note">Loading exercises...</p>
      <p v-else-if="!options.length" class="workbook-answers__note">
        No workbook exercises are available to your account yet.
      </p>

      <template v-if="selectedSlug">
        <div class="workbook-answers__meta">
          <span v-if="savedAt">Last saved {{ formatDate(savedAt) }}</span>
          <span v-else>No answer saved yet.</span>
          <span>Minimum 10 characters.</span>
        </div>

        <label class="workbook-answers__field">
          <span>Your answer</span>
          <textarea
            v-model="answer"
            class="form-input workbook-answers__textarea"
            rows="10"
            maxlength="20000"
            placeholder="What did you observe, how do you know it, what did you conclude, and what would you do next?"
          />
        </label>

        <div class="workbook-answers__actions">
          <button
            type="button"
            class="btn btn--primary btn--sm"
            :disabled="saving || answer.trim().length < 10"
            @click="saveAnswer"
          >
            {{ saving ? 'Saving...' : 'Save and submit for review' }}
          </button>
          <span class="workbook-answers__note">
            Instructor review uses the analyst-answer rubric.
          </span>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from '../api/axios'

const options = ref([])
const selectedSlug = ref('')
const answer = ref('')
const savedAt = ref(null)
const loadingOptions = ref(false)
const saving = ref(false)
const message = ref('')
const error = ref('')

function formatDate(value) {
  if (!value) return ''
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

async function loadOptions() {
  loadingOptions.value = true
  try {
    const response = await axios.get('/workbook-answers/options')
    options.value = response.data.exercises || []
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load the workbook exercises.'
  } finally {
    loadingOptions.value = false
  }
}

async function loadAnswer() {
  message.value = ''
  error.value = ''
  if (!selectedSlug.value) {
    answer.value = ''
    savedAt.value = null
    return
  }
  try {
    const response = await axios.get(`/workbook-answers/${selectedSlug.value}`)
    const item = response.data.answer
    answer.value = item?.answer_text || ''
    savedAt.value = item?.updated_at || null
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not load your saved answer.'
  }
}

async function saveAnswer() {
  if (!selectedSlug.value) return
  saving.value = true
  message.value = ''
  error.value = ''
  try {
    const response = await axios.put(`/workbook-answers/${selectedSlug.value}`, {
      answer: answer.value,
    })
    savedAt.value = response.data.answer?.updated_at || null
    message.value = response.data.created
      ? 'Answer saved and sent for instructor review.'
      : 'This version was already saved for review.'
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
  max-width: 900px;
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
  color: var(--accent);
}

.workbook-answers__head h1 {
  margin: 0 0 0.5rem;
}

.workbook-answers__head p {
  color: var(--text-muted, #64748b);
  margin: 0;
}

.workbook-answers__panel {
  display: grid;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color, #dbe3ee);
  border-radius: 0.8rem;
  background: var(--bg-secondary, #fff);
}

.workbook-answers__field {
  display: grid;
  gap: 0.35rem;
}

.workbook-answers__textarea {
  resize: vertical;
  min-height: 12rem;
  line-height: 1.5;
}

.workbook-answers__meta,
.workbook-answers__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.workbook-answers__meta,
.workbook-answers__note {
  color: var(--text-muted, #64748b);
  font-size: 0.85rem;
}

.workbook-answers__message {
  color: #166534;
  background: #dcfce7;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
}
</style>
