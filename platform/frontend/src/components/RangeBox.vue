<template>
  <div
    ref="rangeboxRoot"
    class="rangebox"
    :class="{ 'rangebox--fullscreen': isFullscreen, 'rangebox--collapsed': isCollapsed }"
    @dragover.prevent
    @drop.prevent="rejectFileDrop"
    @dragstart.prevent
  >
    <!-- Toolbar -->
    <div class="rangebox__toolbar">
      <div class="rangebox__toolbar-left">
        <div class="rangebox__status" :class="`rangebox__status--${connectionState}`">
          <span class="rangebox__status-dot"></span>
          {{ statusLabel }}
        </div>
        <span class="rangebox__label">{{ toolbarLabel }}</span>
        <span v-if="impersonation" class="rangebox__impersonate-badge">
          IMPERSONATING {{ impersonation.username }}
        </span>
        <span v-if="showTimer && timeRemaining !== null" class="rangebox__timer" :class="{ 'rangebox__timer--warning': timeRemaining < 300 }">
          {{ formattedTime }}
        </span>
      </div>
      <div class="rangebox__toolbar-right">
        <select
          v-model="qualityPreset"
          class="rangebox__select"
          title="Stream quality"
          aria-label="Stream quality"
        >
          <option v-for="(preset, key) in QUALITY_PRESETS" :key="key" :value="key">
            {{ preset.label }}
          </option>
        </select>
        <button
          v-if="connectionState === 'connected'"
          @click="sendCtrlAltDel"
          class="rangebox__btn"
          title="Send Ctrl+Alt+Del to the desktop"
        >
          Ctrl+Alt+Del
        </button>
        <button
          v-if="connectionState === 'disconnected'"
          @click="connect"
          class="rangebox__btn"
          title="Reconnect"
        >
          Reconnect
        </button>
        <button
          @click="toggleClipboard"
          class="rangebox__btn"
          :class="{ 'rangebox__btn--active': showClipboard }"
          title="Clipboard"
        >
          Clipboard
        </button>
        <button @click="toggleCollapse" class="rangebox__btn" :title="isCollapsed ? 'Expand' : 'Minimize'">
          {{ isCollapsed ? 'Expand' : 'Minimize' }}
        </button>
        <button @click="toggleFullscreen" class="rangebox__btn" :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'">
          {{ isFullscreen ? 'Exit FS' : 'Fullscreen' }}
        </button>
        <button
          v-if="showClose"
          @click="closeViewer"
          class="rangebox__btn rangebox__btn--close"
          title="Close RangeBox"
          aria-label="Close RangeBox"
        >
          Close
        </button>
      </div>
    </div>

    <!-- Clipboard panel -->
    <div v-if="showClipboard && !isCollapsed" class="rangebox__clipboard">
      <textarea
        v-model="clipboardText"
        placeholder="Paste text here, then press Send to transfer to RangeBox..."
        rows="3"
        @paste="onClipboardPanelPaste"
        @drop.prevent="rejectFileDrop"
      ></textarea>
      <p class="rangebox__clipboard-note">
        Text only. Files cannot leave or enter the RangeBox.
      </p>
      <p v-if="clipboardNotice" class="rangebox__clipboard-warning">{{ clipboardNotice }}</p>
      <div class="rangebox__clipboard-actions">
        <button @click="sendClipboard" class="rangebox__btn rangebox__btn--primary" :disabled="!clipboardText">
          Send to RangeBox
        </button>
        <button @click="readClipboardIntoPanel" class="rangebox__btn" title="Read text from your browser clipboard">
          Read clipboard
        </button>
        <button @click="receiveClipboard" class="rangebox__btn">
          Get from RangeBox
        </button>
        <button
          v-if="labContext"
          @click="useClipboardAsFlag"
          class="rangebox__btn"
          :disabled="!clipboardText"
          title="Copy the clipboard text into the flag field"
        >
          Use as flag
        </button>
      </div>
    </div>

    <!-- VNC viewport -->
    <div v-show="!isCollapsed" ref="vncContainer" class="rangebox__viewport">
      <div v-if="connectionState === 'connecting'" class="rangebox__connecting">
        <div class="rangebox__spinner"></div>
        <p>Connecting to RangeBox...</p>
        <p class="rangebox__connecting-hint">Starting {{ imageDisplayName || 'RangeBox' }} desktop environment</p>
      </div>
      <div v-if="connectionState === 'disconnected'" class="rangebox__disconnected">
        <p>Connection lost</p>
        <p v-if="connectionMessage" class="rangebox__disconnected-hint">{{ connectionMessage }}</p>
        <button @click="connect" class="rangebox__btn rangebox__btn--primary">Reconnect</button>
      </div>
    </div>

    <!-- Lab dock: target addresses and flag entry without leaving the desktop -->
    <div v-if="labContext && !isCollapsed && !isAdminViewer" class="rangebox__lab-dock">
      <div class="rangebox__lab-meta">
        <strong class="rangebox__lab-name">{{ labContext.lab_name }}</strong>
        <span v-if="labContext.network_subnet" class="rangebox__lab-network">
          Network <code>{{ labContext.network_subnet }}</code>
        </span>
        <span
          v-for="target in labContext.target_ips"
          :key="target.id || target.ip"
          class="rangebox__ip-chip"
          :title="target.label"
        >
          {{ target.label }} <code>{{ target.ip }}</code>
        </span>
        <span v-if="labCompleted" class="rangebox__flag-accepted">Flag accepted</span>
      </div>

      <form v-if="!labCompleted" class="rangebox__flag-form" @submit.prevent="submitFlag">
        <label for="rangebox-flag" class="rangebox__flag-label">Flag</label>
        <input
          id="rangebox-flag"
          ref="flagInput"
          v-model="flagValue"
          type="text"
          class="rangebox__flag-input"
          placeholder="OCR{your_flag_here}"
          autocomplete="off"
          autocapitalize="off"
          autocorrect="off"
          spellcheck="false"
          enterkeyhint="go"
          :disabled="flagSubmitting"
          @paste="onFlagPaste"
        />
        <button
          type="button"
          class="rangebox__btn"
          :disabled="flagSubmitting"
          title="Paste and clean the flag from your clipboard"
          @click="pasteFlagFromClipboard"
        >
          Paste
        </button>
        <button type="submit" class="rangebox__btn rangebox__btn--primary" :disabled="flagSubmitting || !flagValue.trim()">
          {{ flagSubmitting ? 'Checking...' : 'Submit flag' }}
        </button>
        <span v-if="flagMessage" class="rangebox__flag-message" :class="{ 'rangebox__flag-message--error': flagError }">
          {{ flagMessage }}
        </span>
      </form>
      <p v-if="!labCompleted" class="rangebox__flag-hint">
        Copy the flag inside the desktop; it fills here automatically. Or paste with Ctrl+V.
      </p>
      <p v-else class="rangebox__flag-done">You can close this window or return to the exercise.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from '../api/axios'
import { isAdmin } from '../utils/roles'
import { usePoll } from '../composables/usePoll'

const props = defineProps({
  sessionId: { type: Number, default: null },
  standalone: { type: Boolean, default: false },
  imageName: { type: String, default: '' },
  adminTargetUserId: { type: Number, default: null },
  statusData: { type: Object, default: null },
  // Lab metadata for the in-window flag/IP dock (exercise RangeBox only).
  labContext: { type: Object, default: null },
  showClose: { type: Boolean, default: false },
  showTimer: { type: Boolean, default: true },
})

const router = useRouter()

const QUALITY_PRESETS = {
  high: { label: 'High quality', quality: 9, compression: 0 },
  balanced: { label: 'Balanced', quality: 6, compression: 2 },
  low: { label: 'Low bandwidth', quality: 3, compression: 6 },
}

// State
const rangeboxRoot = ref(null)
const vncContainer = ref(null)
const connectionState = ref('connecting') // connecting | connected | disconnected
const connectionMessage = ref('')
const isFullscreen = ref(false)
const isCollapsed = ref(false)
const showClipboard = ref(false)
const clipboardText = ref('')
const clipboardNotice = ref('')
const qualityPreset = ref(localStorage.getItem('ocr.rangebox.quality') || 'balanced')

const FILE_TRANSFER_NOTICE = 'Files cannot leave or enter the RangeBox. Copy text only.'

function rejectFileDrop(event) {
  const files = event.dataTransfer?.files
  if (files?.length) {
    clipboardNotice.value = FILE_TRANSFER_NOTICE
  }
  // Always stop the browser from opening, uploading, or downloading the file.
  event.preventDefault()
  event.stopPropagation()
  if (event.dataTransfer) event.dataTransfer.dropEffect = 'none'
}

function onClipboardPanelPaste(event) {
  const items = Array.from(event.clipboardData?.items || [])
  if (items.some((item) => item.kind === 'file')) {
    event.preventDefault()
    clipboardNotice.value = FILE_TRANSFER_NOTICE
    return
  }
  clipboardNotice.value = ''
}

// In-window flag submission (exercise RangeBox only).
const flagValue = ref('')
const flagMessage = ref('')
const flagError = ref(false)
const flagSubmitting = ref(false)
const flagAccepted = ref(false)
const flagInput = ref(null)

const FLAG_PATTERN = /OCR\{[^}]*\}/i

// Paste and clipboard text can carry newlines, zero-width characters, shell
// prompts, or a whole log line. Keep only the flag when one is present so a
// correct flag is not rejected for the wrapper around it.
function extractFlag(text) {
  if (!text) return ''
  const cleaned = String(text)
    .replace(/[\u200B-\u200D\uFEFF]/g, '')
    .trim()
  const match = cleaned.match(FLAG_PATTERN)
  return match ? match[0] : cleaned
}

function setFlagCandidate(text, message = '') {
  const candidate = extractFlag(text)
  if (!candidate) return
  flagValue.value = candidate
  flagMessage.value = message
  flagError.value = false
  nextTick(() => flagInput.value?.focus())
}

function onFlagPaste(event) {
  const items = Array.from(event.clipboardData?.items || [])
  if (items.some((item) => item.kind === 'file')) {
    event.preventDefault()
    flagMessage.value = FILE_TRANSFER_NOTICE
    flagError.value = true
    return
  }
  const text = event.clipboardData?.getData('text') || ''
  if (!text) return
  event.preventDefault()
  setFlagCandidate(text)
}

async function pasteFlagFromClipboard() {
  try {
    const text = await navigator.clipboard.readText()
    if (!text) {
      flagMessage.value = 'Your clipboard is empty. Copy the flag, then try again.'
      flagError.value = true
      return
    }
    setFlagCandidate(text)
  } catch {
    flagMessage.value = 'Clipboard access is blocked. Click the field and press Ctrl+V.'
    flagError.value = true
    nextTick(() => flagInput.value?.focus())
  }
}

function useClipboardAsFlag() {
  if (!clipboardText.value) return
  setFlagCandidate(clipboardText.value, 'Flag copied from the RangeBox clipboard. Check it and submit.')
}

const timeRemaining = ref(null)
const impersonation = ref(null)

let rfb = null
let reconnectTimer = null
let initialConnectTimer = null
let scaleTimer = null
let reconnectAttempts = 0
let resizeObserver = null
let timerInterval = null
let unmounted = false
const MAX_RECONNECT_ATTEMPTS = 5

const STATUS_LABELS = {
  connecting: 'Connecting...',
  connected: 'Connected',
  disconnected: 'Disconnected',
}
const statusLabel = computed(() => STATUS_LABELS[connectionState.value] || connectionState.value)

const imageDisplayName = computed(() => {
  if (!props.imageName) return ''
  const names = { kali: 'Kali', ubuntu: 'Ubuntu', remnux: 'REMnux' }
  return names[props.imageName.toLowerCase()] || props.imageName
})

const isAdminViewer = computed(() => !!props.adminTargetUserId)
const labCompleted = computed(() => flagAccepted.value || !!props.labContext?.completed)

const toolbarLabel = computed(() => {
  if (isAdminViewer.value) return `Admin View — Student ${props.adminTargetUserId}`
  return imageDisplayName.value ? `RangeBox - ${imageDisplayName.value}` : 'RangeBox'
})

const formattedTime = computed(() => {
  if (timeRemaining.value === null) return ''
  const t = Math.max(0, timeRemaining.value)
  const h = Math.floor(t / 3600)
  const m = Math.floor((t % 3600) / 60)
  const s = t % 60
  if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

const fetchTimeRemaining = async () => {
  if (!props.showTimer) return
  if (isAdminViewer.value) return  // No per-session timer for an admin watching a student
  if (props.standalone && props.statusData) {
    // Parent already fetched /rangebox/standalone/status; reuse it.
    const t = props.statusData.time_remaining
    if (t !== undefined && t !== null) {
      timeRemaining.value = t
    }
    return
  }
  try {
    const endpoint = props.standalone
      ? '/rangebox/standalone/status'
      : `/rangebox/${props.sessionId}/status`
    const { data } = await axios.get(endpoint)
    if (data.time_remaining !== undefined && data.time_remaining !== null) {
      timeRemaining.value = data.time_remaining
    }
  } catch {
    // Silently ignore — timer is a nice-to-have
  }
}

const startTimer = () => {
  stopTimer()
  timerInterval = setInterval(() => {
    if (timeRemaining.value !== null) {
      timeRemaining.value = Math.max(0, timeRemaining.value - 1)
      if (timeRemaining.value <= 0) {
        // Session expired — disconnect
        connectionState.value = 'disconnected'
        if (rfb) {
          try { rfb.disconnect() } catch {}
          rfb = null
        }
        stopTimer()
      }
    }
  }, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const fetchImpersonationStatus = async () => {
  if (!props.standalone) return
  try {
    const { data } = await axios.get('/admin/impersonate/status')
    impersonation.value = data.active ? data : null
  } catch {
    // Keep badge visible on errors (auth hiccups, network blips)
  }
}

// Started from onMounted only for admin standalone sessions; pauses while the
// tab is hidden and fires an immediate refresh on return.
const impersonationPoll = usePoll(fetchImpersonationStatus, 10000, { auto: false, immediate: true })

// RFB is imported lazily inside connect() so noVNC stays out of the shared
// bundle and only loads when a VNC connection is actually opened.

const getWsUrl = async () => {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  let path
  if (isAdminViewer.value) {
    // Admin viewing a student's RangeBox
    path = `admin/${props.adminTargetUserId}/${props.sessionId}/vnc`
    } else if (props.standalone) {
    path = 'standalone/vnc'
  } else {
    path = `${props.sessionId}/vnc`
  }
  // Exchange JWT for a short-lived, single-use ticket to avoid leaking
  // the long-lived JWT into WebSocket URLs, logs, and browser history.
  let credential
  try {
    const { data } = await axios.post('/rangebox/ws-ticket')
    credential = data.ticket
  } catch {
    // Do NOT fall back to raw JWT — it would leak into URLs, logs, and browser history.
    // Force the user to retry instead.
    console.warn('Failed to obtain WebSocket ticket — connection will not be established.')
    return null
  }
  return `${proto}//${window.location.host}/api/rangebox/${path}?token=${encodeURIComponent(credential)}`
}

const connect = async () => {
  if (rfb) {
    try { rfb.disconnect() } catch {}
    rfb = null
  }

  connectionState.value = 'connecting'
  connectionMessage.value = ''

  await nextTick()
  const target = vncContainer.value
  if (!target) return

  // Clear previous canvas
  while (target.firstChild) {
    if (!target.firstChild.classList?.contains('rangebox__connecting') &&
        !target.firstChild.classList?.contains('rangebox__disconnected')) {
      target.removeChild(target.firstChild)
    } else {
      break
    }
  }

  try {
    const { default: RFB } = await import('@novnc/novnc')
    const url = await getWsUrl()
    if (!url) {
      connectionState.value = 'disconnected'
      return
    }
    rfb = new RFB(target, url, {
      wsProtocols: ['binary'],
    })

    rfb.viewOnly = false
    rfb.scaleViewport = true
    rfb.resizeSession = true
    rfb.clipViewport = false
    rfb.showDotCursor = true
    applyQuality()

    rfb.addEventListener('connect', () => {
      connectionState.value = 'connected'
      connectionMessage.value = ''
      reconnectAttempts = 0
      try { rfb.focus() } catch {}
      // Force noVNC to recalculate scale after layout settles
      scaleTimer = setTimeout(() => {
        if (rfb && !unmounted) {
          rfb.scaleViewport = false
          rfb.scaleViewport = true
        }
      }, 200)
      // Fetch session time remaining and start countdown
      if (props.showTimer) {
        fetchTimeRemaining().then(() => {
          if (timeRemaining.value !== null) startTimer()
        })
      }
    })

    rfb.addEventListener('securityfailure', (e) => {
      connectionMessage.value =
        e.detail?.reason || 'The desktop rejected the connection. Try reconnecting.'
    })

    rfb.addEventListener('credentialsrequired', () => {
      connectionMessage.value =
        'The desktop asked for credentials this viewer does not hold. Reconnect the session.'
    })

    rfb.addEventListener('disconnect', (e) => {
      connectionState.value = 'disconnected'
      rfb = null

      // Auto-reconnect on unexpected disconnect
      if (!e.detail.clean && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++
        const delay = Math.min(2000 * reconnectAttempts, 10000)
        console.log(`RangeBox reconnecting in ${delay}ms (attempt ${reconnectAttempts})`)
        reconnectTimer = setTimeout(connect, delay)
      }
    })

    rfb.addEventListener('clipboard', (e) => {
      if (e.detail.text) {
        clipboardText.value = e.detail.text
        // Copying a flag inside the guest should land it in the flag field,
        // so the learner can submit without a second copy/paste round trip.
        if (props.labContext && !labCompleted.value && FLAG_PATTERN.test(e.detail.text)) {
          flagValue.value = extractFlag(e.detail.text)
          flagMessage.value = 'Flag captured from the desktop clipboard. Check it and submit.'
          flagError.value = false
        }
      }
    })

  } catch (e) {
    console.error('RangeBox connection failed:', e)
    connectionState.value = 'disconnected'
    // The container can be "running" before websockify accepts connections.
    // Retry a few times rather than leaving the user on a dead desktop.
    if (!unmounted && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++
      const delay = Math.min(2000 * reconnectAttempts, 10000)
      reconnectTimer = setTimeout(connect, delay)
    }
  }
}

const applyQuality = () => {
  const preset = QUALITY_PRESETS[qualityPreset.value] || QUALITY_PRESETS.balanced
  if (rfb) {
    rfb.qualityLevel = preset.quality
    rfb.compressionLevel = preset.compression
  }
}

watch(qualityPreset, (value) => {
  localStorage.setItem('ocr.rangebox.quality', value)
  applyQuality()
})

const focusRfb = () => {
  try { rfb?.focus() } catch {}
}

const sendCtrlAltDel = () => {
  try { rfb?.sendCtrlAltDel() } catch {}
  focusRfb()
}

async function readClipboardIntoPanel() {
  try {
    clipboardText.value = await navigator.clipboard.readText()
  } catch {
    // Clipboard permission is commonly blocked on http:// or by the browser.
    // Leave the textarea focused so Ctrl+V still works.
    showClipboard.value = true
  }
}

const handleFullscreenChange = () => {
  if (!document.fullscreenElement) isFullscreen.value = false
}

const toggleFullscreen = async () => {
  if (isFullscreen.value) {
    isFullscreen.value = false
    try {
      if (document.fullscreenElement) await document.exitFullscreen()
    } catch {}
    return
  }
  isFullscreen.value = true
  if (isCollapsed.value) isCollapsed.value = false
  try {
    await rangeboxRoot.value?.requestFullscreen?.()
  } catch {
    // The CSS fullscreen class still works when the browser refuses native
    // fullscreen (for example inside an iframe without allowfullscreen).
  }
}

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
  if (isCollapsed.value && isFullscreen.value) isFullscreen.value = false
}

const toggleClipboard = () => {
  showClipboard.value = !showClipboard.value
}

const closeViewer = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/exercises')
  }
}

const submitFlag = async () => {
  const labId = props.labContext?.lab_id
  const flag = extractFlag(flagValue.value)
  if (!labId || !flag || flagSubmitting.value) return
  flagValue.value = flag
  flagSubmitting.value = true
  flagMessage.value = ''
  flagError.value = false
  try {
    const params = props.labContext?.course_id
      ? { course_id: props.labContext.course_id }
      : {}
    const { data } = await axios.post(
      `/exercises/labs/${labId}/submit-flag`,
      { flag },
      { params },
    )
    flagError.value = !data?.correct
    flagMessage.value = data?.message || (data?.correct ? 'Flag accepted.' : 'Flag not accepted yet.')
    if (data?.correct) {
      flagValue.value = ''
      flagAccepted.value = true
    }
  } catch (error) {
    flagError.value = true
    flagMessage.value = error.response?.data?.detail || 'Could not submit the flag. Try again.'
  } finally {
    flagSubmitting.value = false
  }
}

// Getting text into the guest by TYPING it as keystrokes. rfb.clipboardPasteFrom
// only sets the RFB clipboard channel, which needs a clipboard agent inside the
// guest to land anywhere -- Dockur Windows ships none, so the old "Send to VM"
// silently did nothing. sendKey injects each character as a real keypress, which
// the guest receives regardless of clipboard support, landing directly in the
// focused window (e.g. PowerShell). QEMU's VNC maps keysyms (incl. shift for
// uppercase/symbols) itself, so a keysym-only event per char is enough.
const _KEYSYMS = { '\n': 0xff0d, '\r': 0xff0d, '\t': 0xff09 }
function _charKeysym(ch) {
  if (_KEYSYMS[ch] != null) return _KEYSYMS[ch]
  const cp = ch.codePointAt(0)
  return cp < 0x100 ? cp : 0x01000000 + cp   // Latin-1: keysym==codepoint; else X11 Unicode keysym
}
const sendClipboard = async () => {
  if (!rfb || !clipboardText.value) return
  const text = clipboardText.value
  try { rfb.focus() } catch {}
  // Best-effort clipboard set too (harmless; helps guests that DO have an agent).
  try { rfb.clipboardPasteFrom(text) } catch {}
  for (const ch of text) {
    const keysym = _charKeysym(ch)
    try {
      rfb.sendKey(keysym, null, true)
      rfb.sendKey(keysym, null, false)
    } catch {}
    await new Promise(r => setTimeout(r, 15))   // pace so the guest keeps up
  }
}

const receiveClipboard = () => {
  // Request clipboard from VNC — the 'clipboard' event handler above will catch it
  if (rfb) {
    rfb.focus()
  }
}

// Handle Escape key to exit fullscreen
const handleKeydown = (e) => {
  if (e.key === 'Escape' && isFullscreen.value) {
    isFullscreen.value = false
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  document.addEventListener('fullscreenchange', handleFullscreenChange)

  // Watch viewport container for size changes and re-trigger noVNC scaling
  if (vncContainer.value) {
    resizeObserver = new ResizeObserver(() => {
      if (rfb) {
        rfb.scaleViewport = false
        rfb.scaleViewport = true
      }
    })
    resizeObserver.observe(vncContainer.value)
  }

  // Check impersonation status for standalone RangeBox (admin only)
  if (isAdmin() && props.standalone) {
    impersonationPoll.start()
  }

  // Delay connection slightly to let the container's VNC server start
  initialConnectTimer = setTimeout(connect, 2000)
})

onUnmounted(() => {
  unmounted = true
  window.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  stopTimer()
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
  if (reconnectTimer) clearTimeout(reconnectTimer)
  if (initialConnectTimer) clearTimeout(initialConnectTimer)
  if (scaleTimer) clearTimeout(scaleTimer)
  if (rfb) {
    try { rfb.disconnect() } catch {}
    rfb = null
  }
})

// Reconnect if session changes
watch(() => props.sessionId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    reconnectAttempts = 0
    connect()
  }
})
</script>

<style scoped>
.rangebox {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color, #2a2a3e);
  border-radius: 8px;
  overflow: hidden;
  background: #1a1a2e;
  margin-bottom: 1rem;
}

.rangebox--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
  margin: 0;
}

.rangebox--collapsed {
  height: auto;
}

/* Toolbar */
.rangebox__toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: #16162a;
  border-bottom: 1px solid var(--border-color, #2a2a3e);
  flex-shrink: 0;
  gap: 0.5rem;
}

.rangebox__toolbar-left,
.rangebox__toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rangebox__label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #a0a0c0;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.rangebox__impersonate-badge {
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
  background: rgba(217, 83, 79, 0.85);
  padding: 0.15rem 0.6rem;
  border-radius: 4px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  animation: pulse 2s infinite;
}

.rangebox__timer {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  color: #5cb85c;
  background: rgba(92, 184, 92, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.rangebox__timer--warning {
  color: #d9534f;
  background: rgba(217, 83, 79, 0.15);
  animation: pulse 1.5s infinite;
}

.rangebox__status {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.75rem;
  color: #808090;
}

.rangebox__status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #808090;
}

.rangebox__status--connecting .rangebox__status-dot {
  background: #f0ad4e;
  animation: pulse 1.5s infinite;
}

.rangebox__status--connected .rangebox__status-dot {
  background: #5cb85c;
}

.rangebox__status--disconnected .rangebox__status-dot {
  background: #d9534f;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.rangebox__btn {
  padding: 0.25rem 0.6rem;
  font-size: 0.75rem;
  border: 1px solid var(--border-color, #2a2a3e);
  border-radius: 4px;
  background: transparent;
  color: #a0a0c0;
  cursor: pointer;
  transition: all 0.15s;
}

.rangebox__select {
  padding: 0.25rem 0.4rem;
  border: 1px solid var(--border-color, #2a2a3e);
  border-radius: 4px;
  background: #12122a;
  color: #a0a0c0;
  font-size: 0.72rem;
}

.rangebox__btn:hover {
  background: rgba(255,255,255,0.05);
  color: #e0e0f0;
}

.rangebox__btn--active {
  background: rgba(100,100,255,0.15);
  border-color: rgba(100,100,255,0.4);
  color: #a0a0ff;
}

.rangebox__btn--primary {
  background: rgba(92, 184, 92, 0.2);
  border-color: rgba(92, 184, 92, 0.4);
  color: #5cb85c;
}

.rangebox__btn--primary:hover {
  background: rgba(92, 184, 92, 0.3);
}

.rangebox__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Clipboard panel */
.rangebox__clipboard {
  padding: 0.5rem 0.75rem;
  background: #12122a;
  border-bottom: 1px solid var(--border-color, #2a2a3e);
}

.rangebox__clipboard textarea {
  width: 100%;
  background: #1a1a2e;
  border: 1px solid var(--border-color, #2a2a3e);
  border-radius: 4px;
  color: #e0e0f0;
  padding: 0.5rem;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.8rem;
  resize: vertical;
}

.rangebox__clipboard-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.rangebox__clipboard-note {
  margin: 0.35rem 0 0;
  color: #808090;
  font-size: 0.66rem;
}

.rangebox__clipboard-warning {
  margin: 0.25rem 0 0;
  color: #f0ad4e;
  font-size: 0.7rem;
  font-weight: 600;
}

/* VNC viewport */
.rangebox__viewport {
  position: relative;
  flex: 1;
  min-height: 400px;
  background: #000;
  overflow: hidden;
}

.rangebox--fullscreen .rangebox__viewport {
  min-height: 0;
}

/* noVNC handles canvas sizing via scaleViewport — do NOT override
   width/height here or mouse coordinates will be offset. */

/* Lab dock: target IPs and flag entry inside the RangeBox window */
.rangebox__lab-dock {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.9rem;
  padding: 0.55rem 0.75rem;
  background: #12122a;
  border-top: 1px solid var(--border-color, #2a2a3e);
}

.rangebox__lab-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.75rem;
  min-width: 0;
}

.rangebox__lab-name {
  color: #e0e0f0;
  font-size: 0.8rem;
  white-space: nowrap;
}

.rangebox__lab-network,
.rangebox__ip-chip {
  color: #a0a0c0;
  font-size: 0.72rem;
  white-space: nowrap;
}

.rangebox__ip-chip {
  padding: 0.12rem 0.45rem;
  border: 1px solid rgba(100, 100, 255, 0.28);
  border-radius: 999px;
  background: rgba(100, 100, 255, 0.1);
}

.rangebox__lab-network code,
.rangebox__ip-chip code {
  color: #c7d2fe;
}

.rangebox__flag-accepted {
  color: #5cb85c;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.rangebox__flag-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.45rem;
  margin-left: auto;
  min-width: 0;
}

.rangebox__flag-label {
  color: #a0a0c0;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.rangebox__flag-input {
  width: min(260px, 40vw);
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--border-color, #2a2a3e);
  border-radius: 4px;
  background: #1a1a2e;
  color: #e0e0f0;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 0.78rem;
}

.rangebox__flag-input:focus {
  outline: 2px solid rgba(100, 100, 255, 0.55);
  outline-offset: 1px;
}

.rangebox__flag-message {
  flex-basis: 100%;
  color: #5cb85c;
  font-size: 0.72rem;
}

.rangebox__flag-hint {
  margin: 0.35rem 0 0;
  color: #808090;
  font-size: 0.68rem;
  line-height: 1.4;
}

.rangebox__disconnected-hint {
  max-width: 32rem;
  margin: 0.35rem 0 0.75rem;
  color: #f0ad4e;
  font-size: 0.78rem;
  line-height: 1.45;
  text-align: center;
}

.rangebox__flag-message--error,
.rangebox__flag-done {
  color: #f0ad4e;
}

.rangebox__flag-done {
  margin: 0;
  font-size: 0.72rem;
}

/* Connecting overlay */
.rangebox__connecting,
.rangebox__disconnected {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.85);
  color: #a0a0c0;
  z-index: 10;
}

.rangebox__connecting-hint {
  font-size: 0.8rem;
  color: #606080;
  margin-top: 0.25rem;
}

.rangebox__spinner {
  width: 36px;
  height: 36px;
  border: 3px solid #2a2a3e;
  border-top-color: #5cb85c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.rangebox__btn--close {
  margin-left: 0.35rem;
  border-color: color-mix(in srgb, var(--danger) 45%, transparent);
  color: var(--danger);
}

.rangebox__btn--close:hover {
  background: var(--danger-bg);
  color: var(--danger);
}

@media (prefers-reduced-motion: reduce) {
  .rangebox__spinner,
  .rangebox__status--connecting .rangebox__status-dot,
  .rangebox__impersonate-badge,
  .rangebox__timer--warning {
    animation: none;
  }
  .rangebox__btn {
    transition: none;
  }
}
</style>


