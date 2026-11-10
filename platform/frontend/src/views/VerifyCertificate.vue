<template>
  <div class="verify-page">
    <header class="verify-nav">
      <router-link to="/" class="verify-brand" aria-label="SWOCTS Cyber Range home">
        <img src="/swocts-cyber-range-mark.png" alt="" />
        <span>SWOCTS Cyber Range</span>
      </router-link>
      <nav class="verify-nav__links" aria-label="Public links">
        <router-link to="/about">About</router-link>
        <router-link v-if="signedIn" to="/dashboard">Dashboard</router-link>
        <router-link v-if="signedIn && role === 'admin'" to="/admin">Admin</router-link>
        <router-link v-if="!signedIn" to="/login">Sign in</router-link>
      </nav>
    </header>

    <main class="verify-layout">
      <section class="verify-card">
        <header class="verify-card__header">
          <p class="verify-card__eyebrow">Certificate verification</p>
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
              v-model="certificateId"
              type="text"
              class="form-input"
              placeholder="OCR-TRACK-L01-0123456789"
              autocomplete="off"
              autocapitalize="characters"
              spellcheck="false"
              :aria-invalid="validationError ? 'true' : 'false'"
              aria-describedby="certificate-id-error"
              required
              @input="clearValidationError"
            />
            <button type="submit" class="btn btn--primary" :disabled="!certificateId">
              Verify
            </button>
          </div>
          <p v-if="validationError" id="certificate-id-error" class="verify-form__error" role="alert">
            {{ validationError }}
          </p>
          <p class="verify-form__hint">
            The ID is printed near the bottom of the certificate and starts with
            <code>OCR-</code>.
          </p>
        </form>

        <p v-if="loading" class="verify-state" role="status">Checking the certificate...</p>

        <p v-if="error" class="verify-form__error" role="alert">{{ error }}</p>

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
            <div class="verify-result__actions">
              <button type="button" class="btn btn--secondary" @click="copyShareLink">
                {{ copied ? 'Link copied' : 'Copy link' }}
              </button>
              <a
                class="btn btn--secondary"
                :href="linkedInUrl"
                target="_blank"
                rel="noopener noreferrer"
              >
                Share on LinkedIn
              </a>
              <button type="button" class="btn btn--secondary" @click="shareNative">
                Share
              </button>
            </div>
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
          <router-link to="/">SWOCTS Cyber Range</router-link>
          <span aria-hidden="true"> · </span>
          <router-link to="/about">About this site</router-link>
        </p>
      </section>

      <aside class="verify-side" aria-label="Verification help">
        <article class="verify-side__card">
          <h2>What this confirms</h2>
          <ul>
            <li>Track and level completed</li>
            <li>Exercises completed</li>
            <li>Award date</li>
            <li>Issuer and certificate ID</li>
          </ul>
        </article>

        <article class="verify-side__card">
          <h2>Where to find the ID</h2>
          <p>
            The certificate ID is printed near the bottom of the PDF or printed
            certificate. You can also scan the QR code on the certificate.
          </p>
          <code class="verify-example">OCR-WEB-L01-0123456789</code>
        </article>

        <article class="verify-side__card verify-side__card--privacy">
          <h2>Privacy</h2>
          <p>
            Verification returns only public certificate fields. It does not show
            a username, email address, or other account details. Read the
            <router-link to="/privacy">Privacy notice</router-link>.
          </p>
        </article>

        <div class="verify-side__cta">
          <p>Viewing the platform for the first time?</p>
          <router-link to="/about" class="btn btn--secondary btn--sm">About this site</router-link>
        </div>
      </aside>
    </main>

    <footer class="verify-footer">
      <span>Powered by OpenCyberRange.</span>
      <nav aria-label="Footer links">
        <router-link to="/privacy">Privacy</router-link>
        <router-link to="/about">About</router-link>
      </nav>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'

// Certificate IDs are ASCII-only: OCR-<track prefix>-L<level>-<hex digest>.
// Keep this in step with _CERTIFICATE_ID_RE in the backend curriculum router.
const CERTIFICATE_ID_RE = /^OCR-[A-Z0-9-]{1,8}-L[0-9]{2}-[A-F0-9]{10}$/
const CERTIFICATE_ID_MAX_LENGTH = 27

const route = useRoute()
const router = useRouter()
const certificateId = ref(route.params.certificateId || '')
const loading = ref(false)
const error = ref('')
const validationError = ref('')
const result = ref(null)
const copied = ref(false)
const user = JSON.parse(localStorage.getItem('user') || '{}')
const signedIn = Boolean(localStorage.getItem('token'))
const role = user.role || 'student'

const shareUrl = computed(() => window.location.href)
const linkedInUrl = computed(
  () => `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl.value)}`
)

const setMeta = (key, content, attribute = 'property') => {
  if (!content) return
  let element = document.head.querySelector(`meta[${attribute}="${key}"]`)
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, key)
    document.head.appendChild(element)
  }
  element.setAttribute('content', content)
}

const applyResultMeta = (data) => {
  if (!data?.valid) return
  const title = `${data.recipient} — ${data.track_name} Level ${data.level_number}`
  document.title = `${title} | SWOCTS Cyber Range`
  const description =
    `${data.recipient} completed Level ${data.level_number}: ${data.level_name} ` +
    `in ${data.track_name} on the SWOCTS Cyber Range. ` +
    `${data.exercises_completed} of ${data.exercises_total} exercises completed.`
  setMeta('og:title', title)
  setMeta('og:description', description)
  setMeta('og:type', 'article')
  setMeta('og:url', window.location.href)
  setMeta('og:image', `${window.location.origin}/swocts-cyber-range-mark.png`)
  setMeta('twitter:card', 'summary', 'name')
  setMeta('twitter:title', title, 'name')
  setMeta('twitter:description', description, 'name')
}

const copyShareLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
  } catch {
    const input = document.createElement('textarea')
    input.value = shareUrl.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    input.remove()
  }
  copied.value = true
  setTimeout(() => { copied.value = false }, 2500)
}

const shareNative = async () => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: result.value?.recipient
          ? `${result.value.recipient} — ${result.value.track_name}`
          : 'SWOCTS Cyber Range certificate',
        text: result.value?.message || 'Verified certificate',
        url: shareUrl.value,
      })
      return
    } catch {
      // The user cancelled or sharing is unavailable; fall through to copy.
    }
  }
  await copyShareLink()
}

const normalizeCertificateId = (value) => String(value || '').trim().toUpperCase()

const validateCertificateId = (value) => {
  const id = normalizeCertificateId(value)
  if (!id) {
    validationError.value = 'Enter a certificate ID.'
    return null
  }
  if (id.length > CERTIFICATE_ID_MAX_LENGTH || !CERTIFICATE_ID_RE.test(id)) {
    validationError.value =
      'Certificate IDs use letters, numbers, and hyphens only, for example OCR-WEB-L01-0123456789.'
    return null
  }
  validationError.value = ''
  return id
}

const clearValidationError = () => {
  validationError.value = ''
}

const load = async (rawId) => {
  const id = validateCertificateId(rawId)
  if (!id) {
    result.value = null
    loading.value = false
    return
  }
  certificateId.value = id
  loading.value = true
  error.value = ''
  result.value = null
  try {
    const { data } = await axios.get(`/exercises/verify/certificate/${encodeURIComponent(id)}`)
    result.value = data
    applyResultMeta(data)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Could not check this certificate.'
  } finally {
    loading.value = false
  }
}

const submit = () => {
  const id = validateCertificateId(certificateId.value)
  if (!id) return
  certificateId.value = id
  if (route.params.certificateId) {
    load(id)
  } else {
    router.push(`/verify/certificate/${encodeURIComponent(id)}`)
  }
}

const reset = () => {
  result.value = null
  error.value = ''
  validationError.value = ''
  certificateId.value = ''
  document.title = 'Verify a certificate | SWOCTS Cyber Range'
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

.verify-form__error {
  margin: 0.35rem 0 0;
  color: var(--danger);
  font-size: 0.82rem;
  line-height: 1.45;
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

.verify-result__note {
  margin-bottom: 0;
}

.verify-result__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1rem 0;
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

/* Public verification layout */
.verify-page {
  display: flex;
  flex-direction: column;
  place-items: initial;
  padding: 0;
  background:
    radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.14), transparent 40%),
    radial-gradient(circle at 90% 25%, rgba(139, 92, 246, 0.12), transparent 44%),
    var(--bg-primary);
}

.verify-nav {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  padding: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.verify-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: var(--text-primary);
  font-weight: 700;
  text-decoration: none;
}

.verify-brand img {
  width: 38px;
  height: 38px;
  object-fit: contain;
}

.verify-nav__links {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  font-size: 0.85rem;
}

.verify-nav__links a {
  color: var(--text-secondary);
  text-decoration: none;
}

.verify-nav__links a:hover {
  color: var(--text-primary);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.verify-layout {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.85fr);
  gap: 1.25rem;
  align-items: start;
  padding: 1.5rem 0 2rem;
}

.verify-card {
  width: 100%;
  padding: 2rem;
}

.verify-card__header {
  max-width: 62ch;
}

.verify-form__hint {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.78rem;
  line-height: 1.5;
}

.verify-form__hint code {
  font-family: "JetBrains Mono", ui-monospace, monospace;
  color: var(--text-secondary);
}

.verify-side {
  display: grid;
  gap: 0.8rem;
}

.verify-side__card {
  padding: 1rem 1.1rem;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  background: var(--bg-secondary);
}

.verify-side__card h2 {
  margin: 0 0 0.4rem;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.verify-side__card p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.verify-side__card ul {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.verify-side__card--privacy {
  border-left: 3px solid var(--accent);
}

.verify-example {
  display: block;
  margin-top: 0.55rem;
  padding: 0.45rem 0.6rem;
  border-radius: 6px;
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}

.verify-side__cta {
  padding: 1rem;
  border: 1px dashed var(--border-color);
  border-radius: 10px;
  text-align: center;
}

.verify-side__cta p {
  margin: 0 0 0.5rem;
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.verify-footer {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  padding: 1rem 0 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  color: var(--text-muted);
  font-size: 0.78rem;
}

.verify-footer nav {
  display: flex;
  gap: 0.85rem;
}

.verify-footer a {
  color: var(--text-secondary);
  text-decoration: none;
}

.verify-footer a:hover {
  color: var(--text-primary);
  text-decoration: underline;
}

.verify-page a:focus-visible,
.verify-page button:focus-visible,
.verify-page input:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 2px;
}

@media (max-width: 900px) {
  .verify-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .verify-nav {
    align-items: flex-start;
    flex-direction: column;
  }

  .verify-layout {
    padding-top: 0.75rem;
  }
}

</style>
