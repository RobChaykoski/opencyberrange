#!/usr/bin/env node
/**
 * Learning-surface smoke test.
 *
 * Checks that the level UI matches the API for a signed-in learner:
 *   - the Quiz button appears only when the level is complete and has_quiz;
 *   - the Certificate button appears only when the level is complete;
 *   - no page or console errors are raised.
 *
 * Works with any learner account. Use a completed test account to exercise the
 * positive cases.
 *
 * Environment:
 *   UI_BASE_URL          deployment URL (required)
 *   UI_USERNAME          test learner (required)
 *   UI_PASSWORD          test learner password (required)
 *   UI_TRACK_SLUG        default high-school
 *   UI_ARTIFACT_DIR      default ui-learning-artifacts
 *   UI_PLAYWRIGHT_PATH   module path or file URL for playwright/playwright-core
 *   UI_BROWSER_EXECUTABLE system browser executable
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const PLAYWRIGHT = process.env.UI_PLAYWRIGHT_PATH || 'playwright'
let chromium
try {
  ;({ chromium } = require(PLAYWRIGHT))
} catch (err) {
  console.error(`Cannot load Playwright from ${PLAYWRIGHT}.`)
  console.error(String(err.message || err))
  process.exit(2)
}

const BASE = (process.env.UI_BASE_URL || '').replace(/\/$/, '')
const USER = process.env.UI_USERNAME || ''
const PASS = process.env.UI_PASSWORD || ''
const TRACK = process.env.UI_TRACK_SLUG || 'high-school'
const OUT = process.env.UI_ARTIFACT_DIR || 'ui-learning-artifacts'
if (!BASE || !USER || !PASS) {
  console.error('UI_BASE_URL, UI_USERNAME and UI_PASSWORD are required')
  process.exit(2)
}
fs.mkdirSync(OUT, { recursive: true })

const checks = []
const failures = []
const pageErrors = []
const consoleErrors = []
function check(name, ok, detail = '') {
  const row = { name, ok: Boolean(ok), detail: String(detail).slice(0, 400) }
  checks.push(row)
  if (!row.ok) failures.push(row)
  console.log(`${row.ok ? 'PASS' : 'FAIL'} ${name}${detail ? ` :: ${row.detail}` : ''}`)
}

const browser = await chromium.launch({
  headless: true,
  ...(process.env.UI_BROWSER_EXECUTABLE ? { executablePath: process.env.UI_BROWSER_EXECUTABLE } : {}),
})
const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1280, height: 900 } })
await context.addInitScript(({ username }) => {
  localStorage.setItem(`ocr_orientation_seen_v1_${username}`, '1')
}, { username: USER })
const page = await context.newPage()
page.on('pageerror', (error) => pageErrors.push(String(error)))
page.on('console', (message) => {
  if (message.type() === 'error' && !/favicon/i.test(message.text())) consoleErrors.push(message.text())
})

await page.goto(`${BASE}/login`, { waitUntil: 'networkidle', timeout: 60000 })
await page.fill('#username', USER)
await page.fill('#password', PASS)
await page.click('button[type="submit"]')
await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 60000 }).catch(() => {})
check('learning: signed in', !page.url().includes('/login'), page.url())

await page.goto(`${BASE}/exercises/${TRACK}`, { waitUntil: 'networkidle', timeout: 60000 })
await page.locator('.level-section').first().waitFor({ timeout: 20000 })
for (let attempt = 0; attempt < 12; attempt += 1) {
  const toggle = page.locator('.level-toggle[aria-expanded="false"]').first()
  if ((await toggle.count()) === 0) break
  await toggle.click()
  await page.waitForTimeout(120)
}

const token = await page.evaluate(() => localStorage.getItem('token'))
const response = await page.request.get(`${BASE}/api/exercises/tracks/${TRACK}`, {
  headers: { Authorization: `Bearer ${token}` },
})
check('learning: track API', response.ok(), `HTTP ${response.status()}`)
const track = response.ok() ? (await response.json()).track : null
const levels = track?.levels || []
const sections = page.locator('.level-section')
check('learning: level sections match API', (await sections.count()) === levels.length, `${await sections.count()} vs ${levels.length}`)

for (let index = 0; index < levels.length; index += 1) {
  const level = levels[index]
  const section = sections.nth(index)
  const hasQuizButton = (await section.locator('.level-certificate-btn', { hasText: 'Quiz' }).count()) > 0
  const hasCertButton = (await section.locator('.level-certificate-btn', { hasText: 'Certificate' }).count()) > 0
  const expectQuiz = Boolean(level.is_complete && level.has_quiz)
  const expectCert = Boolean(level.is_complete)
  check(
    `learning: level ${level.level_number} quiz visibility`,
    hasQuizButton === expectQuiz,
    `ui=${hasQuizButton} api_complete=${level.is_complete} api_has_quiz=${level.has_quiz}`,
  )
  check(
    `learning: level ${level.level_number} certificate visibility`,
    hasCertButton === expectCert,
    `ui=${hasCertButton} api_complete=${level.is_complete}`,
  )
}

await page.screenshot({ path: path.join(OUT, 'learning-smoke.png'), fullPage: true })
check('learning: no page errors', pageErrors.length === 0, pageErrors.join(' | '))
check('learning: no console errors', consoleErrors.length === 0, consoleErrors.join(' | '))

await browser.close()
const evidence = {
  schema: 1,
  runAt: new Date().toISOString(),
  script: path.basename(fileURLToPath(import.meta.url)),
  base: BASE,
  user: USER,
  track: TRACK,
  checks,
  failed: failures.length,
  pageErrors,
  consoleErrors,
  artifacts: ['learning-smoke.png'],
}
fs.writeFileSync(path.join(OUT, 'learning-smoke.json'), JSON.stringify(evidence, null, 2) + '\n')
console.log(`\n${checks.length - failures.length}/${checks.length} checks passed, ${failures.length} failed`)
process.exit(failures.length ? 1 : 0)
