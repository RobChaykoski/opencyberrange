<template>
  <section class="quiz-submit" :aria-labelledby="titleId">
    <div class="quiz-submit__copy">
      <h3 :id="titleId">{{ title }}</h3>
      <p v-if="description" class="quiz-submit__description">{{ description }}</p>
      <p v-if="warning" class="quiz-submit__warning">{{ warning }}</p>
    </div>
    <div class="quiz-submit__actions">
      <template v-if="!confirming">
        <button
          ref="triggerButton"
          type="button"
          class="btn btn--primary quiz-submit__btn"
          :disabled="submitting || disabled"
          @click="$emit('update:confirming', true)"
        >
          {{ submitting ? 'Submitting...' : submitLabel }}
        </button>
      </template>
      <template v-else>
        <p class="quiz-submit__confirm" role="alert">{{ confirmText }}</p>
        <button
          ref="confirmButton"
          type="button"
          class="btn btn--primary quiz-submit__btn"
          :disabled="submitting || disabled"
          @click="$emit('submit')"
        >
          {{ submitting ? 'Submitting...' : confirmLabel }}
        </button>
        <button
          type="button"
          class="btn btn--outline quiz-submit__btn"
          :disabled="submitting"
          @click="$emit('update:confirming', false)"
        >
          {{ cancelLabel }}
        </button>
      </template>
    </div>
  </section>
</template>

<script setup>
import { nextTick, ref, useId, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Finished answering?' },
  description: { type: String, default: '' },
  warning: { type: String, default: '' },
  submitLabel: { type: String, default: 'Submit' },
  confirmText: { type: String, default: 'Submit now?' },
  confirmLabel: { type: String, default: 'Yes, submit' },
  cancelLabel: { type: String, default: 'Keep working' },
  confirming: { type: Boolean, default: false },
  submitting: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

defineEmits(['submit', 'update:confirming'])

const titleId = useId()
const triggerButton = ref(null)
const confirmButton = ref(null)

watch(
  () => props.confirming,
  async (value) => {
    await nextTick()
    if (value) confirmButton.value?.focus()
    else triggerButton.value?.focus()
  }
)
</script>

<style scoped>
.quiz-submit {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 0.9rem;
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--accent);
  border-radius: 0.75rem;
  background: var(--bg-primary);
}

.quiz-submit__copy h3 {
  margin: 0 0 0.2rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.quiz-submit__description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.5;
}

.quiz-submit__warning {
  margin: 0.35rem 0 0;
  color: var(--warning);
  font-size: 0.84rem;
  line-height: 1.5;
}

.quiz-submit__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.quiz-submit__confirm {
  flex-basis: 100%;
  margin: 0 0 0.15rem;
  color: var(--text-primary);
  font-size: 0.84rem;
  font-weight: 600;
  text-align: right;
}

.quiz-submit__btn {
  min-height: 44px;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.quiz-submit__btn:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

@media (max-width: 720px) {
  .quiz-submit {
    flex-direction: column;
    align-items: stretch;
  }

  .quiz-submit__actions {
    justify-content: stretch;
  }

  .quiz-submit__confirm {
    text-align: left;
  }

  .quiz-submit__btn {
    width: 100%;
  }
}
</style>
