<template>
  <span v-if="!value" class="privacy-text">{{ fallback }}</span>
  <span v-else-if="!privacyMode" class="privacy-text">{{ value }}</span>
  <span
    v-else-if="masked === value"
    class="privacy-text"
  >{{ value }}</span>
  <span
    v-else
    class="privacy-text privacy-text--masked"
    tabindex="0"
    title="Hover or focus to reveal"
  >
    <span class="privacy-text__mask" aria-hidden="true">{{ masked }}</span>
    <span class="privacy-text__value">{{ value }}</span>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { usePrivacy } from '../composables/usePrivacy'

const props = defineProps({
  value: { type: String, default: '' },
  type: { type: String, default: 'username' },
  fallback: { type: String, default: '' },
})

const { privacyMode, maskUsername, maskEmail } = usePrivacy()

const masked = computed(() =>
  props.type === 'email' ? maskEmail(props.value) : maskUsername(props.value)
)
</script>

<style scoped>
.privacy-text--masked {
  display: inline-block;
  cursor: help;
  border-radius: 0.2rem;
  outline-offset: 2px;
}

.privacy-text__value {
  display: none;
}

.privacy-text--masked:hover .privacy-text__mask,
.privacy-text--masked:focus .privacy-text__mask {
  display: none;
}

.privacy-text--masked:hover .privacy-text__value,
.privacy-text--masked:focus .privacy-text__value {
  display: inline;
}
</style>
