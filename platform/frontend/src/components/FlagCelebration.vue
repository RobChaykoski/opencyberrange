<template>
  <Teleport to="body">
    <Transition name="fc-fade">
      <div
        v-if="show"
        class="fc-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="fc-title"
        @click.self="$emit('close')"
      >
        <canvas
          v-if="showCanvas"
          ref="canvasEl"
          class="fc-canvas"
          aria-hidden="true"
        ></canvas>

        <div v-if="effect === 'confetti'" class="fc-confetti" aria-hidden="true">
          <span
            v-for="piece in confetti"
            :key="piece.id"
            class="fc-confetti__piece"
            :style="piece.style"
          ></span>
        </div>

        <div class="fc-card">
          <div class="fc-flag" aria-hidden="true">
            <span class="fc-flag__pole"></span>
            <span class="fc-flag__cloth"><FlagIcon /></span>
          </div>

          <p class="fc-kicker">{{ headline }}</p>
          <h2 id="fc-title" class="fc-title">Flag captured</h2>
          <p class="fc-lab">{{ labName }}</p>

          <div class="fc-stats">
            <div class="fc-stat">
              <span class="fc-stat__value">{{ formatDuration(timeSeconds) }}</span>
              <span class="fc-stat__label">time to solve</span>
            </div>
            <div class="fc-stat">
              <span class="fc-stat__value">{{ attempts }}</span>
              <span class="fc-stat__label">{{ attempts === 1 ? 'attempt' : 'attempts' }}</span>
            </div>
            <div class="fc-stat">
              <span class="fc-stat__value">{{ hintsUsed }}</span>
              <span class="fc-stat__label">{{ hintsUsed === 1 ? 'hint' : 'hints' }}</span>
            </div>
          </div>

          <div v-if="newAchievements.length" class="fc-achievements">
            <p class="fc-achievements__title">
              {{ newAchievements.length === 1 ? 'New badge unlocked' : `${newAchievements.length} new badges unlocked` }}
            </p>
            <div class="fc-achievements__list">
              <AchievementMedallion
                v-for="achievement in newAchievements"
                :key="achievement.id"
                :type="achievement.type"
                :label="achievement.label"
                :description="achievement.description"
              />
            </div>
          </div>

          <div class="fc-actions">
            <button
              ref="primaryButton"
              type="button"
              class="btn btn--primary"
              @click="$emit('next')"
            >
              {{ nextLabel }}
            </button>
            <button type="button" class="btn btn--outline" @click="$emit('close')">
              Keep exploring
            </button>
          </div>
          <p class="fc-hint">Press Esc to close</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import FlagIcon from './icons/FlagIcon.vue'
import AchievementMedallion from './AchievementMedallion.vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  headline: { type: String, default: 'Flag captured' },
  labName: { type: String, default: '' },
  timeSeconds: { type: Number, default: 0 },
  attempts: { type: Number, default: 0 },
  hintsUsed: { type: Number, default: 0 },
  nextLabel: { type: String, default: 'Next objective' },
  newAchievements: { type: Array, default: () => [] },
  // fireworks | matrix | confetti | off. The profile preference chooses this.
  effect: { type: String, default: 'fireworks' },
})

const emit = defineEmits(['close', 'next'])

const primaryButton = ref(null)
const confetti = ref([])
const canvasEl = ref(null)
const reducedMotion = ref(false)

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#a78bfa', '#06b6d4', '#f472b6']
const FIREWORK_COLORS = ['#22c55e', '#38bdf8', '#f59e0b', '#a78bfa', '#f472b6', '#facc15']
const MATRIX_GLYPHS = '01ABCDEF#$%&@*+=-<>{}[]'

const prefersReducedMotion = () =>
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

const showCanvas = computed(
  () =>
    props.show &&
    !reducedMotion.value &&
    (props.effect === 'fireworks' || props.effect === 'matrix')
)

let ctx = null
let rafId = 0
let canvasWidth = 0
let canvasHeight = 0
let particles = []
let matrixDrops = []
let lastBurstAt = 0

const makeConfetti = () => {
  if (prefersReducedMotion()) return []
  return Array.from({ length: 48 }, (_, index) => {
    const size = 5 + Math.random() * 6
    return {
      id: index,
      style: {
        left: `${Math.random() * 100}%`,
        width: `${size}px`,
        height: `${size * (1.3 + Math.random() * 0.6)}px`,
        background: COLORS[index % COLORS.length],
        animationDelay: `${Math.random() * 0.35}s`,
        animationDuration: `${1.4 + Math.random() * 1.3}s`,
        '--fc-drift': `${(Math.random() - 0.5) * 280}px`,
        '--fc-spin': `${360 + Math.random() * 720}deg`,
      },
    }
  })
}

function resizeCanvas() {
  const canvas = canvasEl.value
  if (!canvas) return
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  canvasWidth = canvas.clientWidth || window.innerWidth
  canvasHeight = canvas.clientHeight || window.innerHeight
  canvas.width = Math.floor(canvasWidth * dpr)
  canvas.height = Math.floor(canvasHeight * dpr)
  ctx = canvas.getContext('2d')
  if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
}

function burst(x, y, count = 56) {
  for (let index = 0; index < count; index += 1) {
    const angle = Math.random() * Math.PI * 2
    const speed = 1.6 + Math.random() * 4.2
    particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      decay: 0.008 + Math.random() * 0.012,
      size: 1.4 + Math.random() * 2.1,
      color: FIREWORK_COLORS[Math.floor(Math.random() * FIREWORK_COLORS.length)],
    })
  }
}

function drawFireworks(now) {
  if (!ctx) return
  ctx.clearRect(0, 0, canvasWidth, canvasHeight)
  ctx.globalCompositeOperation = 'lighter'
  if (now - lastBurstAt > 520) {
    burst(
      canvasWidth * (0.15 + Math.random() * 0.7),
      canvasHeight * (0.12 + Math.random() * 0.5)
    )
    lastBurstAt = now
  }
  particles = particles.filter((particle) => {
    particle.x += particle.vx
    particle.y += particle.vy
    particle.vy += 0.035
    particle.vx *= 0.992
    particle.vy *= 0.992
    particle.life -= particle.decay
    if (particle.life <= 0) return false
    ctx.globalAlpha = Math.max(particle.life, 0)
    ctx.fillStyle = particle.color
    ctx.beginPath()
    ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
    ctx.fill()
    return true
  })
  ctx.globalAlpha = 1
  ctx.globalCompositeOperation = 'source-over'
  rafId = window.requestAnimationFrame(drawFireworks)
}

function initMatrix() {
  const columnWidth = 16
  const columns = Math.max(1, Math.ceil(canvasWidth / columnWidth))
  matrixDrops = Array.from({ length: columns }, () => ({
    y: Math.random() * canvasHeight,
    speed: 1.2 + Math.random() * 3.4,
  }))
}

function drawMatrix() {
  if (!ctx) return
  ctx.fillStyle = 'rgba(2, 6, 23, 0.14)'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)
  ctx.font = '15px "JetBrains Mono", ui-monospace, monospace'
  matrixDrops.forEach((drop, index) => {
    const glyph = MATRIX_GLYPHS[Math.floor(Math.random() * MATRIX_GLYPHS.length)]
    ctx.fillStyle = Math.random() > 0.965 ? '#d1fae5' : '#22c55e'
    ctx.fillText(glyph, index * 16 + 4, drop.y)
    drop.y += drop.speed
    if (drop.y > canvasHeight && Math.random() > 0.975) {
      drop.y = 0
      drop.speed = 1.2 + Math.random() * 3.4
    }
  })
  rafId = window.requestAnimationFrame(drawMatrix)
}

function stopEffect() {
  if (rafId) window.cancelAnimationFrame(rafId)
  rafId = 0
  particles = []
  matrixDrops = []
  if (ctx) ctx.clearRect(0, 0, canvasWidth, canvasHeight)
}

function startEffect() {
  stopEffect()
  if (!showCanvas.value) return
  resizeCanvas()
  if (!ctx) return
  lastBurstAt = 0
  if (props.effect === 'fireworks') {
    burst(canvasWidth * 0.3, canvasHeight * 0.28)
    burst(canvasWidth * 0.72, canvasHeight * 0.36)
    rafId = window.requestAnimationFrame(drawFireworks)
  } else if (props.effect === 'matrix') {
    initMatrix()
    rafId = window.requestAnimationFrame(drawMatrix)
  }
}

function onResize() {
  if (!showCanvas.value) return
  resizeCanvas()
  if (props.effect === 'matrix') initMatrix()
}

const formatDuration = (seconds) => {
  if (!seconds || seconds < 0) return '—'
  const total = Math.round(seconds)
  const minutes = Math.floor(total / 60)
  const remainder = total % 60
  if (minutes === 0) return `${remainder}s`
  return `${minutes}m ${String(remainder).padStart(2, '0')}s`
}

const onKeydown = (event) => {
  if (event.key === 'Escape' && props.show) emit('close')
}

watch(
  [() => props.show, () => props.effect],
  async ([visible]) => {
    if (typeof document !== 'undefined') {
      document.body.style.overflow = visible ? 'hidden' : ''
    }
    reducedMotion.value = prefersReducedMotion()
    if (visible) {
      confetti.value = props.effect === 'confetti' ? makeConfetti() : []
      await nextTick()
      startEffect()
      primaryButton.value?.focus()
    } else {
      stopEffect()
      confetti.value = []
    }
  }
)

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', onResize)
  stopEffect()
  if (typeof document !== 'undefined') document.body.style.overflow = ''
})
</script>

<style scoped>
.fc-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  place-items: center;
  padding: 1.25rem;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(6px);
}

.fc-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.85;
}

.fc-card {
  position: relative;
  z-index: 2;
  width: min(560px, 100%);
  max-height: calc(100vh - 2.5rem);
  overflow-y: auto;
  padding: 2rem 1.75rem 1.5rem;
  text-align: center;
  background:
    radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.22), transparent 55%),
    var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
}

.fc-flag {
  position: relative;
  width: 74px;
  height: 74px;
  margin: 0 auto 0.35rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: var(--success);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  box-shadow: inset 0 0 0 2px var(--success), 0 10px 30px rgba(34, 197, 94, 0.25);
}

.fc-flag__pole {
  position: absolute;
  bottom: 14px;
  left: 50%;
  width: 2px;
  height: 30px;
  background: var(--text-muted);
  border-radius: 2px;
}

.fc-flag__cloth {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  transform-origin: left center;
  animation: fc-wave 1.7s ease-in-out infinite;
}

.fc-flag__cloth :deep(svg) {
  width: 30px;
  height: 30px;
}

@keyframes fc-wave {
  0%, 100% { transform: rotate(-2deg) skewY(0deg); }
  50% { transform: rotate(2deg) skewY(-3deg); }
}

.fc-kicker {
  margin: 1rem 0 0.1rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--success);
}

.fc-title {
  margin: 0;
  font-size: clamp(2rem, 6vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.fc-lab {
  margin: 0.45rem 0 1.25rem;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.fc-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
  margin: 0 auto 1.25rem;
  max-width: 380px;
}

.fc-stat {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  padding: 0.65rem 0.4rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-primary);
}

.fc-stat__value {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.fc-stat__label {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.fc-achievements {
  margin: 0 0 1.25rem;
  padding: 0.9rem 0.75rem 0.4rem;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.fc-achievements__title {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--warning);
}

.fc-achievements__list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}

.fc-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.6rem;
}

.fc-hint {
  margin: 0.9rem 0 0;
  font-size: 0.68rem;
  color: var(--text-muted);
}

.fc-confetti {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: hidden;
  pointer-events: none;
}

.fc-confetti__piece {
  position: absolute;
  top: -16px;
  border-radius: 2px;
  opacity: 0.95;
  animation-name: fc-fall;
  animation-timing-function: cubic-bezier(0.15, 0.7, 0.35, 1);
  animation-fill-mode: forwards;
}

@keyframes fc-fall {
  0% { transform: translate(0, 0) rotate(0deg); opacity: 1; }
  100% { transform: translate(var(--fc-drift), 108vh) rotate(var(--fc-spin)); opacity: 0; }
}

.fc-fade-enter-active,
.fc-fade-leave-active {
  transition: opacity 0.18s ease;
}

.fc-fade-enter-from,
.fc-fade-leave-to {
  opacity: 0;
}

.fc-fade-enter-active .fc-card {
  animation: fc-pop 0.28s cubic-bezier(0.2, 0.9, 0.3, 1.2);
}

@keyframes fc-pop {
  from { transform: scale(0.92); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@media (max-width: 520px) {
  .fc-card {
    padding: 1.5rem 1rem 1.25rem;
  }

  .fc-stats {
    gap: 0.4rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fc-confetti,
  .fc-canvas,
  .fc-flag__cloth {
    display: none;
  }

  .fc-fade-enter-active .fc-card {
    animation: none;
  }
}
</style>
