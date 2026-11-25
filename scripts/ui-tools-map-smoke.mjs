#!/usr/bin/env node
/**
 * Threat-map and Tools UI smoke.
 *
 * Local mock mode (default):
 *   cd platform/frontend && npm run preview -- --port 4173
 *   node scripts/ui-tools-map-smoke.mjs
 *
 * Live mode:
 *   UI_BASE_URL=https://<host> UI_SMOKE_TOKEN=<jwt> node scripts/ui-tools-map-smoke.mjs
 *
 * Optional:
 *   UI_MOCK_API=1             force mock mode even when a token is present
 *   UI_SMOKE_USER='{"username":"...","role":"student"}'  live-mode user
 *   UI_ARTIFACT_DIR           screenshot directory
 *   UI_BROWSER_EXECUTABLE     system Chromium/Edge
 *
 * The local mode intercepts every /api call, so it never touches a deployment.
 * The live mode performs GETs and browser interactions only.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)))
const PLAYWRIGHT = process.env.UI_PLAYWRIGHT_PATH || path.join(ROOT, 'platform', 'frontend', 'node_modules', 'playwright')

async function loadPlaywright(spec) {
  if (spec.startsWith('file:')) return import(spec)
  if (path.isAbsolute(spec) || spec.startsWith('.')) {
    const resolved = path.resolve(spec)
    const entry = fs.existsSync(path.join(resolved, 'index.mjs'))
      ? path.join(resolved, 'index.mjs')
      : resolved
    return import(pathToFileURL(entry).href)
  }
  return import(spec)
}

const { chromium } = await loadPlaywright(PLAYWRIGHT)

const BASE = (process.env.UI_BASE_URL || 'http://localhost:4173').replace(/\/$/, '')
const TOKEN = process.env.UI_SMOKE_TOKEN || ''
const MOCK = process.env.UI_MOCK_API === '1' || !TOKEN
const OUT = process.env.UI_ARTIFACT_DIR || 'ui-tools-map-artifacts'
const USER = (() => {
  try {
    return JSON.parse(process.env.UI_SMOKE_USER || '{}')
  } catch {
    return {}
  }
})()

const user = {
  username: USER.username || 'smoke_student',
  role: USER.role || 'student',
  first_name: USER.first_name || 'Smoke',
  last_name: USER.last_name || 'Student',
  must_change_password: false,
}

function mockThreat() {
  const file = path.join(ROOT, 'platform', 'backend', 'app', 'data', 'threat-awareness.json')
  const threat = JSON.parse(fs.readFileSync(file, 'utf8'))
  const reported = threat.totals.entries_reported || 0
  threat.sample = threat.mode === 'sample'
  threat.totals.coverage = reported && threat.totals.entries_observed
    ? Math.round((reported / threat.totals.entries_observed) * 10000) / 10000
    : 0
  for (const row of [...threat.categories, ...threat.countries]) {
    row.share = reported ? Math.round((row.count / reported) * 10000) / 10000 : 0
  }
  return threat
}

function mockRansom() {
  const file = path.join(ROOT, 'platform', 'backend', 'app', 'data', 'ransomware-activity.json')
  const ransom = JSON.parse(fs.readFileSync(file, 'utf8'))
  const posts = ransom.totals.window_posts || 0
  ransom.sample = ransom.mode === 'sample'
  for (const row of ransom.groups) {
    row.share = posts ? Math.round((row.count / posts) * 10000) / 10000 : 0
  }
  return ransom
}

const checks = []
function check(name, ok, detail = '') {
  checks.push({ name, ok: Boolean(ok), detail })
  console.log(`${ok ? 'PASS' : 'FAIL'}: ${name}${detail ? ' - ' + detail : ''}`)
}

async function reachable() {
  try {
    const response = await fetch(BASE, { redirect: 'manual' })
    return response.status > 0
  } catch {
    return false
  }
}

if (!(await reachable())) {
  console.error(`UI base is not reachable: ${BASE}`)
  console.error('Local mode: run "cd platform/frontend && npm run preview -- --port 4173" first.')
  process.exit(2)
}

fs.mkdirSync(OUT, { recursive: true })
const browser = await chromium.launch({
  headless: true,
  ...(process.env.UI_BROWSER_EXECUTABLE ? { executablePath: process.env.UI_BROWSER_EXECUTABLE } : {}),
})
const consoleErrors = []
const pageErrors = []

async function contextFor(viewport, theme) {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 2,
    ignoreHTTPSErrors: true,
    isMobile: viewport.width <= 768,
    hasTouch: viewport.width <= 768,
  })
  await context.addInitScript(({ token, user, theme }) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    localStorage.setItem('theme', theme)
    localStorage.setItem(`ocr_orientation_seen_v1_${user.username}`, '1')
  }, { token: MOCK ? 'mock-token' : TOKEN, user, theme })

  if (MOCK) {
    const threat = mockThreat()
    const ransom = mockRansom()
    await context.route('**/api/**', async (route) => {
      const url = route.request().url()
      if (url.includes('/api/setup/status')) {
        return route.fulfill({ json: { setup_complete: true } })
      }
      if (url.includes('/api/threat-awareness')) {
        return route.fulfill({ json: threat })
      }
      if (url.includes('/api/ransomware-activity')) {
        return route.fulfill({ json: ransom })
      }
      if (url.includes('/api/auth/me')) {
        return route.fulfill({ json: user })
      }
      return route.fulfill({ json: {} })
    })
  }

  return context
}

async function dismiss(page) {
  const understand = page.getByRole('button', { name: /I understand/i })
  if (await understand.count()) {
    await understand.click()
    await page.waitForTimeout(200)
  }
}

async function openPage(context, route) {
  const page = await context.newPage()
  page.on('console', (message) => {
    if (message.type() === 'error' && !/favicon|net::ERR_/i.test(message.text())) {
      consoleErrors.push(`${route}: ${message.text()}`)
    }
  })
  page.on('pageerror', (error) => pageErrors.push(`${route}: ${String(error)}`))
  await page.goto(`${BASE}${route}`, { waitUntil: 'networkidle' })
  await dismiss(page)
  await page.waitForTimeout(300)
  return page
}

async function checkThreatMap(page, label) {
  await page.waitForSelector('.threat-map')
  const markerCount = await page.locator('.threat-map__dot').count()
  check(`${label}: map markers render`, markerCount >= 100, `${markerCount} markers`)
  check(`${label}: snapshot boundary visible`, (await page.locator('.threat-map').innerText()).includes('not live'))

  const europe = page.locator('.threat-map__chip', { hasText: 'Europe' })
  if (await europe.count()) {
    await europe.first().click()
    await page.waitForTimeout(200)
    const filtered = await page.locator('.threat-map__dot').count()
    check(`${label}: region filter narrows the map`, filtered < markerCount, `${filtered} markers in Europe`)
    await page.locator('.threat-map__chip', { hasText: 'All regions' }).first().click()
    await page.waitForTimeout(200)
  }

  const hotspot = page.locator('.threat-map__row', { hasText: 'Germany' })
  if (await hotspot.count()) {
    await hotspot.first().click()
    const detail = await page.locator('.threat-map__detail').innerText()
    check(`${label}: selecting a hotspot shows the detail`, detail.includes('Germany') && detail.includes('rank'))
    const osm = await page.locator('.threat-map__external').getAttribute('href')
    check(`${label}: OpenStreetMap link is opt-in`, Boolean(osm && osm.includes('openstreetmap.org')), osm || '')
  } else {
    check(`${label}: Germany hotspot exists`, false)
  }

  const options = page.locator('.map-quiz__option')
  check(`${label}: challenge offers options`, (await options.count()) >= 3, `${await options.count()} options`)
  if (await options.count()) {
    await options.first().click()
    check(`${label}: challenge gives feedback`, await page.locator('.map-quiz__feedback').isVisible())
  }

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth)
  check(`${label}: no horizontal page overflow`, !overflow)
}

async function checkTools(page, label) {
  await page.waitForSelector('.tools-page')
  const cards = page.locator('.tool-card')
  check(`${label}: four tool cards render`, (await cards.count()) === 4, `${await cards.count()} cards`)

  const zapCard = page.locator('.tool-card', { hasText: 'OWASP ZAP' })
  check(`${label}: ZAP card has a download link`, (await zapCard.locator('a[href*="zaproxy.org/download"]').count()) === 1)
  await zapCard.getByRole('button', { name: /Open OWASP ZAP scan planner/i }).click()
  await page.waitForSelector('.tool-panel')
  check(`${label}: tool panel opens`, await page.locator('.tool-panel').isVisible())

  const frame = page.frameLocator('.tool-panel__frame')
  await frame.locator('#target').waitFor()
  await frame.locator('#target').fill('https://practice.lab/app')
  const baseline = await frame.locator('#command').innerText()
  check(`${label}: ZAP baseline command is generated`, baseline.includes('zap-baseline.py'), baseline.slice(0, 90))
  check(`${label}: copy is gated before authorisation`, await frame.locator('#copy').isDisabled())

  await frame.locator('#auth').check()
  await frame.locator('#disposable').check()
  await frame.locator('#scope').check()
  check(`${label}: copy unlocks after authorisation`, !(await frame.locator('#copy').isDisabled()))

  await frame.locator('#mode-full').click()
  const full = await frame.locator('#command').innerText()
  check(`${label}: full mode uses the active scanner`, full.includes('zap-full-scan.py'))
  check(`${label}: full mode shows the active-scan warning`, await frame.locator('#full-warning').isVisible())

  await page.locator('.tool-panel__close').click()
  await page.locator('.tool-panel').waitFor({ state: 'detached', timeout: 3000 })
  check(`${label}: tool panel closes`, (await page.locator('.tool-panel').count()) === 0)
}

try {
  const desktop = await contextFor({ width: 1440, height: 1000 }, 'dark')
  const threatPage = await openPage(desktop, '/threat-awareness')
  await checkThreatMap(threatPage, 'desktop')
  await threatPage.screenshot({ path: path.join(OUT, 'desktop-threat-map.png'), fullPage: true })

  const toolsPage = await openPage(desktop, '/toolbox')
  await checkTools(toolsPage, 'desktop')
  await toolsPage.screenshot({ path: path.join(OUT, 'desktop-tools.png'), fullPage: false })
  await desktop.close()

  const mobile = await contextFor({ width: 390, height: 844 }, 'light')
  const mobileThreat = await openPage(mobile, '/threat-awareness')
  await checkThreatMap(mobileThreat, 'mobile')
  await mobileThreat.screenshot({ path: path.join(OUT, 'mobile-threat-map.png'), fullPage: true })
  await mobile.close()
} finally {
  await browser.close()
}

check('no page errors', pageErrors.length === 0, pageErrors.slice(0, 3).join(' | '))
check('no console errors', consoleErrors.length === 0, consoleErrors.slice(0, 3).join(' | '))

const failures = checks.filter((row) => !row.ok)
console.log('')
console.log(`${checks.length - failures.length}/${checks.length} checks passed`)
if (failures.length) {
  console.error('Failures:')
  for (const failure of failures) console.error(`  - ${failure.name}${failure.detail ? `: ${failure.detail}` : ''}`)
  process.exit(1)
}
console.log(`Artifacts: ${OUT}`)
