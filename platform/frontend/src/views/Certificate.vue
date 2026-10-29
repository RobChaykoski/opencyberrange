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
      <button v-if="certificate" class="btn btn--primary" @click="printCertificate">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 6 2 18 2 18 9"/>
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
          <rect x="6" y="14" width="12" height="8"/>
        </svg>
        Print certificate
      </button>
    </div>

    <div v-if="loading" class="certificate-state">Preparing your certificate...</div>

    <div v-else-if="error" class="certificate-state certificate-state--error">
      <h2>Certificate unavailable</h2>
      <p>{{ error }}</p>
      <button class="btn btn--primary no-print" @click="goBack">Return to the track</button>
    </div>

    <article v-else-if="certificate" class="certificate" aria-label="Certificate of completion">
      <div class="certificate__frame">
        <div class="certificate__corner certificate__corner--tl"></div>
        <div class="certificate__corner certificate__corner--tr"></div>
        <div class="certificate__corner certificate__corner--bl"></div>
        <div class="certificate__corner certificate__corner--br"></div>

        <header class="certificate__header">
          <img src="/swocts_logo.jpg" alt="SWOCTS" class="certificate__logo" />
          <p class="certificate__eyebrow">OpenCyberRange</p>
          <h1 class="certificate__title">Certificate of Completion</h1>
          <div class="certificate__rule"></div>
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
        </section>

        <footer class="certificate__footer">
          <div class="certificate__signature">
            <div class="certificate__signature-line"></div>
            <p class="certificate__signature-name">Presented by SWOCTS</p>
            <p class="certificate__signature-role">OpenCyberRange Training Range</p>
          </div>

          <div class="certificate__seal" aria-hidden="true">
            <div class="certificate__seal-ring">
              <span>SWOCTS</span>
              <small>VERIFIED</small>
            </div>
          </div>

          <div class="certificate__meta">
            <p class="certificate__meta-label">Date awarded</p>
            <p class="certificate__meta-value">{{ certificate.issued_display }}</p>
            <p class="certificate__meta-id">Certificate ID {{ certificate.certificate_id }}</p>
          </div>
        </footer>
      </div>
    </article>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '../api/axios'

const route = useRoute()
const router = useRouter()

const certificate = ref(null)
const loading = ref(true)
const error = ref('')

const load = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await axios.get(
      `/exercises/tracks/${route.params.trackSlug}/levels/${route.params.levelId}/certificate`
    )
    certificate.value = data
  } catch (e) {
    error.value = e?.response?.data?.detail
      || 'We could not issue a certificate for this level yet.'
  } finally {
    loading.value = false
  }
}

const printCertificate = () => window.print()

const goBack = () => {
  if (route.params.trackSlug) {
    router.push(`/exercises/${route.params.trackSlug}`)
  } else {
    router.push('/exercises')
  }
}

onMounted(load)
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
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
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

.certificate__logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
  margin-bottom: 0.5rem;
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

.certificate__footer {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: end;
  gap: 1rem;
}

.certificate__signature {
  justify-self: start;
  min-width: 190px;
}

.certificate__signature-line {
  width: 190px;
  height: 1px;
  background: #9ca3af;
  margin-bottom: 0.45rem;
}

.certificate__signature-name {
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 1.05rem;
  font-weight: 700;
  color: #111827;
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

@media (max-width: 720px) {
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

  .certificate__signature-line {
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
