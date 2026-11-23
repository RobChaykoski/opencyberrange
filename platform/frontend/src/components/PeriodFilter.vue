<template>
  <div class="period-filter" role="group" aria-label="Reporting period">
    <span class="period-filter__label">Period</span>
    <div class="period-filter__pills">
      <button
        v-for="item in presets"
        :key="item.key"
        type="button"
        class="period-filter__pill"
        :class="{ 'period-filter__pill--active': preset === item.key }"
        :aria-pressed="preset === item.key"
        @click="$emit('update:preset', item.key)"
      >
        {{ item.label }}
      </button>
    </div>
    <div v-if="preset === 'custom'" class="period-filter__custom">
      <label class="period-filter__field">
        <span>From</span>
        <input
          type="datetime-local"
          :value="customStart"
          @input="$emit('update:custom-start', $event.target.value)"
        />
      </label>
      <span class="period-filter__separator">to</span>
      <label class="period-filter__field">
        <span>To</span>
        <input
          type="datetime-local"
          :value="customEnd"
          @input="$emit('update:custom-end', $event.target.value)"
        />
      </label>
    </div>
  </div>
</template>

<script setup>
import { PERIOD_PRESETS } from '../composables/usePeriod'

defineProps({
  preset: { type: String, default: '7d' },
  customStart: { type: String, default: '' },
  customEnd: { type: String, default: '' },
  presets: { type: Array, default: () => PERIOD_PRESETS },
})

defineEmits(['update:preset', 'update:custom-start', 'update:custom-end'])
</script>

<style scoped>
.period-filter {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem 0.6rem;
  min-width: 0;
}

.period-filter__label {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.period-filter__pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.period-filter__pill {
  padding: 0.25rem 0.55rem;
  border: 1px solid var(--border-color);
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}

.period-filter__pill:hover {
  border-color: var(--accent);
  color: var(--text-primary);
}

.period-filter__pill:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.period-filter__pill--active {
  border-color: var(--accent);
  background: var(--accent-bg);
  color: var(--accent-text);
}

.period-filter__custom {
  display: flex;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.period-filter__field {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  color: var(--text-muted);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.period-filter__field input {
  padding: 0.25rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 0.72rem;
}

.period-filter__field input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 1px;
}

.period-filter__separator {
  padding-bottom: 0.3rem;
  color: var(--text-muted);
  font-size: 0.7rem;
}

@media (max-width: 640px) {
  .period-filter,
  .period-filter__pills {
    width: 100%;
  }

  .period-filter__pill {
    min-height: 36px;
  }
}
</style>
