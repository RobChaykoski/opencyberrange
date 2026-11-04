<template>
  <span
    class="user-avatar"
    :class="`user-avatar--${safeStyle}`"
    :style="styleVars"
  >
    <span class="user-avatar__inner">
      <img v-if="src" :src="src" :alt="alt" />
      <span v-else class="user-avatar__initials" aria-hidden="true">{{ initials }}</span>
    </span>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  name: { type: String, default: '' },
  borderStyle: { type: String, default: 'solid' },
  borderColor: { type: String, default: 'blue' },
  size: { type: Number, default: 36 },
  alt: { type: String, default: '' },
})

const COLORS = {
  blue: '#3b82f6',
  violet: '#8b5cf6',
  emerald: '#10b981',
  amber: '#f59e0b',
  rose: '#f43f5e',
  cyan: '#06b6d4',
  slate: '#64748b',
  gold: '#d4a017',
}

const STYLES = new Set(['none', 'solid', 'dashed', 'double', 'glow', 'gradient'])

const safeStyle = computed(() => (
  STYLES.has(props.borderStyle) ? props.borderStyle : 'solid'
))

const styleVars = computed(() => {
  const color = COLORS[props.borderColor] || COLORS.blue
  const size = Math.min(Math.max(props.size, 20), 160)
  return {
    '--avatar-size': `${size}px`,
    '--avatar-color': color,
    '--avatar-font': `${Math.max(10, Math.round(size * 0.32))}px`,
  }
})

const initials = computed(() => {
  const source = String(props.name || '?').trim()
  if (!source) return '?'
  const words = source.split(/\s+/).filter(Boolean)
  if (!words.length) return '?'
  const first = Array.from(words[0])[0] || ''
  if (words.length === 1) {
    return Array.from(words[0]).slice(0, 2).join('').toUpperCase()
  }
  const last = Array.from(words[words.length - 1])[0] || ''
  return `${first}${last}`.toUpperCase()
})
</script>

<style scoped>
.user-avatar {
  display: inline-grid;
  place-items: center;
  flex-shrink: 0;
  width: var(--avatar-size);
  height: var(--avatar-size);
  border-radius: 50%;
  box-sizing: content-box;
  background: transparent;
}

.user-avatar__inner {
  display: grid;
  place-items: center;
  width: var(--avatar-size);
  height: var(--avatar-size);
  overflow: hidden;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #fff;
  font-size: var(--avatar-font);
  font-weight: 700;
  letter-spacing: 0.02em;
}

.user-avatar__inner img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar--solid {
  border: 3px solid var(--avatar-color);
}

.user-avatar--dashed {
  border: 3px dashed var(--avatar-color);
}

.user-avatar--double {
  border: 4px double var(--avatar-color);
}

.user-avatar--glow {
  border: 3px solid var(--avatar-color);
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--avatar-color) 24%, transparent),
    0 0 16px color-mix(in srgb, var(--avatar-color) 55%, transparent);
}

.user-avatar--gradient {
  padding: 3px;
  background: conic-gradient(
    from 140deg,
    var(--avatar-color),
    color-mix(in srgb, var(--avatar-color) 28%, #ffffff),
    var(--avatar-color),
    color-mix(in srgb, var(--avatar-color) 38%, #000000),
    var(--avatar-color)
  );
}

@media (prefers-reduced-motion: reduce) {
  .user-avatar {
    transition: none;
  }
}
</style>
