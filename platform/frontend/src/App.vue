<template>
  <div
    id="app"
    class="app-root"
    :class="{
      'app-root--impersonating': isImpersonating,
      'app-root--sidebar-collapsed': sidebarCollapsed,
      'app-root--nav-open': mobileNavOpen,
      'app-root--authenticated': isAuthenticated,
    }"
  >
    <a href="#main-content" class="skip-link">Skip to main content</a>
    <!-- Impersonation Banner -->
    <ImpersonationBanner />

    <!-- Theme Toggle (global): dark -> light -> high contrast -->
    <button
      @click="toggleTheme"
      class="theme-toggle"
      :title="`Switch to ${nextThemeLabel} mode`"
      :aria-label="`Switch to ${nextThemeLabel} mode`"
    >
      <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <circle cx="12" cy="12" r="9"/>
        <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/>
      </svg>
    </button>

    <!-- Sidebar Layout (authenticated) -->
    <template v-if="isAuthenticated">
      <AppSidebar
        :collapsed="isMobile ? false : sidebarCollapsed"
        :mobile-open="mobileNavOpen"
        :is-mobile="isMobile"
        :user-role="userRole"
        :username="username"
        @toggle="sidebarCollapsed = !sidebarCollapsed"
        @logout="logout"
        @close="closeMobileNav"
      />
      <div
        v-if="isMobile && mobileNavOpen"
        class="mobile-backdrop"
        aria-hidden="true"
        @click="closeMobileNav"
      ></div>
      <main
        id="main-content"
        tabindex="-1"
        class="main-content"
        :class="{
          'main-content--mobile': isMobile,
          'main-content--with-tabbar': isMobile && isStudent,
        }"
        :inert="isMobile && mobileNavOpen"
      >
        <header v-if="isMobile" class="mobile-topbar">
          <button
            ref="mobileMenuButton"
            type="button"
            class="mobile-topbar__button"
            aria-label="Open navigation"
            :aria-expanded="mobileNavOpen"
            aria-controls="primary-sidebar"
            @click="openMobileNav"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <router-link to="/dashboard" class="mobile-topbar__brand" aria-label="SWOCTS Cyber Range home">
            <img src="/swocts-cyber-range-mark.png" alt="" />
            <span>SWOCTS</span>
          </router-link>
          <button
            type="button"
            class="mobile-topbar__button"
            :aria-label="`Switch to ${nextThemeLabel} mode`"
            :title="`Switch to ${nextThemeLabel} mode`"
            @click="toggleTheme"
          >
            <svg v-if="theme === 'dark'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
            <svg v-else-if="theme === 'light'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none" />
            </svg>
          </button>
        </header>
        <router-view :key="authState.token || 'guest'" />
        <MobileTabBar v-if="isMobile && isStudent" />
      </main>
      <GuidedTour v-model="showTour" :steps="tourSteps" @finish="onTourFinish" />
    </template>

    <!-- Guest (no sidebar) -->
    <main v-else class="main-content main-content--guest">
      <router-view :key="'guest'" />
    </main>

    <ToolPanel />

    <footer class="app-footer">
      <router-link to="/dashboard" class="app-footer__brand" aria-label="SWOCTS Cyber Range">
        <img src="/swocts-cyber-range-mark.png" alt="" class="app-footer__mark" />
        <span>SWOCTS Cyber Range</span>
      </router-link>
      <span class="app-footer__powered-label">Powered by</span>
      <a
        href="https://github.com/RobChaykoski/opencyberrange"
        target="_blank"
        rel="noopener noreferrer"
        class="app-footer__powered"
      >
        <img src="/ocr-logo-dark.png" alt="" class="app-footer__logo" />
        <span>OpenCyberRange</span>
      </a>
      <router-link to="/verify" class="app-footer__verify">Verify a certificate</router-link>
      <router-link to="/privacy" class="app-footer__verify">Privacy</router-link>
      <router-link to="/about/installation" class="app-footer__verify">About this installation</router-link>
      <span v-if="appVersion" class="app-footer__version" :title="appRelease">v{{ appVersion }}</span>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted, provide, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from './components/AppSidebar.vue'
import GuidedTour from './components/GuidedTour.vue'
import ImpersonationBanner from './components/ImpersonationBanner.vue'
import MobileTabBar from './components/MobileTabBar.vue'
import ToolPanel from './components/ToolPanel.vue'
import { useTheme } from './composables/useTheme'
import { usePrivacy } from './composables/usePrivacy'
import { useModules } from './composables/useModules'
import { useMobileView } from './composables/useMobileView'
import { setWikiAuthCookie } from './utils/wikiAuth'
import { useImpersonation } from './composables/useImpersonation'
import api from './api/axios'

const router = useRouter()
const { applyPrivacyDefaultForRole } = usePrivacy()
const { theme, nextThemeLabel, toggleTheme } = useTheme()
const { fetchModules, isModuleEnabled, resetModules } = useModules()
const { isImpersonating } = useImpersonation()
const { isMobile } = useMobileView()

const sidebarCollapsed = ref(false)
const mobileNavOpen = ref(false)
const mobileMenuButton = ref(null)
const appVersion = ref('')
const appRelease = ref('')

const openMobileNav = () => {
  mobileNavOpen.value = true
  nextTick(() => {
    document.querySelector('.sidebar .nav-item')?.focus()
  })
}

const closeMobileNav = () => {
  mobileNavOpen.value = false
  nextTick(() => {
    mobileMenuButton.value?.focus()
  })
}

const onGlobalKeydown = (event) => {
  if (!mobileNavOpen.value) return
  if (event.key === 'Escape') {
    closeMobileNav()
    return
  }
  if (event.key !== 'Tab' || !isMobile.value) return

  const sidebar = document.querySelector('.sidebar')
  if (!sidebar) return
  const focusable = [...sidebar.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )].filter((el) => el.offsetParent !== null)
  if (!focusable.length) return

  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first.focus()
  }
}

watch(() => router.currentRoute.value.fullPath, () => {
  mobileNavOpen.value = false
  nextTick(() => {
    document.getElementById('main-content')?.focus({ preventScroll: true })
  })
})

watch(isMobile, (value) => {
  if (!value) mobileNavOpen.value = false
})

// Reactive state to track auth changes - this ensures Vue reactivity works
const authState = ref({
  token: localStorage.getItem('token'),
  user: localStorage.getItem('user')
})

// Update auth state from localStorage - this function is exposed for external updates
const updateAuthState = () => {
  authState.value = {
    token: localStorage.getItem('token'),
    user: localStorage.getItem('user')
  }
}

// Provide updateAuthState and module helpers to child components
provide('updateAuthState', updateAuthState)
provide('isModuleEnabled', isModuleEnabled)
provide('isImpersonating', isImpersonating)

// Listen for storage events (cross-tab sync)
let storageListener = null
// Keep the wiki_auth cookie in sync with the current JWT so nginx auth_request
// gates (wikis and the SO console) always have a valid token. Scope logic is in
// the shared helper.
const refreshWikiAuthCookie = () => setWikiAuthCookie()

const loadAppVersion = async () => {
  try {
    const { data } = await api.get('/version')
    appVersion.value = data.version || ''
    appRelease.value = data.release || ''
  } catch {
    // Version display is informational; never block the interface on it.
  }
}

onMounted(() => {
  storageListener = () => { updateAuthState(); refreshWikiAuthCookie() }
  window.addEventListener('storage', storageListener)
  window.addEventListener('keydown', onGlobalKeydown)
  // Initial update
  updateAuthState()
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    applyPrivacyDefaultForRole(user.role)
  } catch { /* private mode or malformed session */ }
  refreshWikiAuthCookie()
  loadAppVersion()
  // Fetch module status if authenticated
  if (authState.value.token) {
    fetchModules()
    maybeStartTour()
  }
})

onUnmounted(() => {
  if (storageListener) {
    window.removeEventListener('storage', storageListener)
  }
  window.removeEventListener('keydown', onGlobalKeydown)
})

const isAuthenticated = computed(() => {
  return !!authState.value.token
})

const userRole = computed(() => {
  try {
    const user = JSON.parse(authState.value.user || '{}')
    return user.role || (user.is_admin ? 'admin' : 'student')
  } catch {
    return 'student'
  }
})

const isStudent = computed(() => userRole.value === 'student')

const username = computed(() => {
  try {
    const user = JSON.parse(authState.value.user || '{}')
    return user.username || 'User'
  } catch {
    return 'User'
  }
})

// ---- First-time-use orientation tour ----
const showTour = ref(false)
const tourUser = computed(() => {
  try {
    const u = JSON.parse(authState.value.user || '{}')
    return u.username || String(u.id || 'anon')
  } catch {
    return 'anon'
  }
})
const tourKey = computed(() => 'ocr_orientation_seen_v1_' + tourUser.value)
let tourCheckedForToken = null
const tourSteps = [
  { title: 'Welcome to the range', body: 'Here is a quick tour to get you from zero to your first running lab. It takes under a minute.', placement: 'center' },
  { title: '1. Connect over the VPN', body: 'Most labs run on an isolated network you reach over a VPN. Open VPN Setup to download your config and connect. You only do this once.', selector: '[data-tour="nav-vpn"]' },
  { title: '2. Or skip the VPN with RangeBox', body: 'No local setup? When you start a lab you can launch it with RangeBox instead, a full Kali attack box right in your browser, with nothing to install.', placement: 'center' },
  { title: '3. Find your exercises', body: 'Your labs live under Exercises, grouped into tracks by skill. Courses holds any work an instructor has assigned you.', selector: '[data-tour="nav-exercises"]' },
  { title: '4. Start your first lab', body: 'Open a track, pick an exercise, and click Launch or Start Exercise. Choose the VPN or a RangeBox when it starts, and your step-by-step workbook opens right alongside.', route: '/exercises', selector: '.track-grid .track-card' },
  { title: 'You are set', body: 'That is the whole loop: connect, launch, follow the workbook. You can replay this tour anytime from the sidebar menu. Have fun.', placement: 'center', route: '/exercises' },
]

// Browser storage is the fast path, but it is origin-scoped and can be
// cleared. Persist the same preference on the account so a student does not
// see the tour again from another browser, hostname, or private window.
async function tourSeenOnServer() {
  try {
    const { data } = await api.get('/auth/settings')
    return Boolean(data?.notification_prefs?.orientation_seen_v1)
  } catch {
    return false
  }
}

async function persistTourSeenOnServer() {
  try {
    const { data } = await api.get('/auth/settings')
    const prefs = { ...(data?.notification_prefs || {}), orientation_seen_v1: true }
    await api.put('/auth/settings', { notification_prefs: prefs })
  } catch {
    // Best effort. The localStorage key still suppresses the common case.
  }
}

async function maybeStartTour() {
  if (!authState.value.token || userRole.value !== 'student') return
  if (tourUser.value === 'anon') return
  if (localStorage.getItem(tourKey.value)) return
  // Avoid duplicate settings calls when mount and the token watcher both fire.
  if (tourCheckedForToken === authState.value.token) return
  tourCheckedForToken = authState.value.token

  if (await tourSeenOnServer()) {
    try { localStorage.setItem(tourKey.value, '1') } catch { /* private mode */ }
    return
  }

  setTimeout(() => {
    if (!isAuthenticated.value || userRole.value !== 'student') return
    // Re-check inside the timeout: another tab may have opened the tour while
    // this tab was waiting.
    if (localStorage.getItem(tourKey.value)) return
    // Persist as soon as it opens. Otherwise closing the tab, navigating away,
    // or reloading before pressing Skip/Finish makes it reappear on the next
    // login. The sidebar still offers "Take the tour" for a deliberate replay.
    try { localStorage.setItem(tourKey.value, '1') } catch { /* private mode */ }
    showTour.value = true
    void persistTourSeenOnServer()
  }, 900)
}
function onTourFinish() {
  try { localStorage.setItem(tourKey.value, '1') } catch { /* private mode */ }
  void persistTourSeenOnServer()
  showTour.value = false
}
function startTour() { showTour.value = true }
provide('startTour', startTour)
watch(() => authState.value.token, (t, old) => { if (t && !old) maybeStartTour() })

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  updateAuthState() // Update reactive state immediately
  resetModules()
  router.push('/login')
}

// Expose updateAuthState globally for Login.vue to call
// This ensures immediate reactivity when login happens
if (typeof window !== 'undefined') {
  window.__updateAuthState = updateAuthState
}
</script>

<style>
/* Global CSS Variables - Dark (default) */
:root {
  color-scheme: dark;
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #94a3b8;
  --border-color: #334155;
  --accent: #2563eb;
  --accent-text: #60a5fa;
  --badge-blue: #60a5fa;
  --badge-slate: #94a3b8;
  --badge-green: #4ade80;
  --badge-red: #f87171;
  --badge-amber: #fbbf24;
  --badge-purple: #c084fc;
  --badge-cyan: #22d3ee;
  --badge-pink: #f472b6;
  --success: #22c55e;
  --warning: #f59e0b;
  --danger: #ef4444;
  --nav-label: #94a3b8;
  --hover-bg: rgba(51, 65, 85, 0.5);
  --hover-text: #f1f5f9;
  --accent-bg: rgba(59, 130, 246, 0.1);
  --danger-bg: rgba(239, 68, 68, 0.1);
  --purple: #8b5cf6;
  --success-bg: rgba(34, 197, 94, 0.15);
  --warning-bg: rgba(245, 158, 11, 0.15);
  --panel-bg: #1e293b;
}

/* Light theme overrides */
[data-theme="light"] {
  color-scheme: light;
  --bg-primary: #ffffff;
  --bg-secondary: #f1f5f9;
  --bg-tertiary: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #55657a;
  --border-color: #cbd5e1;
  --accent: #1d4ed8;
  --accent-text: #1d4ed8;
  --badge-blue: #1d4ed8;
  --badge-slate: #475569;
  --badge-green: #14532d;
  --badge-red: #b91c1c;
  --badge-amber: #92400e;
  --badge-purple: #6b21a8;
  --badge-cyan: #0e7490;
  --badge-pink: #9d174d;
  --success: #15803d;
  --warning: #d97706;
  --danger: #dc2626;
  --nav-label: #475569;
  --hover-bg: rgba(0, 0, 0, 0.05);
  --hover-text: #0f172a;
  --accent-bg: rgba(59, 130, 246, 0.1);
  --danger-bg: rgba(239, 68, 68, 0.1);
  --purple: #7c3aed;
  --success-bg: rgba(22, 163, 74, 0.12);
  --warning-bg: rgba(217, 119, 6, 0.12);
  --panel-bg: #ffffff;
}

/* High-contrast theme: black canvas, white text, strong borders. Accent is
   cyan with black button text; status colours stay distinct and are always
   paired with a text label in the components that use them. */
[data-theme="contrast"] {
  color-scheme: dark;
  --bg-primary: #000000;
  --bg-secondary: #0a0a0a;
  --bg-tertiary: #1a1a1a;
  --text-primary: #ffffff;
  --text-secondary: #f5f5f5;
  --text-muted: #e5e5e5;
  --border-color: #ffffff;
  --accent: #22d3ee;
  --accent-text: #67e8f9;
  --badge-blue: #67e8f9;
  --badge-slate: #e5e5e5;
  --badge-green: #4ade80;
  --badge-red: #f87171;
  --badge-amber: #fbbf24;
  --badge-purple: #d8b4fe;
  --badge-cyan: #67e8f9;
  --badge-pink: #f9a8d4;
  --success: #4ade80;
  --warning: #fbbf24;
  --danger: #f87171;
  --nav-label: #e5e5e5;
  --hover-bg: #1f1f1f;
  --hover-text: #ffffff;
  --accent-bg: rgba(34, 211, 238, 0.2);
  --danger-bg: rgba(248, 113, 113, 0.2);
  --purple: #d8b4fe;
  --success-bg: rgba(74, 222, 128, 0.2);
  --warning-bg: rgba(251, 191, 36, 0.2);
  --panel-bg: #0a0a0a;
}

[data-theme="contrast"] .btn--primary {
  color: #000000;
}

/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Screen-reader-only text: keep labels available to assistive technology
   without showing them in the visual layout. */
.sr-only,
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  line-height: 1.6;
}

/* Global button system. Views that define their own scoped .btn win by
   specificity; nested components that use .btn without a local definition fall
   back to this instead of rendering as raw browser buttons. */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.5rem 1rem; border: none; border-radius: 6px;
  font-family: inherit; font-size: 0.8125rem; font-weight: 500;
  cursor: pointer; text-decoration: none; transition: all 0.15s;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--primary { background: var(--accent); color: #fff; }
.btn--primary:hover:not(:disabled) { background: #2563eb; }
.btn--secondary { background: var(--bg-tertiary); color: var(--text-secondary); border: 1px solid var(--border-color); }
.btn--secondary:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.btn--success { background: var(--success); color: #fff; }
.btn--success:hover:not(:disabled) { background: #16a34a; }
.btn--danger { background: transparent; border: 1px solid var(--danger); color: var(--danger); }
.btn--danger:hover:not(:disabled) { background: rgba(239, 68, 68, 0.1); }
.btn--outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-secondary); }
.btn--outline:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.btn--sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.btn--xs { padding: 0.25rem 0.5rem; font-size: 0.6875rem; }

/* App layout: sidebar + content + a footer that belongs to the content column.
   A flex row put the footer beside the main content, which pushed its logo to
   the far right; the grid keeps the footer below the content instead. */
.app-root {
  --app-sidebar-width: 250px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr) auto;
  min-height: 100vh;
}

.app-root--sidebar-collapsed {
  --app-sidebar-width: 64px;
}

.app-root > .sidebar {
  grid-column: 1;
  grid-row: 1 / -1;
}

/* Offset for impersonation banner */
.app-root--impersonating {
  padding-top: 44px;
}

.main-content {
  grid-column: 2;
  grid-row: 1;
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
}

.main-content--guest {
  width: 100%;
}

/* Mobile application shell. The sidebar becomes an off-canvas drawer and a
   compact top bar owns the menu and theme controls. */
.mobile-topbar {
  display: none;
}

.mobile-backdrop {
  display: none;
}

@media (max-width: 768px) {
  .mobile-topbar {
    position: sticky;
    top: 0;
    z-index: 120;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    min-height: 56px;
    padding: 0.35rem 0.65rem;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  .mobile-topbar__button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    padding: 0;
    border: none;
    border-radius: 10px;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
  }

  .mobile-topbar__button:hover {
    color: var(--text-primary);
    background: var(--hover-bg);
  }

  .mobile-topbar__button:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .mobile-topbar__button svg {
    width: 22px;
    height: 22px;
  }

  .mobile-topbar__brand {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    color: var(--text-primary);
    text-decoration: none;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.14em;
  }

  .mobile-topbar__brand img {
    width: 28px;
    height: 28px;
    object-fit: contain;
    border-radius: 4px;
  }

  .mobile-backdrop {
    position: fixed;
    inset: 0;
    z-index: 250;
    display: block;
    background: rgba(2, 6, 23, 0.58);
  }

  .main-content--with-tabbar {
    padding-bottom: calc(72px + env(safe-area-inset-bottom));
  }

  .app-footer {
    padding-bottom: calc(72px + env(safe-area-inset-bottom));
  }

  .app-root--nav-open .main-content {
    overflow: hidden;
  }
}

/* Theme toggle */
.theme-toggle {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 200;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.theme-toggle svg {
  width: 18px;
  height: 18px;
}

.theme-toggle:hover {
  color: var(--text-primary);
  border-color: var(--accent);
  background: var(--hover-bg);
}

/* Responsive */
@media (max-width: 768px) {
  .app-root {
    --app-sidebar-width: 0px;
    flex-direction: column;
  }
}

/* Printing a certificate should produce only the certificate, not the app
   chrome around it. Certificate.vue hides its own buttons. */
@media print {
  .sidebar,
  .theme-toggle,
  .impersonation-banner,
  .tour-overlay,
  .app-footer {
    display: none !important;
  }

  .app-root,
  .main-content {
    display: block !important;
    overflow: visible !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    background: #fff !important;
  }
}
.app-footer {
  grid-column: 2;
  grid-row: 2;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  border-top: 1px solid var(--border-color);
}

.app-footer__verify {
  margin-left: 0.75rem;
  padding-left: 0.75rem;
  border-left: 1px solid var(--border-color);
  color: var(--text-secondary);
  text-decoration: none;
}

.app-footer__verify:hover {
  color: var(--accent);
}

.app-footer__version {
  margin-left: 0.75rem;
  padding-left: 0.75rem;
  border-left: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.app-footer a {
  color: var(--accent-text);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 2px 0;
}
.app-footer a:hover {
  opacity: 0.8;
}
.app-footer__logo {
  height: 18px;
  width: auto;
  display: block;
  border-radius: 3px;
}

.app-footer__brand {
  gap: 0.35rem;
  font-weight: 700;
  color: var(--text-secondary) !important;
}

.app-footer__mark {
  width: 20px;
  height: 20px;
  object-fit: contain;
  border-radius: 3px;
}

.app-footer__powered-label {
  color: var(--text-secondary);
}

.app-footer__powered {
  gap: 0.3rem;
  font-weight: 600;
}

/* Keep the fixed desktop theme switch out of the mobile top bar; the mobile
   header carries its own theme control. Guest pages have no mobile header, so
   they keep the fixed switch. */
@media (max-width: 768px) {
  .app-root--authenticated .theme-toggle {
    display: none;
  }
}

.skip-link {
  position: absolute;
  top: -100px;
  left: 0.75rem;
  z-index: 1000;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--accent);
  text-decoration: none;
  font-weight: 600;
}

.skip-link:focus {
  top: 0.75rem;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

</style>
