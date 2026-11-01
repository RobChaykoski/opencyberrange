<template>
  <div class="medallion" :class="toneClass" :title="description || label">
    <span class="medallion__ring" aria-hidden="true">
      <span class="medallion__glow"></span>
      <component :is="iconComponent" class="medallion__icon" />
    </span>
    <span class="medallion__label">{{ label }}</span>
    <span v-if="dateLabel" class="medallion__date">{{ dateLabel }}</span>
  </div>
</template>

<script setup>
import { computed, markRaw } from 'vue'
import TargetIcon from './icons/TargetIcon.vue'
import BrainIcon from './icons/BrainIcon.vue'
import CheckCircleIcon from './icons/CheckCircleIcon.vue'
import ClockIcon from './icons/ClockIcon.vue'
import ShieldCheckIcon from './icons/ShieldCheckIcon.vue'
import TrophyIcon from './icons/TrophyIcon.vue'
import FlameIcon from './icons/FlameIcon.vue'

const props = defineProps({
  type: { type: String, default: '' },
  label: { type: String, required: true },
  description: { type: String, default: '' },
  dateLabel: { type: String, default: '' },
})

const ICONS = {
  first_blood: markRaw(TargetIcon),
  no_hints: markRaw(BrainIcon),
  perfectionist: markRaw(CheckCircleIcon),
  speed_demon: markRaw(ClockIcon),
  clean_sweep: markRaw(ShieldCheckIcon),
  streak: markRaw(FlameIcon),
}

const iconComponent = computed(() => {
  if (props.type.startsWith('custom_')) return markRaw(TrophyIcon)
  return ICONS[props.type] || markRaw(TrophyIcon)
})

const toneClass = computed(() => {
  if (props.type.startsWith('custom_')) return 'medallion--custom'
  return `medallion--${props.type.replaceAll('_', '-')}`
})
</script>

<style scoped>
.medallion {
  --tone: var(--accent);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  min-width: 92px;
  max-width: 118px;
  text-align: center;
}

.medallion__ring {
  position: relative;
  display: grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 34% 28%, rgba(255, 255, 255, 0.16), transparent 48%),
    var(--bg-primary);
  border: 1px solid var(--border-color);
  box-shadow:
    inset 0 0 0 1px var(--tone),
    0 0 0 4px var(--bg-secondary),
    0 6px 16px rgba(0, 0, 0, 0.18);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.medallion:hover .medallion__ring {
  transform: translateY(-2px);
  box-shadow:
    inset 0 0 0 1px var(--tone),
    0 0 0 4px var(--bg-secondary),
    0 10px 22px rgba(0, 0, 0, 0.24);
}

.medallion__glow {
  position: absolute;
  inset: 7px;
  border-radius: 50%;
  background: var(--tone);
  opacity: 0.08;
}

.medallion__icon {
  position: relative;
  width: 24px;
  height: 24px;
  color: var(--tone);
}

.medallion__label {
  font-size: 0.74rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--text-primary);
}

.medallion__date {
  font-size: 0.65rem;
  color: var(--text-muted);
}

.medallion--first-blood { --tone: var(--warning); }
.medallion--no-hints { --tone: var(--success); }
.medallion--perfectionist { --tone: var(--accent); }
.medallion--speed-demon { --tone: #f59e0b; }
.medallion--clean-sweep { --tone: #a78bfa; }
.medallion--streak { --tone: #fb923c; }
.medallion--custom { --tone: var(--text-secondary); }

@media (prefers-reduced-motion: reduce) {
  .medallion__ring {
    transition: none;
  }
}
</style>
