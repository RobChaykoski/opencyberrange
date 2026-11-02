<template>
  <div class="verify-page">
    <main class="verify-card">
      <header class="verify-card__header">
        <p class="verify-card__eyebrow">OpenCyberRange</p>
        <h1>Verify a certificate</h1>
        <p class="verify-card__lead">
          Enter the certificate ID printed on the certificate, or scan its QR
          code. Verification confirms the track, level, completion count, and
          award date. It does not expose account details.
        </p>
      </header>

      <form v-if="!result && !loading" class="verify-form" @submit.prevent="submit">
        <label for="certificate-id">Certificate ID</label>
        <div class="verify-form__row">
          <input
            id="certificate-id"
            v-model.trim="certificateId"
            type="text"
            class="form-input"
            placeholder="OCR-TRACK-L01-0123456789"
            autocomplete="off"
            spellcheck="false"
            required
          />
          <button type="submit" class="btn btn--primary" :disabled="!certificateId">
            Verify
          </button>
        </div>
      </form>

      <p v-if="loading" class="verify-state" role="status">Checking the certificate...</p>

      <p v-if="error" class="error-message" role="alert">{{ error }}</p>

      <section v-if="result" class="verify-result" :class="result.valid ? 'verify-result--valid' : 'verify-result--invalid'" aria-live="polite">
        <template v-if="result.valid">
          <p class="verify-result__kicker">Certificate verified</p>
          <h2>{{ result.recipient }}</h2>
          <p class="verify-result__subtitle">
            completed <strong>Level {{ result.level_number }}: {{ result.level_name }}</strong>
            in <strong>{{ result.track_name }}</strong>.
          </p>
          <dl class="verify-result__details">
            <div>
              <dt>Exercises</dt>
              <dd>{{ result.exercises_completed }} / {{ result.exercises_total }}</dd>
            </div>
            <div>
              <dt>Awarded</dt>
              <dd>{{ result.issued_display }}</dd>
            </div>
            <div>
              <dt>Issuer</dt>
              <dd>{{ result.issuer }}</dd>
            </div>
            <div>
              <dt>Certificate ID</dt>
              <dd><code>{{ result.certificate_id }}</code></dd>
            </div>
          </dl>
          <p class="verify-result__note">{{ result.message }}</p>
        </template>
        <template v-else>
          <p class="verify-result__kicker">Not verified</p>
          <h2>We could not confirm this certificate.</h2>
          <p class="verify-result__subtitle">{{ result.reason }}</p>
          <p class="verify-result__note">
            Check the ID for typos. If it still fails, contact the issuer.
          </p>
        </template>
        <button type="button" class="btn btn--secondary" @click="reset">
          Check another certificate
        </button>
      </section>

      <p class="verify-card__footer">
        <router-link to="/">OpenCyberRange</router-link>
      </p>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'

const route = useRoute()
const router = useRouter()
const certificateId = ref(route.params.certificateId || '')
const loading = ref(false)
const error = ref('')
const result = ref(null)

const load = async (id) => {
  if (!id) return
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await axios.get(`/exercises/verify/certificate/${encodeURIComponent(id)}`)
    result.value = data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not check this certificate.'
  } finally {
    loading.value = false
  }
}

const submit = () => {
  const id = certificateId.value.trim()
  if (!id) return
  if (route.params.certificateId) {
    load(id)
  } else {
    router.push(`/verify/certificate/${encodeURIComponent(id)}`)
  }
}

const reset = () => {
  result.value = null
  error.value = ''
  certificateId.value = ''
  if (route.params.certificateId) {
    router.push('/verify')
  }
}

watch(
  () => route.params.certificateId,
  (id) => {
    certificateId.value = id || certificateId.value
    if (id) load(id)
  },
  { immediate: true },
)
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  display: grid;
  place-items: start center;
  padding: 3rem 1rem;
  background:
    radial-gradient(circle at 20% 0%, rgba(59, 130, 246, 0.12), transparent 40%),
    radial-gradient(circle at 80% 100%, rgba(139, 92, 246, 0.1), transparent 45%),
    var(--bg-primary);
}

.verify-card {
  width: min(100%, 720px);
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 18px 45px rgba(2, 6, 23, 0.18);
}

.verify-card__eyebrow {
  margin: 0 0 0.35rem;
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.verify-card h1 {
  margin: 0 0 0.65rem;
  font-size: clamp(1.6rem, 4vw, 2rem);
  color: var(--text-primary);
}

.verify-card__lead,
.verify-result__subtitle,
.verify-result__note {
  color: var(--text-secondary);
  line-height: 1.6;
}

.verify-form {
  margin-top: 1.4rem;
  display: grid;
  gap: 0.45rem;
}

.verify-form label {
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
}

.verify-form__row {
  display: flex;
  gap: 0.6rem;
}

.verify-form__row .form-input {
  flex: 1;
  min-width: 0;
  font-family: "JetBrains Mono", ui-monospace, monospace;
}

.verify-state {
  margin-top: 1.25rem;
  color: var(--text-secondary);
}

.verify-result {
  margin-top: 1.4rem;
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.verify-result--valid {
  border-color: color-mix(in srgb, var(--success) 45%, var(--border-color));
  background: var(--success-bg);
}

.verify-result--invalid {
  border-color: color-mix(in srgb, var(--danger) 45%, var(--border-color));
  background: var(--danger-bg);
}

.verify-result__kicker {
  margin: 0 0 0.35rem;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--success);
}

.verify-result--invalid .verify-result__kicker {
  color: var(--danger);
}

.verify-result h2 {
  margin: 0 0 0.45rem;
  color: var(--text-primary);
  font-size: 1.35rem;
}

.verify-result__details {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem 1.2rem;
  margin: 1.1rem 0;
}

.verify-result__details dt {
  color: var(--text-muted);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.verify-result__details dd {
  margin: 0.2rem 0 0;
  color: var(--text-primary);
  overflow-wrap: anywhere;
}

.verify-result__details code {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.8rem;
}

.verify-card__footer {
  margin: 1.5rem 0 0;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.8rem;
}

.verify-card__footer a {
  color: var(--accent);
}

@media (max-width: 640px) {
  .verify-page {
    padding: 1rem 0.75rem;
  }

  .verify-card {
    padding: 1.25rem;
  }

  .verify-form__row {
    flex-direction: column;
  }

  .verify-result__details {
    grid-template-columns: 1fr;
  }
}
</style>
