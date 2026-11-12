/**
 * Deployment UI smoke test.
 *
 * Required environment:
 *   UI_BASE_URL          e.g. https://192.168.120.44
 *   UI_SMOKE_TOKEN       a JWT for a student or admin test account, or
 *   UI_SMOKE_USERNAME / UI_SMOKE_PASSWORD to log in for a short-lived token
 *
 * Optional:
 *   UI_EXPECTED_VERSION  e.g. 2.5.0
 *   UI_ARTIFACT_DIR      screenshot directory (default ui-smoke-artifacts)
 *   UI_BROWSER_EXECUTABLE  use a system Chromium/Edge instead of Playwright's
 *   UI_PRIVACY_USERNAME / UI_PRIVACY_PASSWORD
 *                        admin account used for the privacy setting checks.
 *                        Falls back to the main smoke account when it is admin.
 *
 * The script is safe to run against a live deployment: it only performs GETs,
 * one optional login, one temporary privacy-default toggle that is restored,
 * and screenshot captures.
 */
import fs from 'node:fs'
import path from 'node:path'
import { chromium, request } from 'playwright'

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
let TOKEN = process.env.UI_SMOKE_TOKEN || ''
const USERNAME = process.env.UI_SMOKE_USERNAME || ''
const PASSWORD = process.env.UI_SMOKE_PASSWORD || ''
const PRIVACY_USERNAME = process.env.UI_PRIVACY_USERNAME || ''
const PRIVACY_PASSWORD = process.env.UI_PRIVACY_PASSWORD || ''
const EXPECTED = process.env.UI_EXPECTED_VERSION || ''
const OUT = process.env.UI_ARTIFACT_DIR || 'ui-smoke-artifacts'
const STARTED_AT = new Date().toISOString()
const ARTIFACTS = []

if (!BASE) {
  console.log('UI smoke skipped: UI_BASE_URL is required.')
  process.exit(0)
}

async function loginAs(username, password) {
  const loginApi = await request.newContext({ baseURL: BASE, ignoreHTTPSErrors: true })
  try {
    const login = await loginApi.post('/api/auth/login', {
      form: { username, password },
    })
    if (!login.ok()) return null
    const body = await login.json()
    const token = body.access_token || body.token || ''
    if (!token) return null
    const meResp = await loginApi.get('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const user = meResp.ok() ? await meResp.json() : {}
    return { token, user }
  } finally {
    await loginApi.dispose()
  }
}

if (!TOKEN && USERNAME && PASSWORD) {
  const session = await loginAs(USERNAME, PASSWORD)
  if (session) TOKEN = session.token
}

if (!TOKEN) {
  console.log('UI smoke skipped: set UI_SMOKE_TOKEN or UI_SMOKE_USERNAME / UI_SMOKE_PASSWORD.')
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

let privacyToken = TOKEN
let privacyMe = me
if (PRIVACY_USERNAME && PRIVACY_PASSWORD) {
  const privacySession = await loginAs(PRIVACY_USERNAME, PRIVACY_PASSWORD)
  if (privacySession) {
    privacyToken = privacySession.token
    privacyMe = privacySession.user
  } else {
    check('privacy admin login', false, 'UI_PRIVACY_USERNAME / UI_PRIVACY_PASSWORD were rejected')
  }
}

if (EXPECTED) check('API version', version.version === EXPECTED, `${version.version} (expected ${EXPECTED})`)

const browser = await chromium.launch({
  headless: true,
  ...(process.env.UI_BROWSER_EXECUTABLE
    ? { executablePath: process.env.UI_BROWSER_EXECUTABLE }
    : {}),
})
const errors = []

async function contextFor(viewport, token = TOKEN, user = me) {
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
  }, { token, me: user })
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
ARTIFACTS.push('mobile-dashboard.png')
await mobile.context.close()

const desktop = await contextFor({ width: 1280, height: 900 })
await desktop.page.goto(`${BASE}/profile?tab=overview`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(900)
const profileTabCount = await desktop.page.locator('[role="tab"]').count()
check('profile tabs', profileTabCount === 5 || profileTabCount === 6, `${profileTabCount} tabs`)
await desktop.page.goto(`${BASE}/events`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(600)
check('events page', /events/i.test(await desktop.page.locator('body').innerText()))
await desktop.page.goto(`${BASE}/rangebox`, { waitUntil: 'networkidle', timeout: 45000 })
await desktop.page.waitForTimeout(600)
check('RangeBox tab', (await desktop.page.locator('body').innerText()).toLowerCase().includes('standalone desktop'))
await desktop.page.screenshot({ path: path.join(OUT, 'desktop-rangebox.png') })
ARTIFACTS.push('desktop-rangebox.png')
await desktop.context.close()

if (privacyMe.role === 'admin') {
  let privacyApi = null
  let privacy = null
  let fresh = null
  let originalDefault = true
  let setDefault = null
  try {
    privacyApi = await request.newContext({
      baseURL: BASE,
      ignoreHTTPSErrors: true,
      extraHTTPHeaders: { Authorization: `Bearer ${privacyToken}` },
    })

    const settingsResp = await privacyApi.get('/api/settings/security')
    const settings = settingsResp.ok() ? await settingsResp.json() : []
    const defaultRow = settings.find((item) => item.key === 'privacy_default_on')
    check('privacy default setting exists', !!defaultRow)
    originalDefault = defaultRow?.value === 'true'

    const aboutResp = await privacyApi.get('/api/about')
    const about = aboutResp.ok() ? await aboutResp.json() : {}
    check(
      'About inventory version matches API',
      about?.platform?.version === version.version,
      `${about?.platform?.version || 'missing'} (API ${version.version || 'unknown'})`
    )

    const openSettings = async (page) => {
      await page.goto(`${BASE}/admin?tab=settings`, { waitUntil: 'networkidle', timeout: 45000 })
      await page.getByText('Platform Settings', { exact: true }).waitFor({ timeout: 20000 })
      await page.locator('.setting-row', { hasText: 'Privacy Mode (this browser)' }).waitFor({ timeout: 20000 })
      await page.locator('.setting-row', { hasText: 'Default Privacy Mode' }).waitFor({ timeout: 20000 })
    }
    const rowButton = (page, label) =>
      page.locator('.setting-row', { hasText: label }).locator('button')
    const buttonState = async (page, label) =>
      (await rowButton(page, label).textContent()).trim()
    setDefault = async (value) => {
      const response = await privacyApi.put('/api/settings/', {
        data: { settings: { privacy_default_on: String(value) } },
      })
      return response.ok()
    }
    const clickDefault = async (page) => {
      await Promise.all([
        page.waitForResponse(
          (response) => response.url().includes('/api/settings/')
            && response.request().method() === 'PUT',
          { timeout: 20000 }
        ),
        rowButton(page, 'Default Privacy Mode').click(),
      ])
      await page.waitForTimeout(250)
    }
    const readDefault = async () => {
      const response = await privacyApi.get('/api/settings/security')
      if (!response.ok()) return null
      const rows = await response.json()
      return rows.find((item) => item.key === 'privacy_default_on')?.value || null
    }

    privacy = await contextFor({ width: 1280, height: 900 }, privacyToken, privacyMe)
    await openSettings(privacy.page)
    const initialCurrent = await buttonState(privacy.page, 'Privacy Mode (this browser)')
    check(
      'fresh admin privacy mode matches platform default',
      initialCurrent === (originalDefault ? 'Enabled' : 'Disabled'),
      `${initialCurrent} (default ${originalDefault ? 'Enabled' : 'Disabled'})`
    )

    await rowButton(privacy.page, 'Privacy Mode (this browser)').click()
    await privacy.page.waitForTimeout(250)
    const flippedCurrent = await buttonState(privacy.page, 'Privacy Mode (this browser)')
    await rowButton(privacy.page, 'Privacy Mode (this browser)').click()
    await privacy.page.waitForTimeout(250)
    const restoredCurrent = await buttonState(privacy.page, 'Privacy Mode (this browser)')
    check(
      'current-browser privacy toggle flips and restores',
      flippedCurrent !== initialCurrent && restoredCurrent === initialCurrent,
      `${initialCurrent} -> ${flippedCurrent} -> ${restoredCurrent}`
    )

    if (originalDefault) {
      await clickDefault(privacy.page)
      check(
        'default privacy toggle turns off',
        (await buttonState(privacy.page, 'Default Privacy Mode')) === 'Disabled'
      )
    } else {
      await clickDefault(privacy.page)
      check(
        'default privacy toggle turns on',
        (await buttonState(privacy.page, 'Default Privacy Mode')) === 'Enabled'
      )
      await clickDefault(privacy.page)
      check(
        'default privacy toggle returns off',
        (await buttonState(privacy.page, 'Default Privacy Mode')) === 'Disabled'
      )
    }
    check('privacy_default_on persists as false', (await readDefault()) === 'false')
    await privacy.page.screenshot({
      path: path.join(OUT, 'privacy-default-off.png'),
      fullPage: true,
    })
    ARTIFACTS.push('privacy-default-off.png')

    fresh = await contextFor({ width: 1280, height: 900 }, privacyToken, privacyMe)
    await openSettings(fresh.page)
    check(
      'new admin browser inherits default off',
      (await buttonState(fresh.page, 'Privacy Mode (this browser)')) === 'Disabled'
    )

    await fresh.page.evaluate(() => {
      localStorage.setItem('privacy-mode', 'on')
      localStorage.removeItem('privacy-mode-explicit')
    })
    await fresh.page.reload({ waitUntil: 'networkidle' })
    await openSettings(fresh.page)
    check(
      'legacy auto-written on follows the platform default',
      (await buttonState(fresh.page, 'Privacy Mode (this browser)')) === 'Disabled'
    )

    await fresh.page.evaluate(() => {
      localStorage.setItem('privacy-mode', 'on')
      localStorage.setItem('privacy-mode-explicit', '1')
    })
    await fresh.page.reload({ waitUntil: 'networkidle' })
    await openSettings(fresh.page)
    check(
      'explicit per-browser preference wins',
      (await buttonState(fresh.page, 'Privacy Mode (this browser)')) === 'Enabled'
    )
    await fresh.page.screenshot({
      path: path.join(OUT, 'privacy-explicit-on.png'),
      fullPage: true,
    })
    ARTIFACTS.push('privacy-explicit-on.png')
  } catch (err) {
    check('privacy checks completed', false, String(err))
  } finally {
    if (privacyApi) {
      const restored = setDefault ? await setDefault(originalDefault) : false
      check('privacy default restored', restored, String(originalDefault))
      await privacyApi.dispose()
    }
    if (privacy?.context) await privacy.context.close()
    if (fresh?.context) await fresh.context.close()
  }
} else {
  console.log('Privacy checks skipped: set UI_PRIVACY_USERNAME / UI_PRIVACY_PASSWORD to an admin account.')
}

check('no page errors', errors.length === 0, errors.slice(0, 3).join(' | '))
await browser.close()

fs.writeFileSync(path.join(OUT, 'checks.json'), JSON.stringify(checks, null, 2))
const failed = checks.filter(c => !c.ok)
const evidence = {
  schema: 'ocr-ui-smoke/1',
  started_at: STARTED_AT,
  finished_at: new Date().toISOString(),
  base_url: BASE,
  expected_version: EXPECTED || null,
  version: version.version || null,
  release: version.release || null,
  role: me.role || null,
  username: me.username || null,
  checks,
  failed: failed.length,
  result: failed.length ? 'fail' : 'pass',
  artifacts: ARTIFACTS,
  ci: {
    run_id: process.env.GITHUB_RUN_ID || null,
    sha: process.env.GITHUB_SHA || null,
    ref: process.env.GITHUB_REF || null,
  },
}
fs.writeFileSync(path.join(OUT, 'evidence.json'), JSON.stringify(evidence, null, 2))
console.log(`\nEvidence written to ${path.join(OUT, 'evidence.json')}`)
console.log(`TOTAL ${checks.length} checks, ${failed.length} failed`)
process.exit(failed.length ? 1 : 0)
