/**
 * Capture Cyber DNA and Cyber GPS screenshots from a dev deployment.
 *
 *   UI_BASE_URL=https://172.16.16.44 \
 *   UI_SMOKE_USERNAME=... UI_SMOKE_PASSWORD=... \
 *   node platform/frontend/ui-dna-screenshots.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium, request } from 'playwright'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..')
const IMG = path.join(ROOT, 'Manual-Lite', '02_Student_Guide', 'img')
const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''

if (!BASE) {
  console.log('DNA screenshots skipped: UI_BASE_URL is required.')
  process.exit(0)
}

async function login() {
  if (!USERNAME || !PASSWORD) return null
  const api = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
  try {
    const response = await api.post('/api/auth/login', {
      form: { username: USERNAME, password: PASSWORD },
    })
    if (!response.ok()) {
      console.error(`Login failed: ${response.status()} ${await response.text()}`)
      return null
    }
    const body = await response.json()
    const token = body.access_token || body.token || ''
    if (!token) return null
    const me = await api.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    return { token, user: me.ok() ? await me.json() : {} }
  } finally {
    await api.dispose()
  }
}

const session = await login()
if (!session?.token) {
  console.error('DNA screenshots failed: provide UI_SMOKE_USERNAME / UI_SMOKE_PASSWORD.')
  process.exit(1)
}

fs.mkdirSync(IMG, { recursive: true })
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  ignoreHTTPSErrors: true,
  viewport: { width: 1440, height: 1200 },
  deviceScaleFactor: 2,
})
await context.addInitScript(({ token, user }) => {
  localStorage.setItem('token', token)
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('theme', 'dark')
  localStorage.setItem('ocr_orientation_seen_v1_' + user.username, '1')
}, { token: session.token, user: session.user })

const page = await context.newPage()
const errors = []
page.on('pageerror', (error) => errors.push(String(error)))

async function shot(selector, filename, label) {
  const locator = page.locator(selector).first()
  await locator.waitFor({ state: 'visible', timeout: 45000 })
  await locator.scrollIntoViewIfNeeded()
  await page.waitForTimeout(400)
  const target = path.join(IMG, filename)
  await locator.screenshot({ path: target, animations: 'disabled' })
  console.log(`WROTE: ${label} -> ${path.relative(ROOT, target)}`)
}

try {
  await page.goto(`${BASE}/profile?tab=skill-tree`, {
    waitUntil: 'networkidle',
    timeout: 60000,
  })
  await shot('.dna-section', 'profile-cyber-dna.png', 'Cyber DNA section')
  await shot('.dna-tree', 'profile-dna-tree.png', 'Cyber DNA spider chart')
  await shot('.dna-ce', 'profile-dna-continuing-education.png', 'Continuing education card')
  await shot('.dna-class-card', 'profile-dna-class.png', 'Cyber DNA class card')

  await page.goto(`${BASE}/profile?tab=careers`, {
    waitUntil: 'networkidle',
    timeout: 60000,
  })
  await shot('.gps', 'profile-cyber-gps.png', 'Cyber GPS view')
  await shot('.gps-panel', 'profile-cyber-gps-signal.png', 'Cyber GPS signal panel')

  if (errors.length) {
    console.error('Page errors:', errors.slice(0, 5))
    process.exitCode = 1
  }
} finally {
  await context.close()
  await browser.close()
}
