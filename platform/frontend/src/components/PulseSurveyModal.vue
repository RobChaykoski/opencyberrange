<template>
  <Teleport to="body">
    <div v-if="show" class="pulse-backdrop" @click.self="skip">
      <section
        class="pulse-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pulse-title"
      >
        <header class="pulse-modal__head">
          <div>
            <p class="pulse-modal__kicker">Quick pulse</p>
            <h2 id="pulse-title">How did that exercise feel?</h2>
            <p class="pulse-modal__lab">{{ labName }}</p>
          </div>
          <button type="button" class="pulse-modal__close" aria-label="Skip pulse survey" @click="skip">
            ×
          </button>
        </header>

        <div class="pulse-question">
          <p class="pulse-question__label">How difficult was this exercise?</p>
          <div class="pulse-options" role="radiogroup" aria-label="Difficulty">
            <label
              v-for="option in difficultyOptions"
              :key="option.value"
              class="pulse-option"
              :class="{ 'pulse-option--active': difficulty === option.value }"
            >
              <input v-model="difficulty" type="radio" name="pulse-difficulty" :value="option.value" />
              <span>{{ option.label }}</span>
            </label>
          </div>
        </div>

        <div class="pulse-question">
          <p class="pulse-question__label">How much did you learn?</p>
          <div class="pulse-options" role="radiogroup" aria-label="Learning">
            <label
              v-for="option in learningOptions"
              :key="option.value"
              class="pulse-option"
              :class="{ 'pulse-option--active': learning === option.value }"
            >
              <input v-model="learning" type="radio" name="pulse-learning" :value="option.value" />
              <span>{{ option.label }}</span>
            </label>
          </div>
        </div>

        <div class="pulse-question">
          <label class="pulse-question__label" for="pulse-unclear">Was anything unclear?</label>
          <textarea
            id="pulse-unclear"
            v-model="unclear"
            rows="3"
            maxlength="2000"
            placeholder="Optional. Tell your instructor what was confusing or missing."
          />
        </div>

        <p v-if="error" class="pulse-error" role="alert">{{ error }}</p>

        <footer class="pulse-modal__foot">
          <button type="button" class="btn btn--secondary btn--sm" :disabled="saving" @click="skip">
            Skip
          </button>
          <button
            type="button"
            class="btn btn--primary btn--sm"
            :disabled="saving || !difficulty || !learning"
            @click="submit"
          >
            {{ saving ? 'Saving...' : 'Submit pulse' }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from '../api/axios'

const props = defineProps({
  show: { type: Boolean, default: false },
  labId: { type: Number, default: null },
  labName: { type: String, default: '' },
  courseId: { type: [Number, String], default: null },
})

const emit = defineEmits(['done'])

const difficultyOptions = [
  { value: 1, label: 'Much too easy' },
  { value: 2, label: 'Easy' },
  { value: 3, label: 'Appropriate' },
  { value: 4, label: 'Difficult' },
  { value: 5, label: 'Much too difficult' },
]
const learningOptions = [
  { value: 1, label: 'Very little' },
  { value: 2, label: 'Little' },
  { value: 3, label: 'Moderate' },
  { value: 4, label: 'Significant' },
  { value: 5, label: 'Extensive' },
]

const difficulty = ref(null)
const learning = ref(null)
const unclear = ref('')
const saving = ref(false)
const error = ref('')

watch(() => props.show, (open) => {
  if (!open) return
  difficulty.value = null
  learning.value = null
  unclear.value = ''
  error.value = ''
})

const submit = async () => {
  if (!difficulty.value || !learning.value || !props.labId) return
  saving.value = true
  error.value = ''
  try {
    await axios.post(`/analytics/pulse/${props.labId}`, {
      difficulty: difficulty.value,
      learning: learning.value,
      unclear: unclear.value.trim() || null,
      course_id: props.courseId ? Number(props.courseId) : null,
    })
    emit('done', true)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not save your pulse response.'
  } finally {
    saving.value = false
  }
}

const skip = () => {
  if (saving.value) return
  emit('done', false)
}
</script>

<style scoped>
.pulse-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(2, 6, 23, 0.72);
}

.pulse-modal {
  width: min(560px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  padding: 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  background: var(--bg-secondary);
  box-shadow: 0 28px 80px rgba(2, 6, 23, 0.45);
}

.pulse-modal__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.pulse-modal__kicker {
  margin: 0 0 0.1rem;
  color: var(--accent);
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.pulse-modal h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.15rem;
}

.pulse-modal__lab {
  margin: 0.2rem 0 0;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.pulse-modal__close {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: transparent;
  color: var(--text-muted);
  font-size: 1.1rem;
  cursor: pointer;
}

.pulse-question + .pulse-question {
  margin-top: 0.9rem;
}

.pulse-question__label {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--text-primary);
  font-size: 0.76rem;
  font-weight: 650;
}

.pulse-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.pulse-option {
  position: relative;
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: 0.66rem;
  cursor: pointer;
}

.pulse-option input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.pulse-option--active,
.pulse-option:focus-within {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--text-primary);
}

.pulse-question textarea {
  width: 100%;
  padding: 0.55rem 0.65rem;
  border: 1px solid var(--border-color);
  border-radius: 9px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.76rem;
  resize: vertical;
}

.pulse-question textarea:focus {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.pulse-error {
  margin: 0.7rem 0 0;
  color: var(--danger);
  font-size: 0.72rem;
}

.pulse-modal__foot {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.1rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--border-color);
}
</style>
