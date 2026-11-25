<template>
  <section v-if="questions.length" class="map-quiz" aria-labelledby="map-quiz-title">
    <header class="map-quiz__head">
      <div>
        <p class="map-quiz__eyebrow">Two-minute challenge</p>
        <h3 id="map-quiz-title">Can you read the snapshot?</h3>
      </div>
      <span class="map-quiz__progress">
        {{ finished ? 'Complete' : `Question ${index + 1} of ${questions.length}` }}
      </span>
    </header>

    <template v-if="!finished && current">
      <p class="map-quiz__question">{{ current.question }}</p>

      <div class="map-quiz__options" role="group" :aria-label="current.question">
        <button
          v-for="option in current.options"
          :key="option.key"
          type="button"
          class="map-quiz__option"
          :class="optionClass(option)"
          :disabled="answered"
          :aria-pressed="choice === option.key"
          @click="answer(option.key)"
        >
          <span class="map-quiz__option-mark" aria-hidden="true">{{ optionMark(option) }}</span>
          <span>{{ option.label }}</span>
        </button>
      </div>

      <p v-if="answered" class="map-quiz__feedback" :class="{ 'map-quiz__feedback--correct': isCorrect }" role="status">
        <strong>{{ isCorrect ? 'Correct.' : 'Not quite.' }}</strong>
        {{ current.explanation }}
      </p>

      <div class="map-quiz__actions">
        <button
          v-if="answered"
          type="button"
          class="btn btn--primary btn--sm"
          @click="next"
        >
          {{ index + 1 < questions.length ? 'Next question' : 'See result' }}
        </button>
        <span v-else class="map-quiz__hint">Pick an answer. Nothing is recorded.</span>
      </div>
    </template>

    <template v-else>
      <p class="map-quiz__question">
        You read the snapshot. The map is a periodic aggregate, not a live
        scoreboard.
      </p>
      <p class="map-quiz__feedback map-quiz__feedback--correct" role="status">
        <strong>{{ score }} of {{ questions.length }}</strong> correct. Try another
        round with new options.
      </p>
      <button type="button" class="btn btn--secondary btn--sm" @click="restart">
        Play again
      </button>
    </template>

    <p class="map-quiz__note">
      This is practice, not assessment. No answer, score, or identity is sent to
      the platform.
    </p>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  countries: {
    type: Array,
    default: () => [],
  },
  entriesReported: {
    type: Number,
    default: 0,
  },
  regions: {
    type: Array,
    default: () => [],
  },
})

const index = ref(0)
const choice = ref('')
const answered = ref(false)
const finished = ref(false)
const score = ref(0)
const seed = ref(0)

const numberFormat = new Intl.NumberFormat()

function formatCount(value) {
  return numberFormat.format(value || 0)
}

function formatShare(value) {
  return `${Math.round((value || 0) * 1000) / 10}%`
}

function shuffle(items, salt) {
  const result = [...items]
  let state = salt + 1
  for (let i = result.length - 1; i > 0; i -= 1) {
    state = (state * 1103515245 + 12345) % 2147483648
    const j = state % (i + 1)
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  return result
}

function shareOptions(share) {
  const correct = Math.max(1, Math.round((share || 0) * 100))
  const half = Math.max(1, Math.round(correct / 2))
  const quarter = Math.max(1, Math.round(correct / 4))
  const values = [...new Set([correct, half, quarter])]
  while (values.length < 3) {
    values.push(values[values.length - 1] + 1)
  }
  return shuffle(values.map((value) => ({
    key: `share-${value}`,
    label: `${value}%`,
    value,
  })), seed.value + 7)
}

const questions = computed(() => {
  const rows = props.countries || []
  const regions = props.regions || []
  if (rows.length < 4) return []
  const top = rows[0]
  const list = []

  const compare = rows.slice(0, Math.min(3, rows.length))
  list.push({
    id: 'compare',
    question: 'Which of these countries has the most reported hostile addresses?',
    options: shuffle(compare.map((row) => ({
      key: row.code,
      label: `${row.label} (${row.code})`,
    })), seed.value + 11),
    correct: top.code,
    explanation: `${top.label} has ${formatCount(top.count)} entries, ${formatShare(top.share)} of the snapshot. A country is where an address is registered, not where an attack happened.`,
  })

  list.push({
    id: 'share',
    question: `About what share of reported entries comes from ${top.label}?`,
    options: shareOptions(top.share),
    correct: `share-${Math.max(1, Math.round((top.share || 0) * 100))}`,
    explanation: `It is ${formatShare(top.share)} — ${formatCount(top.count)} of ${formatCount(props.entriesReported)} reported entries.`,
  })

  if (regions.length >= 3) {
    const topRegions = regions.slice(0, 3)
    list.push({
      id: 'region',
      question: 'Which region has the most reported entries in this snapshot?',
      options: shuffle(topRegions.map((region) => ({
        key: region.id,
        label: region.label,
      })), seed.value + 17),
      correct: topRegions[0].id,
      explanation: `${topRegions[0].label} has ${formatCount(topRegions[0].count)} entries, ${formatShare(topRegions[0].share)} of the snapshot. Regional totals are a coarse lens, not a blame map.`,
    })
  }

  return list
})

const current = computed(() => questions.value[index.value] || null)
const isCorrect = computed(() => !!current.value && choice.value === current.value.correct)

function answer(key) {
  if (answered.value || !current.value) return
  choice.value = key
  answered.value = true
  if (key === current.value.correct) score.value += 1
}

function optionClass(option) {
  if (!answered.value) return {}
  if (option.key === current.value.correct) return 'map-quiz__option--correct'
  if (option.key === choice.value) return 'map-quiz__option--wrong'
  return 'map-quiz__option--muted'
}

function optionMark(option) {
  if (!answered.value) return ''
  if (option.key === current.value.correct) return '✓'
  if (option.key === choice.value) return '×'
  return ''
}

function next() {
  if (index.value + 1 < questions.value.length) {
    index.value += 1
    choice.value = ''
    answered.value = false
    return
  }
  finished.value = true
}

function restart() {
  seed.value += 1
  index.value = 0
  choice.value = ''
  answered.value = false
  finished.value = false
  score.value = 0
}
</script>

<style scoped>
.map-quiz {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background:
    linear-gradient(145deg, var(--accent-bg), transparent 60%),
    var(--bg-primary);
}

.map-quiz__head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.map-quiz__eyebrow {
  margin: 0 0 0.2rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--accent-text);
}

.map-quiz__head h3 {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.map-quiz__progress {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.map-quiz__question {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.45;
}

.map-quiz__options {
  display: grid;
  gap: 0.35rem;
}

.map-quiz__option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.45rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font: inherit;
  font-size: 0.82rem;
  text-align: left;
  cursor: pointer;
}

.map-quiz__option:hover:not(:disabled),
.map-quiz__option:focus-visible {
  border-color: var(--accent);
}

.map-quiz__option:disabled {
  cursor: default;
}

.map-quiz__option--correct {
  border-color: var(--success);
  background: var(--success-bg);
}

.map-quiz__option--wrong {
  border-color: var(--danger);
  background: var(--danger-bg);
}

.map-quiz__option--muted {
  opacity: 0.55;
}

.map-quiz__option-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.1rem;
  flex-shrink: 0;
  font-weight: 700;
}

.map-quiz__feedback {
  margin: 0;
  padding: 0.55rem 0.65rem;
  border-left: 3px solid var(--warning);
  border-radius: 0 6px 6px 0;
  background: var(--warning-bg);
  color: var(--text-primary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.map-quiz__feedback--correct {
  border-left-color: var(--success);
  background: var(--success-bg);
}

.map-quiz__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.map-quiz__hint,
.map-quiz__note {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.72rem;
  line-height: 1.45;
}
</style>
