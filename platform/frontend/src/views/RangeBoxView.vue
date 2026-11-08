<template>
  <RangeBoxHome v-if="!ready" />
  <div v-else class="rangebox-page">
    <RangeBox
      :session-id="sessionId"
      :standalone="isStandalone"
      :image-name="imageName"
      :admin-target-user-id="adminTargetUserId"
      :lab-context="labContext"
    />
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from '../api/axios'
import RangeBox from '../components/RangeBox.vue'
import RangeBoxHome from './RangeBoxHome.vue'

const route = useRoute()

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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #0a0a1a;
  z-index: 9999;
}

.rangebox-page :deep(.rangebox) {
  height: 100vh;
  border: none;
  border-radius: 0;
  margin: 0;
}

.rangebox-page :deep(.rangebox__viewport) {
  min-height: 0;
  flex: 1;
}
</style>
