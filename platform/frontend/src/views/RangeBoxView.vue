<template>
  <RangeBoxHome v-if="!ready" />
  <div v-else-if="isMobile && !mobileBypass" class="rangebox-mobile-gate">
    <h1>RangeBox desktop</h1>
    <p>
      The interactive desktop is built for a laptop or desktop with a keyboard
      and mouse. On a phone the small screen and touch keyboard make lab work
      unreliable.
    </p>
    <router-link :to="mobileViewerLink" class="rangebox-mobile-gate__primary">
      Open the full-screen desktop anyway
    </router-link>
    <router-link to="/exercises" class="rangebox-mobile-gate__secondary">
      Back to exercises
    </router-link>
  </div>
  <div v-else class="rangebox-page">
    <RangeBox
      :session-id="sessionId"
      :standalone="isStandalone"
      :image-name="imageName"
      :admin-target-user-id="adminTargetUserId"
      :lab-context="labContext"
      show-close
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from '../api/axios'
import RangeBox from '../components/RangeBox.vue'
import RangeBoxHome from './RangeBoxHome.vue'
import { useMobileView } from '../composables/useMobileView'

const route = useRoute()
const { isMobile } = useMobileView()

const sessionId = computed(() => {
  const id = route.query.session
  return id ? Number(id) : null
})

const isStandalone = computed(() => route.query.standalone === 'true')

const imageName = computed(() => route.query.image || '')

// Admin mode: viewing a student's RangeBox
const adminTargetUserId = computed(() => {
  const id = route.query.userId
  return id ? Number(id) : null
})

const ready = computed(() => sessionId.value || isStandalone.value)
const mobileBypass = computed(() => route.query.mobile === 'true')
const mobileViewerLink = computed(() => ({
  path: '/rangebox',
  query: { ...route.query, mobile: 'true' },
}))

// The RangeBox window carries the exercise context: lab name, target IPs, and
// the flag form. It is fetched here so the dock can render before the VNC
// connection finishes.
const labContext = ref(null)

async function loadLabContext() {
  if (!sessionId.value || isStandalone.value || adminTargetUserId.value) {
    labContext.value = null
    return
  }
  try {
    const { data } = await axios.get(`/rangebox/${sessionId.value}/lab`)
    labContext.value = data || null
  } catch {
    // A missing context should not break the desktop; the dock simply hides.
    labContext.value = null
  }
}

watch([sessionId, isStandalone, adminTargetUserId], loadLabContext, { immediate: true })
</script>

<style scoped>
.rangebox-page {
  position: fixed;
  inset: 0;
  height: 100vh;
  height: 100dvh;
  background: #0a0a1a;
  z-index: 9999;
  padding-bottom: env(safe-area-inset-bottom);
}

.rangebox-page :deep(.rangebox) {
  height: 100%;
  border: none;
  border-radius: 0;
  margin: 0;
}

.rangebox-page :deep(.rangebox__viewport) {
  min-height: 0;
  flex: 1;
}

.rangebox-mobile-gate {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.85rem;
  max-width: 560px;
  margin: 0 auto;
  padding: 1.5rem;
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.rangebox-mobile-gate h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
}

.rangebox-mobile-gate p {
  margin: 0;
  line-height: 1.6;
}

.rangebox-mobile-gate__primary,
.rangebox-mobile-gate__secondary {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0.55rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
}

.rangebox-mobile-gate__primary {
  background: var(--accent);
  color: #fff;
}

.rangebox-mobile-gate__secondary {
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}
</style>
