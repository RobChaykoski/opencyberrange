<template>
  <main class="deeplink-page">
    <section class="deeplink-card" aria-labelledby="deeplink-title">
      <p class="deeplink-eyebrow">LTI 1.3 · Deep Linking</p>
      <h1 id="deeplink-title">{{ title }}</h1>
      <p class="deeplink-lead">
        Select the exercises this LMS assignment should open. The LMS will
        receive a signed content-item response and create the assignment links.
      </p>

      <p v-if="loading" class="deeplink-state">Loading exercises...</p>
      <p v-else-if="error" class="deeplink-state deeplink-state--error" role="alert">{{ error }}</p>
      <template v-else>
        <label class="deeplink-search">
          <span>Find an exercise</span>
          <input v-model="query" type="search" placeholder="Search by title or slug" />
        </label>
        <div class="deeplink-list" role="group" aria-label="Exercises">
          <label v-for="lab in filteredLabs" :key="lab.slug" class="deeplink-item">
            <input v-model="selected" type="checkbox" :value="lab.slug" @change="onSelect(lab.slug)" />
            <span>
              <strong>{{ lab.name }}</strong>
              <small>{{ lab.slug }}</small>
            </span>
          </label>
        </div>
        <p v-if="!filteredLabs.length" class="deeplink-state">No exercises match that search.</p>

        <div class="deeplink-actions">
          <span>{{ selected.length }} selected{{ acceptMultiple ? '' : ' (one per link)' }}</span>
          <button type="button" class="btn btn--primary" :disabled="submitting || !selected.length" @click="submit">
            {{ submitting ? 'Returning to LMS...' : 'Send to LMS' }}
          </button>
        </div>
        <p v-if="submitError" class="deeplink-state deeplink-state--error" role="alert">{{ submitError }}</p>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { safeHttpUrl } from '../utils/url'

const route = useRoute()
const title = ref('Choose exercises for the LMS')
const labs = ref([])
const selected = ref([])
const acceptMultiple = ref(false)
const query = ref('')
const loading = ref(true)
const error = ref('')
const submitting = ref(false)
const submitError = ref('')

const filteredLabs = computed(() => {
  const needle = query.value.trim().toLowerCase()
  if (!needle) return labs.value
  return labs.value.filter(
    (lab) => lab.name.toLowerCase().includes(needle) || lab.slug.toLowerCase().includes(needle)
  )
})

onMounted(async () => {
  const session = String(route.query.session || '')
  if (!session) {
    error.value = 'This Deep Linking request is missing its session.'
    loading.value = false
    return
  }
  try {
    const { data } = await api.get(`/lti/deep-link/${encodeURIComponent(session)}`)
    title.value = data.title || title.value
    labs.value = data.labs || []
    acceptMultiple.value = Boolean(data.accept_multiple)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not load the Deep Linking session.'
  } finally {
    loading.value = false
  }
})

const onSelect = (slug) => {
  if (acceptMultiple.value) return
  // The LMS accepts one content item per link; keep only the latest choice.
  if (selected.value.includes(slug)) selected.value = [slug]
}

const submit = async () => {
  submitting.value = true
  submitError.value = ''
  try {
    const session = String(route.query.session || '')
    const { data } = await api.post(
      `/lti/deep-link/${encodeURIComponent(session)}/response`,
      { lab_slugs: selected.value }
    )
    const action = safeHttpUrl(data.return_url)
    if (!action) {
      submitError.value = 'The LMS return URL is invalid.'
      return
    }
    const form = document.createElement('form')
    form.method = 'POST'
    form.action = action
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = 'JWT'
    input.value = data.jwt
    form.appendChild(input)
    document.body.appendChild(form)
    form.submit()
  } catch (e) {
    submitError.value = e.response?.data?.detail || 'Could not send the selection to the LMS.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.deeplink-page { min-height: 100vh; display: grid; place-items: start center; padding: 2.5rem 1rem; background: var(--bg-primary); color: var(--text-primary); }
.deeplink-card { width: min(860px, 100%); border: 1px solid var(--border-color); border-radius: 0.75rem; background: var(--bg-secondary); padding: 1.5rem; box-shadow: 0 18px 50px rgba(0,0,0,0.18); }
.deeplink-eyebrow { margin: 0 0 0.3rem; color: var(--accent); font-size: 0.66rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
.deeplink-card h1 { margin: 0; font-size: 1.45rem; }
.deeplink-lead { margin: 0.45rem 0 1rem; max-width: 68ch; color: var(--text-secondary); font-size: 0.82rem; line-height: 1.55; }
.deeplink-state { color: var(--text-secondary); font-size: 0.8rem; }
.deeplink-state--error { color: var(--danger); }
.deeplink-search { display: flex; flex-direction: column; gap: 0.25rem; margin-bottom: 0.75rem; }
.deeplink-search span { color: var(--text-secondary); font-size: 0.7rem; font-weight: 600; }
.deeplink-search input { border: 1px solid var(--border-color); border-radius: 0.35rem; background: var(--bg-primary); color: var(--text-primary); padding: 0.5rem 0.6rem; font-size: 0.8rem; }
.deeplink-list { max-height: 24rem; overflow: auto; border: 1px solid var(--border-color); border-radius: 0.45rem; }
.deeplink-item { display: flex; align-items: flex-start; gap: 0.55rem; padding: 0.5rem 0.65rem; border-bottom: 1px solid var(--border-color); cursor: pointer; }
.deeplink-item:last-child { border-bottom: 0; }
.deeplink-item:hover { background: var(--bg-primary); }
.deeplink-item input { margin-top: 0.2rem; }
.deeplink-item span { display: flex; flex-direction: column; gap: 0.1rem; }
.deeplink-item strong { font-size: 0.78rem; }
.deeplink-item small { color: var(--text-muted); font-size: 0.66rem; font-family: var(--font-mono, monospace); }
.deeplink-actions { display: flex; justify-content: space-between; align-items: center; gap: 1rem; margin-top: 1rem; color: var(--text-secondary); font-size: 0.75rem; }
@media (max-width: 640px) { .deeplink-card { padding: 1rem; } .deeplink-actions { flex-direction: column; align-items: stretch; } }
</style>
