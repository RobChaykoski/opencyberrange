/**
 * Deployment UI smoke test.
 *
 * Required environment:
 *   UI_BASE_URL       e.g. https://172.16.16.44
 *   UI_SMOKE_TOKEN    a JWT for a student or admin test account
 *
 * Optional:
 *   UI_EXPECTED_VERSION  e.g. 2.4.1
 *   UI_ARTIFACT_DIR      screenshot directory (default ui-smoke-artifacts)
 *
 * The script is safe to run against a live deployment: it only performs GETs
 * and screenshot captures.
 */
import fs from 'node:fs'
import path from 'node:path'
import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const TOKEN = process.env.UI_SMOKE_TOKEN || ''
const EXPECTED = process.env.UI_EXPECTED_VERSION || ''
const OUT = process.env.UI_ARTIFACT_DIR || 'ui-smoke-artifacts'

if (!BASE || !TOKEN) {
  console.log('UI smoke skipped: UI_BASE_URL and UI_SMOKE_TOKEN are required.')
  process.exit(0)
}

fs.mkdirSync(OUT, { recursive: true })
const checks = []
const check = (name, ok, detail = '') => {
  checks.push({ name, ok, detail })
  console.log(`${ok ? 'PASS' : 'FAIL'}: ${name}${detail ? ' - ' + detail : ''}`)
}

const api = await request.newContext({
  baseURL: BASE,
  ignoreHTTPSErrors: true,
  extraHTTPHeaders: { Authorization: `Bearer ${TOKEN}` },
})
const version = await (await api.get('/api/version')).json()
const me = await (await api.get('/api/auth/me')).json()
await api.dispose()

if (EXPECTED) check('API version', version.version === EXPECTED, `${version.version} (expected ${EXPECTED})`)

const browser = await chromium.launch({
  headless: true,
  ...(process.env.UI_BROWSER_EXECUTABLE
    ? { executablePath: process.env.UI_BROWSER_EXECUTABLE }
    : {}),
})
const errors = []

async function contextFor(viewport) {
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    viewport,
    deviceScaleFactor: 2,
    isMobile: viewport.width <= 768,
    hasTouch: viewport.width <= 768,
  })
  await context.addInitScript(({ token, me }) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(me))
    localStorage.setItem('ocr_orientation_seen_v1_' + me.username, '1')
  }, { token: TOKEN, me })
  const page = await context.newPage()
  page.on('pageerror', e => errors.push(String(e)))
  return { context, page }
}

const mobile = await contextFor({ width: 390, height: 844 })
await mobile.page.goto(`${BASE}/dashboard`, { waitUntil: 'networkidle', timeout: 45000 })
await mobile.page.waitForTimeout(1000)
check('mobile top bar', await mobile.page.locator('.mobile-topbar').isVisible())
check('mobile sidebar off-canvas', await mobile.page.evaluate(() => {
  const r = document.querySelector('.sidebar').getBoundingClientRect()
  return r.right <= 1
}))
check('mobile no horizontal overflow', await mobile.page.evaluate(() =>
  document.documentElement.scrollWidth - window.innerWidth <= 1
))
const isStudent = me.role === 'student'
check('student bottom tabs', !isStudent || await mobile.page.locator('.mobile-tabbar').isVisible())
await mobile.page.screenshot({ path: path.join(OUT, 'mobile-dashboard.png') })
await mobile.context.close()

const desktop = await contextFor({ width: 1280, height: 900 })
await desktop.page.goto(`${BASE}/profile?tab=overview`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(900)
check('profile five tabs', await desktop.page.locator('[role="tab"]').count() === 5)
await desktop.page.goto(`${BASE}/events`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(600)
check('events page', /events/i.test(await desktop.page.locator('body').innerText()))
await desktop.page.goto(`${BASE}/rangebox`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(600)
check('RangeBox tab', (await desktop.page.locator('body').innerText()).toLowerCase().includes('standalone desktop'))
await desktop.page.screenshot({ path: path.join(OUT, 'desktop-rangebox.png') })
await desktop.context.close()

check('no page errors', errors.length === 0, errors.slice(0, 3).join(' | '))
await browser.close()

fs.writeFileSync(path.join(OUT, 'checks.json'), JSON.stringify(checks, null, 2))
const failed = checks.filter(c => !c.ok)
console.log(`\nTOTAL ${checks.length} checks, ${failed.length} failed`)
process.exit(failed.length ? 1 : 0)
