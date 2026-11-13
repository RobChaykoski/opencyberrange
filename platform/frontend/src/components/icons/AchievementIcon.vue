<template>
  <component :is="iconComponent" class="achievement-icon" aria-hidden="true" />
</template>

<script setup>
import { computed } from 'vue'
import BrainIcon from './BrainIcon.vue'
import CheckCircleIcon from './CheckCircleIcon.vue'
import ClockIcon from './ClockIcon.vue'
import FlagIcon from './FlagIcon.vue'
import FlameIcon from './FlameIcon.vue'
import ForensicsIcon from './ForensicsIcon.vue'
import LightbulbIcon from './LightbulbIcon.vue'
import ShieldCheckIcon from './ShieldCheckIcon.vue'
import TargetIcon from './TargetIcon.vue'
import TerminalIcon from './TerminalIcon.vue'
import TrophyIcon from './TrophyIcon.vue'

const props = defineProps({
  type: { type: String, default: '' },
})

const iconComponent = computed(() => {
  const type = (props.type || '').toLowerCase()
  if (type.includes('first_blood') || type.includes('first_flag')) return FlagIcon
  if (type.includes('no_hints') || type.includes('self_reliant') || type.includes('mfa')) return ShieldCheckIcon
  if (type.includes('perfectionist') || type.includes('first_attempt') || type.includes('quiz_ace') || type.includes('quiz_platinum')) return TargetIcon
  if (type.includes('speed') || type.includes('streak')) return type.includes('speed') ? ClockIcon : FlameIcon
  if (type.includes('clean_sweep') || type.includes('level_complete')) return CheckCircleIcon
  if (type.includes('shell') || type.includes('rangebox') || type.includes('source_')) return TerminalIcon
  if (type.includes('memory') || type.includes('forensic') || type.includes('evidence') || type.includes('log_')) return ForensicsIcon
  if (type.includes('learning_hours') || type.includes('scholar') || type.includes('quiz_')) return BrainIcon
  if (type.includes('quiz_') || type.includes('provenance') || type.includes('liquidity') || type.includes('frontier')) return LightbulbIcon
  if (type.includes('comp_') || type.includes('placement') || type.includes('trophy') || type.includes('custom_')) return TrophyIcon
  return TrophyIcon
})
</script>

<style scoped>
.achievement-icon {
  width: 1.05em;
  height: 1.05em;
  flex-shrink: 0;
  vertical-align: -0.15em;
}
</style>
