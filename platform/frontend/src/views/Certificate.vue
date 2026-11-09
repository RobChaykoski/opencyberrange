<template>
  <div class="certificate-page">
    <div class="certificate-actions no-print">
      <button class="btn btn--ghost" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="19" y1="12" x2="5" y2="12"/>
          <polyline points="12 19 5 12 12 5"/>
        </svg>
        Back
      </button>
      <div class="certificate-actions__right">
        <label v-if="certificate?.achievements?.length" class="certificate-toggle">
          <input v-model="showAchievements" type="checkbox" />
          Include achievements
        </label>
        <label v-if="certificate" class="certificate-design">
          <span>Design</span>
          <select v-model="activeDesign" class="form-input form-input--sm">
            <option v-for="design in certificateDesigns" :key="design.value" :value="design.value">
              {{ design.label }}
            </option>
          </select>
        </label>
        <button v-if="certificate" class="btn btn--secondary" :disabled="downloading" @click="downloadPdf">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          {{ downloading ? 'Preparing...' : 'Download PDF' }}
        </button>
        <button v-if="certificate" class="btn btn--ghost" @click="copyLink">
          {{ copied ? 'Link copied' : 'Copy verification link' }}
        </button>
        <a
          v-if="certificate"
          class="btn btn--ghost"
          :href="linkedInUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          Share on LinkedIn
        </a>
        <button v-if="certificate" class="btn btn--primary" @click="printCertificate">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 6 2 18 2 18 9"/>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
            <rect x="6" y="14" width="12" height="8"/>
          </svg>
          Print certificate
        </button>
      </div>
    </div>

    <div v-if="loading" class="certificate-state">Preparing your certificate...</div>

    <div v-else-if="error" class="certificate-state certificate-state--error">
      <h2>Certificate unavailable</h2>
      <p>{{ error }}</p>
      <button class="btn btn--primary no-print" @click="goBack">Return to the track</button>
    </div>

    <article v-else-if="certificate" class="certificate" :class="`certificate--${activeDesign}`" aria-label="Certificate of completion">
      <div class="certificate__frame">
        <div class="certificate__watermark" aria-hidden="true">
          <img src="/swocts-cyber-range-mark.png" alt="" />
          <div class="certificate__watermark-text">
            <span>SWOCTS</span>
            <span>Cyber Range</span>
          </div>
        </div>

        <div class="certificate__corner certificate__corner--tl"></div>
        <div class="certificate__corner certificate__corner--tr"></div>
        <div class="certificate__corner certificate__corner--bl"></div>
        <div class="certificate__corner certificate__corner--br"></div>

        <header class="certificate__header">
          <img src="/swocts-cyber-range-mark.png" alt="SWOCTS Cyber Range" class="certificate__logo" />
          <div class="certificate__heading">
            <p class="certificate__eyebrow">SWOCTS Cyber Range</p>
            <h1 class="certificate__title">Certificate of Completion</h1>
            <div class="certificate__rule"></div>
          </div>
        </header>

        <section class="certificate__body">
          <p class="certificate__lead">This is to certify that</p>
          <p class="certificate__recipient">{{ certificate.recipient }}</p>
          <p class="certificate__lead">has successfully completed</p>
          <p class="certificate__level">Level {{ certificate.level_number }}: {{ certificate.level_name }}</p>
          <p class="certificate__track">{{ certificate.track_name }}</p>
          <p class="certificate__detail">
            {{ certificate.exercises_completed }} of {{ certificate.exercises_total }}
            exercises completed
          </p>

          <section
            v-if="showAchievements && certificate.achievements?.length"
            class="certificate__achievements"
            aria-labelledby="certificate-achievements-title"
          >
            <p id="certificate-achievements-title" class="certificate__achievements-title">
              Achievements earned
            </p>
            <ul class="certificate__achievements-list">
              <li
                v-for="achievement in certificate.achievements"
                :key="achievement.type"
                class="certificate__achievement"
              >
                <span class="certificate__achievement-icon" aria-hidden="true">{{ achievement.icon }}</span>
                <span class="certificate__achievement-label">{{ achievement.label }}</span>
                <span v-if="achievement.count > 1" class="certificate__achievement-count">
                  &times;{{ achievement.count }}
                </span>
              </li>
            </ul>
          </section>
        </section>

        <footer class="certificate__footer">
          <div class="certificate__signature">
            <p class="certificate__signature-label">Powered by</p>
            <a
              href="https://github.com/RobChaykoski/opencyberrange"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="OpenCyberRange"
            >
              <img src="/ocr-logo-dark.png" alt="OpenCyberRange" class="certificate__signature-logo" />
            </a>
            <p class="certificate__signature-role">OpenCyberRange</p>
          </div>

          <div class="certificate__seal" role="img" aria-label="SWOCTS Cyber Range verified emblem">
            <div class="certificate__seal-ring">
              <img src="/swocts-cyber-range-mark.png" alt="" class="certificate__seal-emblem" />
              <span>SWOCTS</span>
              <small>VERIFIED</small>
            </div>
          </div>

          <div class="certificate__meta">
            <p class="certificate__meta-label">Date awarded</p>
            <p class="certificate__meta-value">{{ certificate.issued_display }}</p>
            <p class="certificate__meta-id">Certificate ID {{ certificate.certificate_id }}</p>
            <p v-if="safeHttpUrl(certificate.verify_url)" class="certificate__verify">
              <a :href="safeHttpUrl(certificate.verify_url)" target="_blank" rel="noopener noreferrer">
                Verify this certificate
              </a>
            </p>
            <div v-if="certificate.qr_code" class="certificate__qr">
              <img :src="certificate.qr_code" alt="QR code to verify this certificate" />
              <span>Scan to verify</span>
            </div>
          </div>
        </footer>
      </div>
    </article>

    <div v-if="certificate && usingAccountName" class="certificate-name-note no-print">
      <strong>This certificate uses your account name.</strong>
      Set the name you want printed in
      <router-link to="/profile?tab=account">Profile → Personal information</router-link>
      before sharing or printing.
    </div>

    <section v-if="certificate" class="certificate-share no-print">
      <div class="certificate-share__copy">
        <h2>Share your achievement</h2>
        <p>
          Post the PDF or share the verification link. Employers and instructors
          can confirm the track, level, award date, and certificate ID instantly.
        </p>
      </div>
      <div class="certificate-share__actions">
        <button class="btn btn--secondary" :disabled="downloading" @click="downloadPdf">
          {{ downloading ? 'Preparing...' : 'Download PDF' }}
        </button>
        <button class="btn btn--ghost" @click="copyLink">
          {{ copied ? 'Link copied' : 'Copy verification link' }}
        </button>
        <a class="btn btn--ghost" :href="linkedInUrl" target="_blank" rel="noopener noreferrer">
          Share on LinkedIn
        </a>
      </div>
      <p v-if="actionMessage" class="certificate-share__status" role="status">{{ actionMessage }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'
import { safeHttpUrl } from '../utils/url'

const route = useRoute()
const router = useRouter()

const certificateDesigns = [
  { value: 'classic', label: 'Classic' },
  { value: 'executive', label: 'Executive' },
  { value: 'modern', label: 'Modern' },
  { value: 'minimal', label: 'Minimal' },
]
const designStorageKey = 'ocr_certificate_design'

const certificate = ref(null)
const loading = ref(true)
const error = ref('')
const showAchievements = ref(true)
const activeDesign = ref('classic')
const downloading = ref(false)
const copied = ref(false)
const actionMessage = ref('')
const accountUsername = ref('')

const usingAccountName = computed(() => (
  Boolean(certificate.value?.recipient && accountUsername.value)
  && certificate.value.recipient.toLowerCase() === accountUsername.value.toLowerCase()
))

const shareUrl = computed(() => {
  return safeHttpUrl(certificate.value?.verify_url)
})
const linkedInUrl = computed(() => {
  if (!shareUrl.value) return 'https://www.linkedin.com/'
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl.value)}`
})

const downloadPdf = async () => {
  if (!certificate.value) return
  downloading.value = true
  try {
    const response = await axios.get(
      `/exercises/tracks/${route.params.trackSlug}/levels/${route.params.levelId}/certificate.pdf`,
      {
        params: { include_achievements: showAchievements.value },
        responseType: 'blob',
      }
    )
    const objectUrl = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = objectUrl
    link.download = `${certificate.value.certificate_id}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(objectUrl)
  } catch (e) {
    actionMessage.value = 'Could not prepare the PDF. Use Print certificate instead.'
    setTimeout(() => { actionMessage.value = '' }, 5000)
  } finally {
    downloading.value = false
  }
}

const copyLink = async () => {
  if (!shareUrl.value) return
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
  actionMessage.value = 'Verification link copied.'
  setTimeout(() => { copied.value = false }, 2500)
  setTimeout(() => { actionMessage.value = '' }, 3500)
}

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get(
      `/exercises/tracks/${route.params.trackSlug}/levels/${route.params.levelId}/certificate`
    )
    certificate.value = data
    document.title = `${data.recipient} — ${data.track_name} Level ${data.level_number} | SWOCTS Cyber Range`
    const stored = localStorage.getItem(designStorageKey)
    const valid = (value) => certificateDesigns.some((design) => design.value === value)
    activeDesign.value = valid(stored)
      ? stored
      : (valid(data.design) ? data.design : 'classic')
  } catch (e) {
    error.value = e?.response?.data?.detail
      || 'We could not issue a certificate for this level yet.'
  } finally {
    loading.value = false
  }
}

watch(activeDesign, (value) => {
  try {
    localStorage.setItem(designStorageKey, value)
  } catch {
    // Storage can be unavailable in private browsing; the design still applies.
  }
})

const printCertificate = () => window.print()

const goBack = () => {
  if (route.params.trackSlug) {
    router.push(`/exercises/${route.params.trackSlug}`)
  } else {
    router.push('/exercises')
  }
}

onMounted(() => {
  try {
    const storedUser = JSON.parse(localStorage.getItem('user') || 'null')
    accountUsername.value = storedUser?.username || ''
  } catch {
    accountUsername.value = ''
  }
  load()
})
</script>

<style scoped>
.certificate-page {
  min-height: calc(100vh - 2rem);
  padding: 2rem 1rem 3rem;
  background:
    radial-gradient(circle at 15% 10%, rgba(245, 158, 11, 0.12), transparent 45%),
    radial-gradient(circle at 85% 90%, rgba(59, 130, 246, 0.12), transparent 45%),
    var(--bg-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.certificate-actions {
  width: min(100%, 1040px);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  padding-right: 2.75rem;
}

.certificate-actions__right {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.certificate-design {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.certificate-design select {
  min-width: 8.5rem;
  padding: 0.35rem 0.5rem;
  font-size: 0.8rem;
}

.certificate-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  user-select: none;
}

.certificate-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.1rem;
  border-radius: 8px;
  border: 1px solid transparent;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.18s ease;
}

.btn svg {
  width: 16px;
  height: 16px;
}

.btn--primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
}

.btn--primary:hover {
  background: linear-gradient(135deg, #2563eb, #1e40af);
}

.btn--secondary {
  background: var(--bg-tertiary);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.btn--secondary:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.btn--secondary:disabled {
  opacity: 0.6;
  cursor: wait;
}

.btn--ghost {
  background: transparent;
  border-color: var(--border-color);
  color: var(--text-secondary);
}

.btn--ghost:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.certificate-state {
  margin-top: 4rem;
  color: var(--text-secondary);
  text-align: center;
}

.certificate-name-note {
  width: min(100%, 1040px);
  padding: 0.7rem 0.9rem;
  border: 1px solid var(--warning);
  border-radius: 10px;
  background: var(--warning-bg);
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.certificate-name-note strong { color: var(--text-primary); }
.certificate-name-note a { color: var(--accent); }

.certificate-state--error h2 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.certificate {
  width: min(100%, 1040px);
  background: #fffdf8;
  color: #1f2937;
  border-radius: 6px;
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.22);
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.certificate-share {
  width: min(100%, 1040px);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-secondary);
}

.certificate-share__copy h2 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.certificate-share__copy p {
  margin: 0;
  max-width: 58ch;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.certificate-share__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.certificate-share__status {
  flex-basis: 100%;
  margin: 0;
  color: var(--success);
  font-size: 0.8rem;
}

.certificate__frame {
  position: relative;
  margin: 14px;
  border: 2px solid #b08d3c;
  outline: 1px solid #d8c08a;
  outline-offset: 7px;
  padding: clamp(2rem, 5vw, 4rem) clamp(1.5rem, 5vw, 4.5rem);
  min-height: 620px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
}

.certificate__watermark {
  position: absolute;
  inset: 0;
  z-index: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transform: rotate(-16deg);
  opacity: 0.075;
  pointer-events: none;
  user-select: none;
}

.certificate__watermark img {
  width: min(46%, 320px);
  height: auto;
  filter: grayscale(1) contrast(1.2);
  mix-blend-mode: multiply;
}

.certificate__watermark-text {
  display: flex;
  align-items: center;
  gap: 0.6em;
  color: #1f2937;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.6rem, 4.5vw, 3.4rem);
  font-weight: 800;
  letter-spacing: 0.22em;
  line-height: 1;
  text-transform: uppercase;
  white-space: nowrap;
}

.certificate__header,
.certificate__body,
.certificate__footer {
  position: relative;
  z-index: 1;
}

.certificate__corner {
  position: absolute;
  width: 42px;
  height: 42px;
  border: 2px solid #b08d3c;
}

.certificate__corner--tl { top: 10px; left: 10px; border-right: 0; border-bottom: 0; }
.certificate__corner--tr { top: 10px; right: 10px; border-left: 0; border-bottom: 0; }
.certificate__corner--bl { bottom: 10px; left: 10px; border-right: 0; border-top: 0; }
.certificate__corner--br { bottom: 10px; right: 10px; border-left: 0; border-top: 0; }

.certificate__header {
  text-align: center;
}

.certificate__heading {
  display: block;
}

.certificate__logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
  display: block;
  margin: 0 auto 0.5rem;
}

.certificate__eyebrow {
  margin: 0;
  font-size: 0.7rem;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  color: #8a6d2f;
  font-weight: 700;
}

.certificate__title {
  margin: 0.4rem 0 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.9rem, 4vw, 3rem);
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #1f2937;
}

.certificate__rule {
  width: 120px;
  height: 3px;
  margin: 1.1rem auto 0;
  background: linear-gradient(90deg, transparent, #b08d3c, transparent);
}

.certificate__body {
  text-align: center;
  padding: 2rem 0;
}

.certificate__lead {
  margin: 0;
  font-size: 0.95rem;
  color: #6b7280;
  letter-spacing: 0.04em;
}

.certificate__recipient {
  margin: 0.5rem 0 1.4rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(2rem, 5vw, 3.4rem);
  font-weight: 700;
  color: #111827;
  border-bottom: 1px solid #d8c08a;
  display: inline-block;
  padding: 0 1.5rem 0.35rem;
}

.certificate__level {
  margin: 0.55rem 0 0.15rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.25rem, 2.6vw, 1.8rem);
  font-weight: 700;
  color: #1f2937;
}

.certificate__track {
  margin: 0;
  font-size: 1rem;
  color: #4b5563;
  font-weight: 600;
}

.certificate__detail {
  margin: 0.9rem 0 0;
  font-size: 0.82rem;
  color: #8a6d2f;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.certificate__achievements {
  margin-top: 1.1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5dcc4;
  break-inside: avoid;
}

.certificate__achievements-title {
  margin: 0 0 0.55rem;
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #8a6d2f;
  font-weight: 700;
}

.certificate__achievements-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.35rem 0.5rem;
}

.certificate__achievement {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.55rem;
  border: 1px solid #e2d5b6;
  border-radius: 999px;
  background: #fbf7ec;
  color: #4b5563;
  font-size: 0.72rem;
  line-height: 1.2;
}

.certificate__achievement-icon {
  font-size: 0.85rem;
  line-height: 1;
}

.certificate__achievement-count {
  color: #8a6d2f;
  font-weight: 700;
}

.certificate__footer {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: end;
  gap: 1rem;
}

.certificate__signature {
  justify-self: start;
  text-align: left;
  min-width: 190px;
}

.certificate__signature-label {
  margin: 0 0 0.3rem;
  font-size: 0.68rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #6b7280;
  font-weight: 600;
}

.certificate__signature-logo {
  width: 48px;
  height: 48px;
  object-fit: contain;
  display: block;
  margin: 0;
}

.certificate__signature-role {
  margin: 0.1rem 0 0;
  font-size: 0.72rem;
  color: #6b7280;
}

.certificate__seal {
  justify-self: center;
}

.certificate__seal-ring {
  width: 104px;
  height: 104px;
  border-radius: 50%;
  border: 3px double #b08d3c;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8a6d2f;
  background:
    radial-gradient(circle, rgba(176, 141, 60, 0.12), transparent 68%);
}

.certificate__seal-emblem {
  width: 30px;
  height: 30px;
  object-fit: contain;
  margin-bottom: 0.1rem;
  filter: grayscale(1) contrast(1.15);
}

.certificate__seal-ring span {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.certificate__seal-ring small {
  font-size: 0.55rem;
  letter-spacing: 0.16em;
  margin-top: 0.15rem;
}

.certificate__meta {
  justify-self: end;
  text-align: right;
  min-width: 190px;
}

.certificate__meta-label {
  margin: 0;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #6b7280;
}

.certificate__meta-value {
  margin: 0.15rem 0 0.5rem;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #111827;
}

.certificate__meta-id {
  margin: 0;
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 0.62rem;
  color: #9ca3af;
  letter-spacing: 0.02em;
}

.certificate__verify {
  margin: 0.35rem 0 0;
  font-size: 0.62rem;
}

.certificate__verify a {
  color: #8a6d2f;
}

.certificate__qr {
  margin-top: 0.45rem;
  display: inline-flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.2rem;
}

.certificate__qr img {
  width: 72px;
  height: 72px;
  padding: 4px;
  background: #fff;
  border: 1px solid #d8c08a;
  border-radius: 4px;
}

.certificate__qr span {
  font-size: 0.55rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8a6d2f;
}

/* --- Executive: navy, gold, left-aligned corporate layout --- */
.certificate--executive { background: #ffffff; }

.certificate--executive .certificate__frame {
  border: 1px solid #0b2545;
  outline: 3px solid #c8a24a;
  outline-offset: 6px;
  padding: clamp(2rem, 5vw, 4rem) clamp(1.75rem, 5vw, 5rem);
}

.certificate--executive .certificate__corner { display: none; }

.certificate--executive .certificate__header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  text-align: left;
  border-bottom: 2px solid #0b2545;
  padding-bottom: 1.1rem;
}

.certificate--executive .certificate__logo { margin: 0; width: 58px; height: 58px; }
.certificate--executive .certificate__heading { flex: 1; }
.certificate--executive .certificate__eyebrow { color: #0b2545; letter-spacing: 0.22em; }
.certificate--executive .certificate__title { color: #0b2545; font-size: clamp(1.6rem, 3.2vw, 2.5rem); }
.certificate--executive .certificate__rule { display: none; }
.certificate--executive .certificate__body { text-align: left; }
.certificate--executive .certificate__recipient { border-bottom: 2px solid #c8a24a; color: #0b2545; }
.certificate--executive .certificate__level { color: #0b2545; }
.certificate--executive .certificate__footer { border-top: 1px solid #d7dee8; padding-top: 1rem; }
.certificate--executive .certificate__seal-ring {
  border-color: #c8a24a;
  color: #0b2545;
  background: radial-gradient(circle, rgba(200, 162, 74, 0.12), transparent 68%);
}
.certificate--executive .certificate__qr img { border-color: #c8a24a; }

/* --- Modern: white, teal accent, right-aligned brand, clean sans --- */
.certificate--modern { background: #ffffff; }

.certificate--modern .certificate__frame {
  border: 0;
  outline: 0;
  border-left: 10px solid #0f766e;
  box-shadow: inset 0 0 0 1px #e2e8f0;
  padding: clamp(2rem, 5vw, 4rem) clamp(1.75rem, 5vw, 5rem);
}

.certificate--modern .certificate__corner { display: none; }

.certificate--modern .certificate__header {
  display: flex;
  flex-direction: row-reverse;
  align-items: center;
  gap: 1.5rem;
  text-align: left;
}

.certificate--modern .certificate__logo { margin: 0; width: 58px; height: 58px; }
.certificate--modern .certificate__heading { flex: 1; }
.certificate--modern .certificate__eyebrow { color: #0f766e; letter-spacing: 0.18em; }
.certificate--modern .certificate__title {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: clamp(1.5rem, 3vw, 2.4rem);
  color: #0f172a;
}
.certificate--modern .certificate__rule { margin: 0.8rem 0 0; width: 80px; background: #0f766e; }
.certificate--modern .certificate__body { text-align: left; }
.certificate--modern .certificate__recipient {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  border-bottom: 3px solid #0f766e;
  color: #0f172a;
}
.certificate--modern .certificate__detail { color: #0f766e; }
.certificate--modern .certificate__footer { border-top: 1px solid #e2e8f0; padding-top: 1rem; }
.certificate--modern .certificate__seal-ring {
  border-color: #0f766e;
  color: #0f766e;
  background: radial-gradient(circle, rgba(15, 118, 110, 0.1), transparent 68%);
}
.certificate--modern .certificate__qr img { border-color: #0f766e; }

/* --- Minimal: monochrome, thin rule, generous whitespace --- */
.certificate--minimal { background: #ffffff; }

.certificate--minimal .certificate__frame {
  border: 1px solid #d1d5db;
  outline: 0;
  padding: clamp(2.25rem, 5vw, 4.5rem) clamp(2rem, 6vw, 5.5rem);
}

.certificate--minimal .certificate__corner { display: none; }
.certificate--minimal .certificate__logo { width: 48px; height: 48px; }
.certificate--minimal .certificate__eyebrow { color: #6b7280; letter-spacing: 0.3em; }
.certificate--minimal .certificate__title {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-weight: 500;
  font-size: clamp(1.4rem, 2.8vw, 2.1rem);
  color: #111827;
}
.certificate--minimal .certificate__rule { width: 40px; height: 1px; background: #9ca3af; }
.certificate--minimal .certificate__recipient {
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  font-weight: 600;
  border-bottom: 1px solid #d1d5db;
  color: #111827;
}
.certificate--minimal .certificate__detail { color: #6b7280; }
.certificate--minimal .certificate__seal-ring {
  border-color: #d1d5db;
  color: #6b7280;
  background: none;
}
.certificate--minimal .certificate__qr img { border-color: #d1d5db; }

@media (max-width: 720px) {
  .certificate-actions {
    padding-right: 0;
    padding-top: 2.5rem;
  }

  .certificate-actions__right {
    width: 100%;
    justify-content: space-between;
  }

  .certificate__frame {
    min-height: 0;
  }

  .certificate__footer {
    grid-template-columns: 1fr;
    justify-items: center;
    text-align: center;
    gap: 1.5rem;
  }

  .certificate__signature,
  .certificate__meta {
    justify-self: center;
    text-align: center;
  }

  .certificate__signature-logo {
    margin-left: auto;
    margin-right: auto;
  }
}

@media print {
  .no-print {
    display: none !important;
  }

  .certificate-page {
    padding: 0;
    background: #fff;
    min-height: 0;
  }

  .certificate {
    width: 100%;
    box-shadow: none;
    border-radius: 0;
  }

  .certificate__frame {
    min-height: 0;
    page-break-inside: avoid;
  }
}
</style>
