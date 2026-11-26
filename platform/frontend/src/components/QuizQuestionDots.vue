<template>
  <div v-if="total > 0" class="quiz-dots" role="group" aria-label="Jump to a question">
    <button
      v-for="number in total"
      :key="number"
      type="button"
      class="quiz-dot"
      :class="{
        'quiz-dot--current': number === position,
        'quiz-dot--answered': answeredSet.has(number),
      }"
      :disabled="disabled"
      :aria-label="`Question ${number}${answeredSet.has(number) ? ', answered' : ', not answered'}`"
      :aria-current="number === position ? 'true' : undefined"
      @click="$emit('jump', number)"
    >
      {{ number }}
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, required: true },
  position: { type: Number, default: 1 },
  answeredPositions: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
})

defineEmits(['jump'])

const answeredSet = computed(() => new Set(props.answeredPositions))
</script>

<style scoped>
.quiz-dots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin: 0.8rem 0;
}

.quiz-dot {
  min-width: 2.25rem;
  height: 2.25rem;
  padding: 0 0.35rem;
  border-radius: 0.4rem;
  border: 1px solid var(--border-color);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}

.quiz-dot:hover:not(:disabled) {
  border-color: var(--accent);
}

.quiz-dot:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.quiz-dot:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.quiz-dot--answered {
  background: var(--accent-bg);
  color: var(--text-primary);
}

.quiz-dot--current {
  border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent);
  color: var(--text-primary);
  font-weight: 700;
}
</style>
