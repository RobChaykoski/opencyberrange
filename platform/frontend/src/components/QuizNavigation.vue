<template>
  <nav v-if="total > 0" class="quiz-nav" aria-label="Question navigation">
    <button
      type="button"
      class="btn btn--outline quiz-nav__btn"
      :disabled="disabled || position <= 1"
      @click="$emit('change', position - 1)"
    >
      <span aria-hidden="true">←</span> Previous question
    </button>
    <p class="quiz-nav__status" aria-live="polite">
      Question {{ position }} of {{ total }}
      <template v-if="answeredCount !== null">
        · {{ answeredCount }} of {{ total }} answered
      </template>
    </p>
    <button
      type="button"
      class="btn btn--secondary quiz-nav__btn quiz-nav__btn--next"
      :disabled="disabled || position >= total"
      @click="$emit('change', position + 1)"
    >
      Next question <span aria-hidden="true">→</span>
    </button>
  </nav>
</template>

<script setup>
defineProps({
  position: { type: Number, required: true },
  total: { type: Number, required: true },
  answeredCount: { type: Number, default: null },
  disabled: { type: Boolean, default: false },
})

defineEmits(['change'])
</script>

<style scoped>
.quiz-nav {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.quiz-nav__btn {
  justify-self: start;
  min-height: 44px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.quiz-nav__btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.quiz-nav__btn--next {
  justify-self: end;
  color: var(--text-primary);
}

.quiz-nav__status {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

@media (max-width: 640px) {
  .quiz-nav {
    grid-template-columns: 1fr 1fr;
  }

  .quiz-nav__status {
    grid-column: 1 / -1;
    grid-row: 1;
    white-space: normal;
  }

  .quiz-nav__btn {
    width: 100%;
  }

  .quiz-nav__btn--next {
    justify-self: stretch;
  }
}
</style>
